from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    DefaultRouter,
)

from apps.run import (
    views,
)


router = DefaultRouter()
router.register('runs', views.RunViewSet)
router.register('users', views.UserViewSet)
router.register('athlete_info', views.AtheleteInfoViewSet)
router.register('challenges', views.ChallengeViewSet)
router.register('positions', views.PositionViewSet)
router.register('collectible_item', views.CollectibleItemViewSet)


urlpatterns = [
    path('company_details/', views.company_details),
    path('runs/<int:run_id>/start/', views.StartRunAPIView.as_view(), name='start-run'),
    path('runs/<int:run_id>/stop/', views.StopRunAPIView.as_view(), name='stop-run'),
    path('upload_file/', views.FileUploadView.as_view()),
    path('subscribe_to_coach/<int:coach_id>/', views.SubscribeToCoachAPIView.as_view()),
    path('', include(router.urls)),
]
