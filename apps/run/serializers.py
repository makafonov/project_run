from typing import (
    TYPE_CHECKING,
    Any,
)

from django.contrib.auth import (
    get_user_model,
)
from rest_framework import (
    serializers,
)
from rest_framework.fields import (
    SerializerMethodField,
)
from rest_framework.relations import (
    SlugRelatedField,
)

from apps.run import (
    types,
)
from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    AthleteInfo,
    Challenge,
    CollectibleItem,
    Position,
    Run,
    Subscribe,
)


if TYPE_CHECKING:
    from django.contrib.auth.models import (
        User as UserModel,
    )


User = get_user_model()


class AthleteSerializer(serializers.ModelSerializer['UserModel']):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(serializers.ModelSerializer[Run]):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer['UserModel']):
    type = SerializerMethodField()
    runs_finished = serializers.IntegerField()
    rating = serializers.FloatField()

    class Meta:
        model = User
        fields: tuple[str, ...] = (
            'id',
            'date_joined',
            'username',
            'last_name',
            'first_name',
            'type',
            'runs_finished',
            'rating',
        )

    def get_type(self, obj: 'UserModel') -> str:
        if obj.is_staff:
            return UserType.COACH

        return UserType.ATHLETE


class AthleteInfoSerializer(serializers.ModelSerializer[AthleteInfo]):
    class Meta:
        model = AthleteInfo
        fields = ('weight', 'goals', 'user_id')


class ChallengeSerializer(serializers.ModelSerializer[Challenge]):
    class Meta:
        model = Challenge
        fields = ('athlete', 'full_name')


class PositionSerializer(serializers.ModelSerializer[Position]):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')

    class Meta:
        model = Position
        fields = ('id', 'run', 'latitude', 'longitude', 'date_time', 'speed', 'distance')


class CollectibleItemSerializer(serializers.ModelSerializer[CollectibleItem]):
    class Meta:
        model = CollectibleItem
        fields = ('id', 'name', 'uid', 'latitude', 'longitude', 'picture', 'value')


class FileUploadSerializer(serializers.Serializer[None]):
    file = serializers.FileField()


class UserWithItemsSerializer(UserSerializer):
    items = CollectibleItemSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'items')


class AthleteWithItemsSerializer(UserWithItemsSerializer):
    coach = serializers.SerializerMethodField()

    class Meta(UserWithItemsSerializer.Meta):
        fields = (*UserWithItemsSerializer.Meta.fields, 'coach')

    def get_coach(self, obj: 'UserModel') -> int | None:
        subscription = obj.subscriptions.first()  # type: ignore[attr-defined]

        return subscription.coach_id if subscription else None


class CoachWithItemsSerializer(UserWithItemsSerializer):
    athletes: SlugRelatedField[Subscribe] = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        source='subscribers',
        slug_field='athlete_id',
    )

    class Meta(UserWithItemsSerializer.Meta):
        fields = (*UserWithItemsSerializer.Meta.fields, 'athletes')


class SubscribeToCoachSerializer(serializers.ModelSerializer[Subscribe]):
    class Meta:
        model = Subscribe
        fields = ('athlete', 'coach')

    def validate(self, attrs: Any) -> Any:  # noqa: ANN401
        if not attrs['coach'].is_staff:
            raise serializers.ValidationError({'coach': 'Можно подписываться только на тренеров.'})

        if attrs['athlete'].is_staff:
            raise serializers.ValidationError({'athlete': 'Подписываться могут только атлеты.'})

        return super().validate(attrs)


class RateCoachSerializer(serializers.Serializer[Subscribe]):
    coach = serializers.IntegerField()
    athlete = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        fields = ('coach', 'athlete', 'rating')


class _AthleteSerializer(serializers.Serializer[types.Athlete]):
    id = serializers.IntegerField(source='athlete__id')
    full_name = serializers.SerializerMethodField()
    username = serializers.CharField(source='athlete__username')

    def get_full_name(self, obj: types.Athlete) -> str:
        return f'{obj["athlete__first_name"]} {obj["athlete__last_name"]}'

    class Meta:
        model = User
        fields = ('id', 'full_name', 'username')


class ChallengeSummarySerializer(serializers.Serializer[types.Challenge]):
    name_to_display = serializers.CharField(source='full_name')
    athletes = _AthleteSerializer(many=True)

    class Meta:
        fields = ('name_to_display', 'athletes')
