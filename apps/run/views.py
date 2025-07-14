import itertools
from operator import (
    itemgetter,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from django.conf import (
    settings,
)
from django.contrib.auth import (
    get_user_model,
)
from django.db.models import (
    Avg,
    Count,
    Max,
    Min,
    Q,
    QuerySet,
    Sum,
)
from django.shortcuts import (
    get_object_or_404,
)
from django_filters.rest_framework import (
    DjangoFilterBackend,
)
from geopy.distance import (  # type: ignore[import-untyped]
    distance,
)
from rest_framework import (
    generics,
    mixins,
    status,
)
from rest_framework.decorators import (
    api_view,
)
from rest_framework.exceptions import (
    ValidationError,
)
from rest_framework.filters import (
    OrderingFilter,
    SearchFilter,
)
from rest_framework.pagination import (
    PageNumberPagination,
)
from rest_framework.parsers import (
    MultiPartParser,
)
from rest_framework.response import (
    Response,
)
from rest_framework.views import (
    APIView,
)
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from apps.run import (
    serializers,
)
from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    AthleteInfo,
    Challenge,
    ChallengeType,
    CollectibleItem,
    Position,
    Run,
    RunStatus,
    Subscribe,
)
from apps.run.services import (
    CollectibleItemService,
)


if TYPE_CHECKING:
    from django.contrib.auth.models import (
        User as UserModel,
    )
    from django_stubs_ext import (
        WithAnnotations,
    )
    from rest_framework.request import (
        Request,
    )
    from rest_framework.serializers import (
        BaseSerializer,
    )

    from apps.run.types import (
        RunWithTime,
    )


User = get_user_model()

_CHALLENGE_RUN_COUNT = 10
_CHALLENGE_DISTANCE = 50
_CHALLENGE_SPEED_DISTANCE = 2
_CHALLENGE_SPEED_TIME = 600
_MIN_POSITION_COUNT = 2


class Pagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


@api_view(['GET'])
def company_details(_: 'Request') -> Response:
    return Response(
        {
            'company_name': settings.COMPANY_NAME,
            'slogan': settings.SLOGAN,
            'contacts': settings.CONTACTS,
        }
    )


class RunViewSet(ModelViewSet[Run]):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = serializers.RunSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    pagination_class = Pagination
    filterset_fields = ('status', 'athlete')
    ordering_fields = ('created_at',)


class UserViewSet(ReadOnlyModelViewSet['UserModel']):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = serializers.UserSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    pagination_class = Pagination
    search_fields = ('first_name', 'last_name')
    ordering_fields = ('date_joined',)

    def get_queryset(self) -> QuerySet['UserModel']:
        qs = self.queryset
        type_ = self.request.query_params.get('type', None)
        if type_:
            is_staff = type_ == UserType.COACH
            qs = qs.filter(is_staff=is_staff)

        return qs.annotate(
            runs_finished=Count('runs', filter=Q(runs__status=RunStatus.FINISHED)),
            rating=Avg('subscribers__rating'),
        )

    def get_serializer_class(self) -> type['BaseSerializer[Any]']:
        if self.action == 'retrieve':
            user = self.get_object()  # additional sql query
            if user.is_staff:
                return serializers.CoachWithItemsSerializer

            return serializers.AthleteWithItemsSerializer

        return super().get_serializer_class()


