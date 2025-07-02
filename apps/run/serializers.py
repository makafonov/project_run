from typing import (
    TYPE_CHECKING,
)

from django.contrib.auth import (
    get_user_model,
)
from rest_framework.fields import (
    SerializerMethodField,
)
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
)

from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    AthleteInfo,
    Challenge,
    Run,
)


if TYPE_CHECKING:
    from django.contrib.auth.models import (
        User as UserModel,
    )


User = get_user_model()


class AthleteSerializer(ModelSerializer['UserModel']):
    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class RunSerializer(ModelSerializer[Run]):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(ModelSerializer['UserModel']):
    type = SerializerMethodField()
    runs_finished = IntegerField()

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished')

    def get_type(self, obj: 'UserModel') -> str:
        if obj.is_staff:
            return UserType.COACH

        return UserType.ATHLETE


class AthleteInfoSerializer(ModelSerializer[AthleteInfo]):
    class Meta:
        model = AthleteInfo
        fields = ('weight', 'goals', 'user_id')


class ChallengeSerializer(ModelSerializer[Challenge]):
    class Meta:
        model = Challenge
        fields = ('athlete', 'full_name')
