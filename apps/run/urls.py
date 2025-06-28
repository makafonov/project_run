from django.urls import (
    path,
)

from apps.run.views import (
    company_details,
)


urlpatterns = [
    path('company_details/', company_details),
]
