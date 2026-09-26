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
def project_identity(request, pk):
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        primary = request.POST.get('primary_color', '#17344F')
        secondary = request.POST.get('secondary_color', '#C68B3C')
        accent = request.POST.get('accent_color', '#8FA99B')
        background = request.POST.get('background_color', '#FBF8F2')
        
        BrandAsset.objects.update_or_create(
            project=project,
            asset_type='COLOR',
            defaults={'content_json': {
                'primary': primary,
                'secondary': secondary,
                'accent': accent,
                'background': background
            }}
        )
        messages.success(request, 'Color palette updated successfully!')
        ActivityLog.objects.create(project=project, user=request.user, action="Updated custom **Brand Color Palette**.", description="")
        return redirect('branding:brand_identity', pk=project.pk)
    
    # Fetch colors and typography if generated
    color_asset = project.assets.filter(asset_type='COLOR').first()
    colors = {'primary': '#17344F', 'secondary': '#C68B3C', 'background': '#FBF8F2', 'accent': '#8FA99B'}
    if color_asset and isinstance(color_asset.content_json, dict):
        colors.update(color_asset.content_json)
        
    font_asset = project.assets.filter(asset_type='TYPOGRAPHY').first()
    fonts = {'primary': 'Playfair Display', 'secondary': 'Inter'}
    if font_asset and isinstance(font_asset.content_json, dict):
        fonts.update(font_asset.content_json)
        
    primary_logo = project.assets.filter(asset_type='LOGO', is_selected=True).first()
        
    context = {
        'project': project,
        'colors': colors,
        'fonts': fonts,
        'primary_logo': primary_logo
    }
    return render(request, 'branding/identity.html', context)


@login_required
def logo_studio(request, pk):
    class LogoPromptAgent:
        def generate_logo_prompt(self, project, style, logo_type):
            prompt = f"Create a detailed AI image generation prompt for a logo. IMPORTANT: Ensure the prompt explicitly commands a {style} style and a {logo_type} format. Business Name: '{project.business_name}'. Brand Personality: '{project.brand_personality}'. Return JSON with 'prompt' (string) containing the exact image prompt starting with: 'A {style} {logo_type} logo for {project.business_name}...'"
            return AIService.generate_structured(prompt) or {}
    from ai_services.services import AIService
    from django.core.files.base import ContentFile
    import time
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            style = request.POST.get('style', 'Minimalist')
            logo_type = request.POST.get('type', 'Wordmark')
            
            agent = LogoPromptAgent()
            prompt_data = agent.generate_logo_prompt(project, style, logo_type)
            
            if not prompt_data or 'prompt' not in prompt_data:
                # Fallback to a basic constructed prompt if AI generation fails
                prompt_data = {'prompt': f"A {style} {logo_type} logo for {project.business_name}"}
                
            if prompt_data and 'prompt' in prompt_data:
                image_bytes = AIService.generate_image(prompt_data['prompt'])
                
                if image_bytes:
                    asset = BrandAsset.objects.create(
                        user=request.user,
                        project=project,
                        asset_type='LOGO',
                        prompt=prompt_data['prompt'],
                        metadata={'style': style, 'type': logo_type},
                        status='READY'
                    )
                    # Save the image to the file_upload field
                    filename = f"logo_{project.id}_{int(time.time())}.png"
                    asset.file_upload.save(filename, ContentFile(image_bytes))
                    asset.save()
                    messages.success(request, 'Logo generated successfully!')
                else:
                    messages.error(request, 'Failed to generate the image. Please check API settings.')
                
            return redirect('branding:logo_studio', pk=project.pk)
            
        elif action == 'select_logo':
            asset_id = request.POST.get('asset_id')
            if asset_id:
                asset = get_object_or_404(BrandAsset, pk=asset_id, project=project)
                BrandAsset.objects.filter(project=project, asset_type='LOGO').update(is_selected=False)
                asset.is_selected = True
                asset.save()
                messages.success(request, 'Primary logo updated!')
            return redirect('branding:logo_studio', pk=project.pk)
            
    logos = BrandAsset.objects.filter(project=project, asset_type='LOGO').order_by('-created_at')
    
    return render(request, 'branding/logo_studio.html', {
        'project': project,
        'logos': logos
    })


