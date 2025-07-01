from typing import (
    TYPE_CHECKING,
)

from django.conf import (
    settings,
)
from django.contrib.auth import (
    get_user_model,
)
from django.db.models import (
    QuerySet,
)
from django.shortcuts import (
    get_object_or_404,
)
from rest_framework import (
    status,
)
from rest_framework.decorators import (
    api_view,
)
from rest_framework.filters import (
    SearchFilter,
)
from rest_framework.response import (
    Response,
)
from rest_framework.views import (
    APIView,
)
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    Run,
    RunStatus,
)
from apps.run.serializers import (
    RunSerializer,
    UserSerializer,
)


if TYPE_CHECKING:
    from django.contrib.auth.models import (
        User as UserModel,
    )
    from rest_framework.request import (
        Request,
    )


User = get_user_model()


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
    serializer_class = RunSerializer


class UserViewSet(ReadOnlyModelViewSet['UserModel']):
    queryset = User.objects.filter(is_superuser=False).all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('first_name', 'last_name')

    def get_queryset(self) -> QuerySet['UserModel']:
        qs = self.queryset
        type_ = self.request.query_params.get('type', None)
        if type_:
            is_staff = type_ == UserType.COACH
            qs = qs.filter(is_staff=is_staff)

        return qs


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

        serializer = RunSerializer(run)

        return Response(serializer.data)


class StopRunAPIView(APIView):
    def post(self, _: 'Request', run_id: int) -> Response:
        run = get_object_or_404(Run, id=run_id)
        if run.status != RunStatus.IN_PROGRESS:
            return Response(
                {
                    'detail': 'Забег не запущен.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = RunStatus.FINISHED
        run.save(update_fields=['status'])

        serializer = RunSerializer(run)

        return Response(serializer.data)
