from audit.models import AuditLog
from branding.models import BrandProject
from django.utils import timezone
from datetime import timedelta

class BrandActivityService:
    @staticmethod
    def get_recent_activity(user, limit=10):
        logs = AuditLog.objects.filter(user=user).order_by('-timestamp')[:limit]
        activities = []
        for log in logs:
            icon = '📥'
            if log.action == 'AI_GENERATE': icon = '🎨'
            if log.action == 'CREATE': icon = '🚀'
            if log.action == 'UPDATE': icon = '✍️'
            
            diff = timezone.now() - log.timestamp
            if diff.days == 0:
                time_str = f"Today, {log.timestamp.strftime('%I:%M %p')}"
            elif diff.days == 1:
                time_str = f"Yesterday, {log.timestamp.strftime('%I:%M %p')}"
            else:
                time_str = f"{diff.days} days ago"
                
            activities.append({
                'time': time_str,
                'text': f"{log.get_action_display()} - {log.target}",
                'icon': icon
            })
        return activities

    @staticmethod
    def get_generation_stats(project: BrandProject):
        creative_types = ['SOCIAL_GRAPHIC', 'AD_CREATIVE', 'POSTER', 'BANNER', 'BUSINESS_CARD', 'LETTERHEAD', 'EMAIL_HEADER']
        return {
            'logos_generated': project.assets.filter(asset_type='LOGO').count(),
            'creative_assets': project.assets.filter(asset_type__in=creative_types).count(),
            'marketing_content': project.marketing_contents.count() + project.assets.filter(asset_type='MARKETING_COPY').count(),
            'social_posts': project.social_posts.count() + project.assets.filter(asset_type='SOCIAL_POST').count(),
            'campaigns': project.campaigns.count() + project.assets.filter(asset_type='CAMPAIGN').count()
        }