@login_required
def creative_studio(request, pk):
    class CreativeDirectionAgent:
        def generate_creative_prompt(self, project, asset_type, goal):
            prompt = (
                f"Create a detailed AI image generation prompt for a {asset_type}. "
                f"Business Name: '{project.business_name}'. Industry: '{project.industry}'. "
                f"Brand Personality: '{project.brand_personality}'. Goal: {goal}. "
                f"CRITICAL INSTRUCTION: The 'prompt' MUST describe a highly specific, photorealistic visual scene "
                f"with concrete subjects (e.g., 'A modern coffee cup on a wooden table next to a laptop', or 'A group of diverse professionals in a bright modern office'). "
                f"DO NOT use abstract marketing fluff like 'generate a visually appealing image representing community'. "
                f"Describe exactly what the camera sees. "
                f"Return JSON with 'prompt' (string), 'headline' (string), 'subheadline' (string)."
            )
            return AIService.generate_structured(prompt) or {}
    from ai_services.services import AIService
    from django.core.files.base import ContentFile
    import time
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate':
            asset_type = request.POST.get('asset_type', 'Social Post')
            goal = request.POST.get('goal', 'Brand Awareness')
            
            agent = CreativeDirectionAgent()
            prompt_data = agent.generate_creative_prompt(project, asset_type, goal)
            
            if not prompt_data or 'prompt' not in prompt_data:
                # Fallback to a basic constructed prompt if AI generation fails
                prompt_data = {'prompt': f"A creative {asset_type} image for a {project.industry} business named {project.business_name}"}
                
            if prompt_data and 'prompt' in prompt_data:
                image_bytes = AIService.generate_image(prompt_data['prompt'])
                
                if image_bytes:
                    asset = BrandAsset.objects.create(
                        user=request.user,
                        project=project,
                        asset_type='SOCIAL_GRAPHIC' if 'Social' in asset_type else 'POSTER',
                        title=f"{asset_type} - {goal}",
                        prompt=prompt_data['prompt'],
                        metadata={'headline': prompt_data.get('headline'), 'subheadline': prompt_data.get('subheadline'), 'goal': goal},
                        status='READY'
                    )
                    filename = f"creative_{project.id}_{int(time.time())}.png"
                    asset.file_upload.save(filename, ContentFile(image_bytes))
                    asset.save()
                    messages.success(request, 'Creative asset generated successfully!')
                else:
                    messages.error(request, 'Failed to generate the image. Please check API settings.')
                
            return redirect('branding:creative_studio', pk=project.pk)
            
    creative_assets = BrandAsset.objects.filter(project=project, asset_type__in=['SOCIAL_GRAPHIC', 'POSTER', 'BANNER', 'AD_CREATIVE']).order_by('-created_at')
    
    context = {
        'project': project,
        'creative_assets': creative_assets
    }
    return render(request, 'branding/creative_studio.html', context)


@login_required
def marketing_studio(request, pk):
    import json
    from django.http import JsonResponse
    from marketing.services import MarketingGenerationService, ContentRefinementService
    from marketing.models import MarketingContent
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        if is_ajax:
            try:
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'generate':
                    content_type = data.get('content_type')
                    content = MarketingGenerationService.generate(
                        user=request.user,
                        project=project,
                        content_type=content_type,
                        **data.get('kwargs', {})
                    )
                    if content:
                        return JsonResponse({
                            'success': True, 
                            'id': content.id, 
                            'content_json': content.content_json,
                            'title': content.title,
                            'content_type_display': content.get_content_type_display(),
                            'status_display': content.get_status_display(),
                            'created_at': content.created_at.strftime("%b %d, %Y")
                        })
                    return JsonResponse({'success': False, 'error': 'Failed to generate content'}, status=500)
                    
                elif action == 'refine':
                    content_id = data.get('content_id')
                    operation = data.get('operation')
                    content = get_object_or_404(MarketingContent, pk=content_id, project=project, user=request.user)
                    
                    refined = ContentRefinementService.refine_content(
                        user=request.user,
                        project=project,
                        existing_content=content,
                        operation=operation
                    )
                    if refined:
                        return JsonResponse({'success': True, 'content_json': refined.content_json})
                    return JsonResponse({'success': False, 'error': 'Failed to refine content'}, status=500)
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
                
    recent_content = MarketingContent.objects.filter(project=project, user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'branding/marketing_studio.html', {
        'project': project,
        'recent_content': recent_content
    })


