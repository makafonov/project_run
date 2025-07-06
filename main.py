import django
import openpyxl


django.setup()
from apps.run.serializers import (
    CollectibleItemSerializer,
)


def read():
    wb = openpyxl.load_workbook('/Users/amnesia/Downloads/upload_example.xlsx', read_only=True)
    sheet = wb.active

    items = []
    headers = [header.value.lower() for header in sheet[1]]
    print(f'{headers=}')
    index = headers.index('url')
    headers[index] = 'picture'

    errors = []
    # return
    for row in sheet.iter_rows(min_row=2, values_only=True):
        print(f'{row=}')

        item = dict(zip(headers, row))
        print(f'{item=}')

        # Serialize the item using CollectibleItemSerializer
        serializer = CollectibleItemSerializer(data=item)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            print(f'{validated_data=}')
            items.append(validated_data)
        else:
            print(f'Validation errors: {serializer.errors}')
            # raise ValueError(f'Invalid data: {serializer.errors}')
            errors.append(row)

        print('\n\n\n\n')

    return items, errors


items, errors = read()
print(f'{items=}')
print(f'{errors=}')