class StartRunAPIView(APIView):
    def post(self, _: 'Request', run_id: int) -> Response:
        run = get_object_or_404(Run, id=run_id)
        if run.status != RunStatus.INIT:
            return Response(
                {
                    'detail': 'Забег уже стартовал или закончен.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = RunStatus.IN_PROGRESS
        run.save(update_fields=['status'])

        serializer = serializers.RunSerializer(run)

        return Response(serializer.data)


class StopRunAPIView(APIView):
    def post(self, _: 'Request', run_id: int) -> Response:
        run: WithAnnotations[Run, RunWithTime] = get_object_or_404(
            Run.objects.select_related('athlete').annotate(
                time=Max('positions__date_time') - Min('positions__date_time'),
            ),
            id=run_id,
        )
        if run.status != RunStatus.IN_PROGRESS:
            return Response(
                {
                    'detail': 'Забег не запущен.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = RunStatus.FINISHED
        run.distance = self._get_distance(positions=run.positions.all())

        speed = 0.0
        count = 0
        for position in run.positions.all():
            if position.speed is not None:
                count += 1
                speed += position.speed
        if count:
            run.speed = round(speed / count, 2)

        fields = ['status', 'distance', 'speed']
        if run.time:
            run.run_time_seconds = run.time.seconds
            fields.append('run_time_seconds')

        run.save(update_fields=fields)

        if self._is_run_count_challenge_completed(run):
            Challenge.objects.create(athlete=run.athlete, full_name=ChallengeType.COUNT)
        if self._is_distance_challenge_completed(run):
            Challenge.objects.create(athlete=run.athlete, full_name=ChallengeType.DISTANCE)
        if self._is_speed_challenge_completed(run):
            Challenge.objects.create(athlete=run.athlete, full_name=ChallengeType.SPEED)

        serializer = serializers.RunSerializer(run)

        return Response(serializer.data)

    def _is_speed_challenge_completed(self, run: Run) -> bool:
        if not (run.run_time_seconds and run.distance):
            return False

        return run.distance >= _CHALLENGE_SPEED_DISTANCE and run.run_time_seconds <= _CHALLENGE_SPEED_TIME

    def _is_run_count_challenge_completed(self, run: Run) -> bool:
        finished_run_count = Run.objects.filter(
            athlete=run.athlete,
            status=RunStatus.FINISHED,
        ).count()

        return finished_run_count % _CHALLENGE_RUN_COUNT == 0

    def _is_distance_challenge_completed(self, run: Run) -> bool:
        if Challenge.objects.filter(
            athlete=run.athlete,
            full_name=ChallengeType.DISTANCE,
        ).exists():
            return False

        total_distance = (
            Run.objects.filter(
                athlete=run.athlete,
                status=RunStatus.FINISHED,
            ).aggregate(total_distance=Sum('distance'))['total_distance']
            or 0
        )

        return total_distance >= _CHALLENGE_DISTANCE

    def _get_distance(self, positions: QuerySet[Position]) -> float:
        result = 0
        if len(positions) < _MIN_POSITION_COUNT:
            return result

        for index in range(1, len(positions)):
            prev = positions[index - 1]
            current = positions[index]
            result += distance((current.latitude, current.longitude), (prev.latitude, prev.longitude)).km

        return result


class AtheleteInfoViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet[AthleteInfo],
):
    queryset = AthleteInfo.objects.all()
    serializer_class = serializers.AthleteInfoSerializer
    http_method_names = ('get', 'put')
    lookup_field = 'user_id'

    def get_object(self) -> AthleteInfo:
        user = get_object_or_404(User, id=self.kwargs[self.lookup_field])
        athlete_info, _ = AthleteInfo.objects.get_or_create(user=user)

        return athlete_info

    def update(self, request: 'Request', *args: Any, **kwargs: Any) -> Response:  # noqa: ANN401
        respose = super().update(request, *args, **kwargs)
        respose.status_code = status.HTTP_201_CREATED

        return respose


class ChallengeViewSet(mixins.ListModelMixin, GenericViewSet[Challenge]):
    queryset = Challenge.objects.all()
    serializer_class = serializers.ChallengeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('athlete',)


class PositionViewSet(ModelViewSet[Position]):
    queryset = Position.objects.all()
    serializer_class = serializers.PositionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('run',)

    def perform_create(self, serializer: 'BaseSerializer[Position]') -> None:
        if serializer.validated_data['run'].status != RunStatus.IN_PROGRESS:
            raise ValidationError({'status': ['Забег не запущен.']})

        items = CollectibleItemService.get_neighbor_items(
            serializer.validated_data['latitude'], serializer.validated_data['longitude']
        )
        for item in items:
            serializer.validated_data['run'].athlete.items.add(item)

        prev_position = Position.objects.filter(run=serializer.validated_data['run']).order_by('-date_time').first()
        if prev_position:
            current_distance = distance(
                (serializer.validated_data['latitude'], serializer.validated_data['longitude']),
                (prev_position.latitude, prev_position.longitude),
            ).m
            speed = round(
                current_distance / (serializer.validated_data['date_time'] - prev_position.date_time).seconds, 2
            )
            serializer.validated_data['speed'] = speed
            serializer.validated_data['distance'] = current_distance / 1000 + prev_position.distance
        else:
            serializer.validated_data['speed'] = 0
            serializer.validated_data['distance'] = 0

        super().perform_create(serializer)


class CollectibleItemViewSet(ReadOnlyModelViewSet[CollectibleItem]):
    queryset = CollectibleItem.objects.all()
    serializer_class = serializers.CollectibleItemSerializer


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request: 'Request') -> Response:
        serializer = serializers.FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            errors = CollectibleItemService.save_collectible_items(serializer.validated_data['file'])

            return Response(errors, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribeToCoachAPIView(generics.CreateAPIView[Subscribe]):
    serializer_class = serializers.SubscribeToCoachSerializer

    def get_serializer(self, *args: Any, **kwargs: Any) -> 'BaseSerializer[Subscribe]':  # noqa: ANN401
        kwargs['data']['coach'] = self.kwargs['coach_id']

        return super().get_serializer(*args, **kwargs)

    def create(self, request: 'Request', *args: Any, **kwargs: Any) -> Response:  # noqa: ANN401
        coach_id = self.kwargs['coach_id']
        get_object_or_404(User, id=coach_id)

        if Subscribe.objects.filter(athlete_id=request.data['athlete']).exists():
            return Response(
                {
                    'detail': 'Подписку можно оформить только один раз.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK

        return response


class ChallengeSummaryAPIView(APIView):
    def get(self, _: 'Request') -> Response:
        challenges = (
            Challenge.objects.select_related('athlete')
            .order_by('full_name')
            .values(
                'full_name',
                'athlete__id',
                'athlete__first_name',
                'athlete__last_name',
                'athlete__username',
            )
        )

        grouped_challenges = []
        for key, group in itertools.groupby(challenges, key=itemgetter('full_name')):
            grouped_challenges.append(
                {
                    'full_name': key,
                    'athletes': list(group),
                }
            )

        return Response(serializers.ChallengeSummarySerializer(grouped_challenges, many=True).data)  # type: ignore[arg-type]


class RateCoachAPIView(APIView):
    def post(self, request: 'Request', coach_id: int) -> Response:
        coach = get_object_or_404(User, id=coach_id)
        try:
            athlete = User.objects.get(id=request.data['athlete'])
        except User.DoesNotExist:
            return Response(
                {
                    'detail': 'Атлет не найден.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subscibe = Subscribe.objects.get(athlete=athlete, coach=coach)
        except Subscribe.DoesNotExist:
            return Response(
                {
                    'detail': 'Атлет должен быть подписан на тренера.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serizalizer = serializers.RateCoachSerializer(data=request.data | {'coach': coach_id})
        serizalizer.is_valid(raise_exception=True)

        subscibe.rating = serizalizer.validated_data['rating']
        subscibe.save(update_fields=['rating'])

        return Response(serizalizer.validated_data)


class AnalyticsForCoachAPIView(APIView):
    def get(self, _: 'Request', coach_id: int) -> Response:
        get_object_or_404(User, id=coach_id)

        longest_run = (
            Run.objects.filter(athlete__subscriptions__coach=coach_id)
            .order_by('-distance')
            .values('athlete_id', 'distance')
            .first()
        )

        total_runs = (
            User.objects.filter(subscriptions__coach=coach_id)
            .annotate(total_runs=Sum('runs__distance', filter=Q(runs__status=RunStatus.FINISHED)))
            .order_by('-total_runs')
            .values('id', 'total_runs')
            .first()
        )

        avg_speed = (
            User.objects.filter(subscriptions__coach=coach_id)
            .annotate(avg_speed=Avg('runs__speed', filter=Q(runs__status=RunStatus.FINISHED)))
            .order_by('-avg_speed')
            .values('id', 'avg_speed')
            .first()
        )

        return Response(
            {
                'longest_run_user': longest_run['athlete_id'] if longest_run else None,
                'longest_run_value': longest_run['distance'] if longest_run else None,
                'total_run_user': total_runs['id'] if total_runs else None,
                'total_run_value': total_runs['total_runs'] if total_runs else None,
                'speed_avg_user': avg_speed['id'] if avg_speed else None,
                'speed_avg_value': avg_speed['avg_speed'] if avg_speed else None,
            }
        )