@login_required
def name_slogan_studio(request, pk):
    class NamingAgent:
        def generate_names(self, project_id, style, count, keyword):
            prompt = f"Generate {count} business names. Style: {style}. Keyword: {keyword}. Return JSON with 'names' (list of strings)."
            from ai_services.services import AIService
            return AIService.generate_structured(prompt) or {}
            
    class CopywritingAgent:
        def generate_slogans(self, project_id, tone, length):
            prompt = f"Generate 5 slogans. Tone: {tone}. Length: {length}. Return JSON with 'slogans' (list of strings)."
            from ai_services.services import AIService
            return AIService.generate_structured(prompt) or {}
            
    class AICoordinator:
        def __init__(self):
            self.naming_agent = NamingAgent()
            self.copywriting_agent = CopywritingAgent()
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'generate_names':
            style = request.POST.get('style', 'Modern')
            count = int(request.POST.get('count', 5))
            keyword = request.POST.get('keyword', '')
            
            coordinator = AICoordinator()
            names_result = coordinator.naming_agent.generate_names(project.id, style=style, count=count, keyword=keyword)
            
            if not names_result or "names" not in names_result:
                # Dynamic fallback using project brand data
                base = keyword if keyword else project.business_name if project.business_name else "Brand"
                ind = project.industry if project.industry else "Business"
                sty = style.lower()
                style_suffixes = {
                    'modern': ['Studio', 'Labs', 'Works', 'Co', 'Hub'],
                    'playful': ['Zone', 'World', 'Planet', 'Spot', 'Place'],
                    'luxurious': ['Elite', 'Prestige', 'Premier', 'Luxe', 'Select'],
                    'minimal': ['Co', 'By', 'Studio', 'Group', 'Group'],
                    'tech': ['AI', 'Tech', 'Systems', 'Digital', 'Labs'],
                }
                suffixes = style_suffixes.get(sty, ['Group', 'Solutions', 'Studio', 'Co', 'Hub'])
                names_result = {"names": [
                    f"{base} {suffixes[0]}",
                    f"{base} {ind} {suffixes[1]}",
                    f"The {base} {suffixes[2]}",
                    f"{base} & {suffixes[3]}",
                    f"{base} {suffixes[4]}",
                ]}
                
            if names_result and "names" in names_result:
                BrandAsset.objects.create(
                    user=request.user,
                    project=project,
                    asset_type='BUSINESS_NAME',
                    content_json=names_result,
                    status='READY',
                    metadata={'style': style, 'count': count, 'keyword': keyword}
                )
                messages.success(request, 'Business names generated successfully!')
            return redirect('branding:name_slogan_studio', pk=project.pk)
            
        elif action == 'generate_slogans':
            tone = request.POST.get('tone', 'Professional')
            length = request.POST.get('length', 'Short')
            
            coordinator = AICoordinator()
            slogans_result = coordinator.copywriting_agent.generate_slogans(project.id, tone=tone, length=length)
            
            if not slogans_result or "slogans" not in slogans_result:
                # Dynamic fallback using project brand data
                bname = project.business_name or 'Your Brand'
                ind = project.industry or 'your industry'
                personality = project.brand_personality or 'excellence'
                audience = project.target_audience or 'everyone'
                slogans_result = {"slogans": [
                    f"{bname}: Where {personality} meets {ind}.",
                    f"Built for {audience}. Powered by {personality}.",
                    f"{bname} — {ind} redefined.",
                    f"Your {ind} journey starts with {bname}.",
                    f"Delivering {personality} to {audience}, every time.",
                ]}
            
            if slogans_result and "slogans" in slogans_result:
                BrandAsset.objects.create(
                    user=request.user,
                    project=project,
                    asset_type='SLOGAN',
                    content_json=slogans_result,
                    status='READY',
                    metadata={'tone': tone, 'length': length}
                )
            return redirect('branding:name_slogan_studio', pk=project.pk)
            
        elif action == 'select_name':
            selected_name = request.POST.get('selected_name')
            if selected_name:
                project.business_name = selected_name
                project.save()
            return redirect('branding:name_slogan_studio', pk=project.pk)
            
        elif action == 'select_slogan':
            slogan_text = request.POST.get('slogan_text')
            asset_id = request.POST.get('asset_id')
            if slogan_text and asset_id:
                asset = get_object_or_404(BrandAsset, pk=asset_id, project=project)
                # Clear other selections
                BrandAsset.objects.filter(project=project, asset_type='SLOGAN').update(is_selected=False)
                asset.is_selected = True
                asset.save()
            return redirect('branding:name_slogan_studio', pk=project.pk)

    name_assets = BrandAsset.objects.filter(project=project, asset_type='BUSINESS_NAME').order_by('-created_at')
    slogan_assets = BrandAsset.objects.filter(project=project, asset_type='SLOGAN').order_by('-created_at')
    
    return render(request, 'branding/name_slogan_studio.html', {
        'project': project,
        'name_assets': name_assets,
        'slogan_assets': slogan_assets
    })


