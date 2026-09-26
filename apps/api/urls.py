from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import BrandProjectViewSet, BrandAssetViewSet, UserFeedbackViewSet, FeatureRequestViewSet, APIMetricViewSet

router = DefaultRouter()
router.register(r'projects', BrandProjectViewSet, basename='project')
router.register(r'assets', BrandAssetViewSet, basename='asset')
router.register(r'feedback', UserFeedbackViewSet, basename='feedback')
router.register(r'features', FeatureRequestViewSet, basename='feature')
router.register(r'metrics', APIMetricViewSet, basename='metric')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', obtain_auth_token, name='api_token'),
]
