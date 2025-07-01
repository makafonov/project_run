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
    ModelSerializer,
)

from apps.run.enums import (
    UserType,
)
from apps.run.models import (
    Run,
)


if TYPE_CHECKING:
    from django.contrib.auth.models import (
        User as UserModel,
    )


User = get_user_model()


class RunSerializer(ModelSerializer[Run]):
    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(ModelSerializer['UserModel']):
    type = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'date_joined', 'username', 'last_name', 'first_name', 'type')

    def get_type(self, obj: 'UserModel') -> str:
        if obj.is_staff:
            return UserType.COACH

        return UserType.ATHLETE
