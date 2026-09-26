from rest_framework import serializers
from branding.models import BrandProject
from brand_assets.models import BrandAsset

class BrandAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandAsset
        fields = ['id', 'project', 'asset_type', 'content', 'raw_prompt', 'is_favorite', 'created_at']
        read_only_fields = ['id', 'created_at']

class BrandProjectSerializer(serializers.ModelSerializer):
    assets = BrandAssetSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = BrandProject
        fields = [
            'id', 'user', 'business_name', 'business_idea', 'industry', 
            'target_audience', 'brand_personality', 'preferred_style', 
            'assets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

from feedback.models import UserFeedback, FeatureRequest
from monitoring.models import APIMetric

class UserFeedbackSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserFeedback
        fields = ['id', 'user', 'rating', 'comments', 'source_page', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class FeatureRequestSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = FeatureRequest
        fields = ['id', 'user', 'title', 'description', 'status', 'upvotes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'upvotes', 'created_at', 'updated_at']

class APIMetricSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = APIMetric
        fields = ['id', 'endpoint', 'method', 'user', 'response_time_ms', 'status_code', 'ip_address', 'timestamp']
        read_only_fields = ['id', 'timestamp']
