from typing import (
    TYPE_CHECKING,
    Any,
)

import openpyxl

from apps.run.models import (
    CollectibleItem,
)
from apps.run.serializers import (
    CollectibleItemSerializer,
)


if TYPE_CHECKING:
    from django.core.files.uploadedfile import (
        InMemoryUploadedFile,
    )


class CollectibleItemService:
    @staticmethod
    def save_collectible_items(file: 'InMemoryUploadedFile') -> list[tuple[Any, ...]]:
        workbook = openpyxl.load_workbook(file, read_only=True)
        sheet = workbook.active

        if not sheet:
            return []

        headers = [header.value.lower() for header in sheet[1] if isinstance(header.value, str)]
        index = headers.index('url')
        headers[index] = 'picture'

        items = []
        errors = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            item = dict(zip(headers, row, strict=True))
            serializer = CollectibleItemSerializer(data=item)
            if serializer.is_valid():
                items.append(serializer.validated_data)
            else:
                errors.append(row)

        if items:
            CollectibleItem.objects.bulk_create(
                [CollectibleItem(**item) for item in items],
                ignore_conflicts=True,
            )

        return errors
