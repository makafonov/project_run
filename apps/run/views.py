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


if TYPE_CHECKING:
    from rest_framework.request import (
        Request,
    )


@api_view(['GET'])
def company_details(_: 'Request') -> Response:
    return Response({
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS,
    })