@login_required
def campaign_studio(request, pk):
    import json
    from django.http import JsonResponse
    from campaigns.services import CampaignGenerationService
    from campaigns.models import Campaign
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        if is_ajax:
            try:
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'generate':
                    campaign = CampaignGenerationService.generate(
                        user=request.user,
                        project=project,
                        name=data.get('name'),
                        goal=data.get('goal'),
                        duration=data.get('duration'),
                        platforms=data.get('platforms', [])
                    )
                    
                    if campaign:
                        items = list(campaign.items.values('scheduled_day', 'platform', 'content_type', 'topic', 'objective'))
                        return JsonResponse({
                            'success': True,
                            'id': campaign.id,
                            'strategy': campaign.strategy,
                            'audience_focus': campaign.audience_focus,
                            'content_pillars': campaign.content_pillars,
                            'timeline': items
                        })
                    return JsonResponse({'success': False, 'error': 'Failed to generate campaign'}, status=500)
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
                
    recent_campaigns = Campaign.objects.filter(project=project, user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'branding/campaign_studio.html', {
        'project': project,
        'recent_campaigns': recent_campaigns
    })


@login_required
def social_studio(request, pk):
    import json
    from django.http import JsonResponse
    from socialmedia.services import SocialGenerationService
    from socialmedia.models import SocialPost
    
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        if is_ajax:
            try:
                data = json.loads(request.body)
                action = data.get('action')
                
                if action == 'generate':
                    platform = data.get('platform')
                    post = SocialGenerationService.generate(
                        user=request.user,
                        project=project,
                        platform=platform,
                        **data.get('kwargs', {})
                    )
                    if post:
                        from workflow.services.approval_service import ApprovalService
                        ApprovalService.queue_for_approval(
                            project=project,
                            user=request.user,
                            instance=post,
                            item_type="Social Post",
                            title=f"{platform} Post",
                            payload=post.content_json
                        )
                        return JsonResponse({'success': True, 'id': post.id, 'content_json': post.content_json, 'queued': True})
                    return JsonResponse({'success': False, 'error': 'Failed to generate post'}, status=500)
                    
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
                
    # Also we should only show approved posts in the recent list? 
    # For now, let's just leave it as is or show status.
    recent_posts = SocialPost.objects.filter(project=project, user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'branding/social_studio.html', {
        'project': project,
        'recent_posts': recent_posts
    })


