from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    DefaultRouter,
)

from apps.run.views import (
    RunViewSet,
    UserViewSet,
    company_details,
)


router = DefaultRouter()
router.register('runs', RunViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('company_details/', company_details),
    path('', include(router.urls)),
]
