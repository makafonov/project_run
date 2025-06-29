from rest_framework.serializers import (
    ModelSerializer,
)

from apps.run.models import (
    Run,
)


class RunSerializer(ModelSerializer[Run]):
    class Meta:
        model = Run
        fields = '__all__'
