import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from branding.models import BrandProject
from brand_assets.models import BrandAsset

@login_required
def home_view(request):
    projects = BrandProject.objects.filter(user=request.user).prefetch_related('assets').order_by('-updated_at')
    recent_project = projects.first()
    
    # Calculate assets count and completion percentage
    assets_count = 0
    completion_pct = 0
    if recent_project:
        from analytics.services.completion import BrandCompletionService
        all_assets = list(recent_project.assets.all())
        assets_count = len(all_assets)
        completion_pct = BrandCompletionService.calculate_completion(recent_project)
    
    # AI Recommendations based on real generated assets
    colors = ['#17344F', '#C68B3C', '#8FA99B', '#FBF8F2']
    typography = 'Playfair Display + Inter'
    if recent_project:
        color_asset = next((a for a in all_assets if a.asset_type == 'COLOR'), None)
        if color_asset and isinstance(color_asset.content_json, dict):
            colors = [
                color_asset.content_json.get('primary', colors[0]),
                color_asset.content_json.get('secondary', colors[1]),
                color_asset.content_json.get('background', colors[2]),
                color_asset.content_json.get('accent', colors[3])
            ]
        font_asset = next((a for a in all_assets if a.asset_type == 'TYPOGRAPHY'), None)
        if font_asset and isinstance(font_asset.content_json, dict):
            typography = font_asset.content_json.get('primary', typography)

    # Determine progress states for the stepper
    has_brand_identity = False
    has_logo = False
    has_creative = False
    has_marketing = False
    
    if recent_project:
        has_brand_identity = any(a.asset_type in ['NAME', 'TAGLINE', 'STORY', 'PERSONALITY', 'VOICE'] for a in all_assets)
        has_logo = any(a.asset_type == 'LOGO' for a in all_assets)
        has_creative = any(a.asset_type in ['POSTER', 'BANNER', 'AD_CREATIVE', 'SOCIAL_GRAPHIC'] for a in all_assets)
        has_marketing = any(a.asset_type in ['MARKETING_COPY', 'SOCIAL_POST', 'CAMPAIGN'] for a in all_assets)
        next_action = 'Launch Campaign Studio' if has_logo else 'Select Primary Logo'
    else:
        next_action = 'Create Your First Brand'

    ai_recommendations = {
        'suggested_colors': colors,
        'suggested_typography': typography,
        'next_action': next_action,
        'marketing_tip': 'Focus marketing copy on your defined target audience.'
    }

    # Timeline Activities from AuditLog
    from audit.models import AuditLog
    from django.utils import timezone
    activities = []
    logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:4]
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
        
    # Chart Data (Last 7 days)
    import datetime
    today = timezone.now().date()
    dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%b %d') for d in dates]
    
    assets_data = []
    ai_data = []
    projects_data = []
    
    for d in dates:
        assets_data.append(BrandAsset.objects.filter(project__user=request.user, created_at__date=d).count())
        ai_data.append(AuditLog.objects.filter(user=request.user, action='AI_GENERATE', timestamp__date=d).count())
        projects_data.append(BrandProject.objects.filter(user=request.user, created_at__date=d).count())

    chart_data = {
        'labels': chart_labels,
        'assets': assets_data,
        'generations': ai_data,
        'projects': projects_data
    }

    context = {
        'projects': projects,
        'recent_project': recent_project,
        'project': recent_project,
        'assets_count': assets_count,
        'completion_pct': completion_pct,
        'ai_recommendations': ai_recommendations,
        'activities': activities,
        'user_name': request.user.first_name or (request.user.username.split('@')[0].capitalize() if '@' in (request.user.username or '') else request.user.username) or 'User',
        'has_brand_identity': has_brand_identity,
        'has_logo': has_logo,
        'has_creative': has_creative,
        'has_marketing': has_marketing,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'dashboard/user_home.html', context)


