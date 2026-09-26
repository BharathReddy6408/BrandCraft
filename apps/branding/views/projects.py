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
def create_project_wizard(request):
    class AICoordinator:
        @staticmethod
        def launch_brand_intelligence(project, context):
            prompt = f"Perform brand intelligence for {project.business_name}. Context: {context}. Return JSON with 'strategy' (object with 'mission', 'vision', 'usp', 'brand_voice', 'values', 'keywords' - as string), 'slogans' (JSON array of strings), 'identity' (string)."
            return AIService.generate_structured(prompt) or {}
            
    from ai_services.context import BrandContextService
    
    if request.method == 'POST':
        # 1. Validation & Save BrandProject
        business_name = request.POST.get('business_name', '').strip()
        business_idea = request.POST.get('business_idea', '').strip()
        industry = request.POST.get('industry', '').strip()
        target_audience = request.POST.get('target_audience', '').strip()
        brand_personality = request.POST.get('brand_personality', '').strip()
        preferred_colors = request.POST.get('preferred_colors', '').strip()
        preferred_style = request.POST.get('preferred_style', '').strip()
        
        # Determine actual hex colors based on wizard string
        primary, secondary, accent, bg = '#17344F', '#C68B3C', '#8FA99B', '#FBF8F2' # Defaults
        if preferred_colors == 'Vibrant & Energetic':
            primary, secondary, accent, bg = '#F06292', '#FF9800', '#FFC107', '#7E57C2'
        elif preferred_colors == 'Calm & Trustworthy':
            primary, secondary, accent, bg = '#1976D2', '#42A5F5', '#90CAF9', '#E3F2FD'
        elif preferred_colors == 'Natural & Organic':
            primary, secondary, accent, bg = '#2E7D32', '#66BB6A', '#A5D6A7', '#8D6E63'
        elif preferred_colors == 'Warm & Friendly':
            primary, secondary, accent, bg = '#FF9800', '#FFB74D', '#FFE0B2', '#D7CCC8'
        elif preferred_colors == 'Elegant & Sophisticated':
            primary, secondary, accent, bg = '#8E24AA', '#BA68C8', '#E1BEE7', '#A1887F'
        elif preferred_colors == 'Minimal & Modern':
            primary, secondary, accent, bg = '#616161', '#9E9E9E', '#E0E0E0', '#F5F5F5'

        project = BrandProject.objects.create(
            user=request.user,
            business_name=business_name,
            business_idea=business_idea,
            industry=industry,
            target_audience=target_audience,
            brand_personality=brand_personality,
            preferred_style=preferred_style,
            preferred_colors=preferred_colors,
            primary_color=primary,
            secondary_color=secondary,
            accent_color=accent,
            background_color=bg,
            generation_status='GENERATING'
        )
        
        # 2. Build Context
        context = BrandContextService.build_context(project)
        
        # 3. AI Coordinator - Initial Brand Intelligence
        try:
            results = AICoordinator.launch_brand_intelligence(project, context)
            
            if 'strategy' in results:
                strat = results['strategy']
                project.brand_mission = strat.get('mission')
                project.brand_vision = strat.get('vision')
                project.usp = strat.get('usp')
                project.brand_voice = strat.get('brand_voice')
                project.brand_values = strat.get('values')
                project.keywords = strat.get('keywords')
                
            project.generation_status = 'COMPLETED'
            project.save()
            
            # Save Slogans to BrandAsset
            if 'slogans' in results:
                BrandAsset.objects.create(
                    project=project,
                    asset_type='SLOGAN',
                    content_json=results['slogans']
                )
                
            # Save Colors and Typography based on identity result or defaults
            BrandAsset.objects.create(
                project=project,
                asset_type='COLOR',
                content_json={'primary': primary, 'secondary': secondary, 'accent': accent, 'background': bg}
            )
            
            # We can also store identity recommendations if we want
            if 'identity' in results:
                BrandAsset.objects.create(
                    project=project,
                    asset_type='PERSONALITY',
                    content_json=results['identity']
                )
                
        except Exception as e:
            project.generation_status = 'FAILED'
            project.save()
            messages.error(request, "Brand intelligence generation failed. Please try again.")

        return redirect('branding:project_detail', pk=project.pk)
        
    return render(request, 'branding/wizard.html')


@login_required
def delete_project(request, pk):
    project = get_project_for_user(pk, request.user)
    if request.method == 'POST':
        project_name = project.business_name
        project.delete()
        messages.success(request, f"Project '{project_name}' was successfully deleted.")
        return redirect('dashboard:home')
    return redirect('branding:settings', pk=pk)


@login_required
def project_detail(request, pk):
    from branding.services import BrandCompletionService
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        if 'selected_variation' in request.POST:
            variation = request.POST.get('selected_variation')
            BrandAsset.objects.get_or_create(
                project=project,
                asset_type='PERSONALITY',
                defaults={'content_json': {'selected_variation': variation, 'voice': 'Confident, Editorial, Professional'}}
            )
            BrandAsset.objects.get_or_create(
                project=project,
                asset_type='COLOR',
                defaults={'content_json': {'primary': '#17344F', 'secondary': '#C68B3C', 'background': '#FBF8F2'}}
            )
            messages.success(request, f"Brand Variation {variation} has been successfully locked and activated!")
            ActivityLog.objects.create(project=project, user=request.user, action=f"Selected and activated **{variation}** color palette.", description="")
            return redirect('branding:project_detail', pk=pk)
        else:
            project.business_name = request.POST.get('business_name', project.business_name)
            project.business_idea = request.POST.get('business_idea', project.business_idea)
            project.industry = request.POST.get('industry', project.industry)
            project.target_audience = request.POST.get('target_audience', project.target_audience)
            project.brand_personality = request.POST.get('brand_personality', project.brand_personality)
            project.preferred_style = request.POST.get('preferred_style', project.preferred_style)
            project.save()
            messages.success(request, "Brand profile successfully updated with catchy improvements!")
            ActivityLog.objects.create(project=project, user=request.user, action="Updated brand profile details.", description="")
        return redirect('branding:project_detail', pk=project.pk)

    # Calculate real completion metrics
    completion_pct = BrandCompletionService.calculate_completion(project)
    project.completion_score = completion_pct
    project.save(update_fields=['completion_score'])
    
    assets = project.assets.all()
    assets_count = assets.count()
    
    # Fetch colors and typography
    colors = {
        'primary': project.primary_color or '#17344F',
        'secondary': project.secondary_color or '#C68B3C',
        'background': project.background_color or '#FBF8F2',
        'accent': project.accent_color or '#8FA99B'
    }
    
    fonts = {
        'primary': project.heading_font or 'Playfair Display',
        'secondary': project.body_font or 'Inter'
    }
    
    context = {
        'project': project,
        'assets': assets,
        'assets_count': assets_count,
        'completion_pct': completion_pct,
        'colors': colors,
        'fonts': fonts,
    }
    return render(request, 'branding/project_detail.html', context)


@login_required
def project_history(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'branding/history.html', {'project': project})


@login_required
def project_settings(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'branding/settings.html', {'project': project})


