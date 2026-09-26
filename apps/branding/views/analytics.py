from collaboration.shortcuts import get_project_for_user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from branding.models import BrandProject
from brand_assets.models import BrandAsset
from ai_services.services import AIService
from ai_services.prompts import PromptLibrary
from activitylogs.models import ActivityLog
import json
import os
import requests


@login_required
def project_analytics(request, pk):
    from analytics.services.completion import BrandCompletionService
    from analytics.services.readiness import CampaignReadinessService
    from analytics.services.activity import BrandActivityService
    from analytics.models import BrandAudit
    
    project = get_project_for_user(pk, request.user)
    
    # Deterministic Metrics
    foundation_score = BrandCompletionService.calculate_foundation(project)
    activation_score = BrandCompletionService.calculate_activation(project)
    readiness_data = CampaignReadinessService.evaluate(project)
    activity_stats = BrandActivityService.get_generation_stats(project)
    
    # Latest Audit
    latest_audit = BrandAudit.objects.filter(project=project, user=request.user).order_by('-created_at').first()
    
    color_asset = project.assets.filter(asset_type='COLOR').first()
    colors = {'primary': '#17344F', 'secondary': '#C68B3C', 'background': '#FBF8F2', 'accent': '#8FA99B'}
    if color_asset and isinstance(color_asset.content_json, dict):
        colors.update(color_asset.content_json)
        
    return render(request, 'branding/analytics.html', {
        'project': project, 
        'colors': colors,
        'foundation_score': foundation_score,
        'activation_score': activation_score,
        'readiness_data': readiness_data,
        'activity_stats': activity_stats,
        'latest_audit': latest_audit
    })


@login_required
def run_brand_audit(request, pk):
    import json
    from django.http import JsonResponse
    from analytics.services.audit import BrandAuditService
    
    if request.method == 'POST':
        project = get_project_for_user(pk, request.user)
        audit = BrandAuditService.run_full_audit(project, request.user)
        
        if audit:
            ActivityLog.objects.create(project=project, user=request.user, action=f"Run a new **Brand Audit** (Score: {audit.overall_score}%).", description="")
            return JsonResponse({
                'success': True,
                'audit': {
                    'consistency_score': audit.consistency_score,
                    'summary': audit.summary,
                    'strengths': audit.strengths,
                    'weaknesses': audit.weaknesses,
                    'opportunities': audit.opportunities
                }
            })
        return JsonResponse({'success': False, 'error': 'Audit generation failed.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


