from typing import (
    TYPE_CHECKING,
)

from django.conf import (
    settings,
)
from rest_framework.decorators import (
    api_view,
)
from rest_framework.response import (
    Response,
)
from rest_framework.viewsets import (
    ModelViewSet,
)

from apps.run.models import (
    Run,
)
from apps.run.serializers import (
    RunSerializer,
)


if TYPE_CHECKING:
    from rest_framework.request import (
        Request,
    )


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
    queryset = Run.objects.all()
    serializer_class = RunSerializer
