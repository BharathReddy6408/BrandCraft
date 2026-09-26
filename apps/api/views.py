from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from branding.models import BrandProject
from brand_assets.models import BrandAsset
from .serializers import BrandProjectSerializer, BrandAssetSerializer

class BrandProjectViewSet(viewsets.ModelViewSet):
    serializer_class = BrandProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view/edit their own brand projects
        return BrandProject.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BrandAssetViewSet(viewsets.ModelViewSet):
    serializer_class = BrandAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view/edit assets belonging to their own projects
        return BrandAsset.objects.filter(project__user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        asset = self.get_object()
        asset.is_favorite = not asset.is_favorite
        asset.save()
        return Response(
            {'status': 'favorite toggled', 'is_favorite': asset.is_favorite},
            status=status.HTTP_200_OK
        )

from feedback.models import UserFeedback, FeatureRequest
from monitoring.models import APIMetric
from .serializers import UserFeedbackSerializer, FeatureRequestSerializer, APIMetricSerializer

class UserFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = UserFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view/edit their own feedback
        return UserFeedback.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FeatureRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FeatureRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FeatureRequest.objects.all().order_by('-upvotes', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        req = self.get_object()
        req.upvotes += 1
        req.save()
        return Response({'status': 'upvoted', 'upvotes': req.upvotes}, status=status.HTTP_200_OK)

class APIMetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = APIMetricSerializer
    permission_classes = [permissions.IsAdminUser] # Admin-only metrics view

    def get_queryset(self):
        return APIMetric.objects.all().order_by('-timestamp')

