from typing import (
    TYPE_CHECKING,
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

from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    AthleteInfo,
    Challenge,
    CollectibleItem,
    Position,
    Run,
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

    class Meta:
        model = User
        fields: tuple[str, ...] = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

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
        fields = ('id', 'run', 'latitude', 'longitude', 'date_time')


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
