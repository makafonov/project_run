from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    DefaultRouter,
)

from apps.run.views import (
    AtheleteInfoViewSet,
    ChallengeViewSet,
    PositionViewSet,
    RunViewSet,
    StartRunAPIView,
    StopRunAPIView,
    UserViewSet,
    company_details,
)


router = DefaultRouter()
router.register('runs', RunViewSet)
router.register('users', UserViewSet)
router.register('athlete_info', AtheleteInfoViewSet)
router.register('challenges', ChallengeViewSet)
router.register('positions', PositionViewSet)


urlpatterns = [
    path('company_details/', company_details),
    path('runs/<int:run_id>/start/', StartRunAPIView.as_view()),
    path('runs/<int:run_id>/stop/', StopRunAPIView.as_view()),
    path('', include(router.urls)),
]
