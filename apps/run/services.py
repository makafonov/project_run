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

        items = []
        errors = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            item = {
                'name': row[0],
                'uid': row[1],
                'value': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'picture': row[5],
            }
            serializer = CollectibleItemSerializer(data=item)
            if serializer.is_valid():
                items.append(CollectibleItem(**serializer.validated_data))
            else:
                errors.append(row)

        if items:
            CollectibleItem.objects.bulk_create(items)

        return errors
