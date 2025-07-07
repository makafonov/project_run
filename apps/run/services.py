from typing import (
    TYPE_CHECKING,
    Any,
)

import openpyxl
from django.db import (
    models,
)
from geopy.distance import (  # type: ignore[import-untyped]
    distance,
)

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


_NEAREST_DISTANCE = 100


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

    @staticmethod
    def get_neighbor_items(latitude: float, longitude: float) -> list[CollectibleItem]:
        items = CollectibleItem.objects.annotate(
            distance=(
                models.ExpressionWrapper(pow(models.F('latitude') - latitude, 2), output_field=models.FloatField())
                + models.ExpressionWrapper(pow(models.F('longitude') - longitude, 2), output_field=models.FloatField())
            ),
        ).filter(
            distance__lte=pow(0.15 / 9, 2),  # в пределах 150 метров
        )

        return [
            item
            for item in items
            if distance((latitude, longitude), (item.latitude, item.longitude)).m <= _NEAREST_DISTANCE
        ]
