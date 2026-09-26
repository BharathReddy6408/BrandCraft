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
def generate_names(request, pk):
    from ai_services.context import BrandContextService
    project = get_project_for_user(pk, request.user)
    
    context = BrandContextService.build_context(project)
    prompt = PromptLibrary.get_naming_prompt(context)
        
    system_msg = "You are a world-class branding expert. Output only valid JSON."
    response = AIService.generate_text(prompt, system_msg)
    
    if response:
        try:
            parsed = json.loads(response)
            BrandAsset.objects.create(
                project=project,
                asset_type='NAME',
                content_json=parsed,
                prompt=prompt
            )
        except json.JSONDecodeError:
            BrandAsset.objects.create(
                project=project,
                asset_type='NAME',
                content_json={"names": response.split('\n')},
                prompt=prompt
            )
            
    return redirect('branding:project_detail', pk=project.pk)


@login_required
def project_chat_api(request, pk):
    from ai_services.orchestrator import CopilotOrchestrator
    import json
    
    if request.method == 'POST':
        project = get_project_for_user(pk, request.user)
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            conversation_id = data.get('conversation_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
            
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        result = CopilotOrchestrator.process_message(
            user=request.user,
            project=project,
            message_content=message,
            conversation_id=conversation_id
        )

        if result.get("success"):
            return JsonResponse({
                'response': result['content'].get('text', 'Here is your generated content.'),
                'conversation_id': result['conversation_id'],
                'response_type': result.get('response_type', 'text'),
                'content': result.get('content', {}),
                'actions': result['actions']
            })
        else:
            return JsonResponse({'error': result.get('error', 'Unknown error occurred')}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


