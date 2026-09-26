from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from collaboration.shortcuts import get_project_for_user
from collaboration.services.team_service import TeamService
from collaboration.services.collab_service import CollaborationService
from collaboration.permissions import require_project_access, has_project_access, get_user_project_role
from enterprise.services.sharing_service import SharingService
from collaboration.models import TeamMember, Invitation, ProjectTask, Comment
from brand_assets.models import BrandAsset
from enterprise.models import SharedLink
import json

@login_required
@require_project_access
def brand_hub(request, pk):
    """
    The central hub overview of the brand project.
    """
    project = get_project_for_user(pk, request.user)
    
    # Collect summary data for widgets
    recent_assets = BrandAsset.objects.filter(project=project).order_by('-created_at')[:5]
    upcoming_tasks = ProjectTask.objects.filter(project=project, status__in=['TODO', 'IN_PROGRESS']).order_by('due_date')[:5]
    
    from analytics.services.completion import BrandCompletionService
    health_score = BrandCompletionService.calculate_completion(project)
    
    context = {
        'project': project,
        'recent_assets': recent_assets,
        'upcoming_tasks': upcoming_tasks,
        'health_score': health_score,
        'role': get_user_project_role(request.user, project)
    }
    
    return render(request, 'collaboration/hub.html', context)

@login_required
@require_project_access
def team_management(request, pk):
    project = get_project_for_user(pk, request.user)
    
    # Only Owner or Admin can manage team
    role = get_user_project_role(request.user, project)
    if role not in ['OWNER', 'ADMIN']:
        messages.error(request, "You do not have permission to manage the team.")
        return redirect('collaboration:brand_hub', pk=project.pk)
        
    members = TeamMember.objects.filter(project=project)
    invitations = Invitation.objects.filter(project=project, status='PENDING')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'invite':
            email = request.POST.get('email')
            invite_role = request.POST.get('role', 'VIEWER')
            TeamService.invite_member(project, email, invite_role, request.user)
            messages.success(request, f"Invitation sent to {email}.")
            return redirect('collaboration:team_management', pk=project.pk)
            
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            TeamService.remove_member(project, user_id)
            messages.success(request, "Member removed.")
            return redirect('collaboration:team_management', pk=project.pk)
            
        elif action == 'revoke_invite':
            invite_id = request.POST.get('invite_id')
            TeamService.revoke_invitation(invite_id, request.user)
            messages.success(request, "Invitation revoked.")
            return redirect('collaboration:team_management', pk=project.pk)
            
    return render(request, 'collaboration/team_management.html', {
        'project': project,
        'members': members,
        'invitations': invitations,
        'role': role
    })

@login_required
def accept_invitation(request, token):
    success, result = TeamService.accept_invitation(token, request.user)
    if success:
        messages.success(request, f"You have joined the team for {result.business_name}.")
        return redirect('collaboration:brand_hub', pk=result.pk)
    else:
        messages.error(request, result)
        return redirect('dashboard:home')

@login_required
@require_project_access
def tasks_api(request, pk):
    project = get_project_for_user(pk, request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'create':
                title = data.get('title')
                priority = data.get('priority', 'MEDIUM')
                # Optional Assignee and Due Date handling
                task = CollaborationService.create_task(
                    project=project,
                    creator=request.user,
                    title=title,
                    priority=priority
                )
                return JsonResponse({'success': True, 'task_id': task.id})
                
            elif action == 'update_status':
                task_id = data.get('task_id')
                status = data.get('status')
                CollaborationService.update_task_status(task_id, status)
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'})

def client_presentation(request, token):
    """
    Read-only public/secure presentation mode.
    """
    link = get_object_or_404(SharedLink, token=token)
    
    if not link.is_valid():
        return render(request, 'collaboration/link_expired.html')
        
    if link.password_hash:
        if request.method == 'POST':
            password = request.POST.get('password')
            if SharingService.verify_password(link, password):
                request.session[f'auth_{token}'] = True
            else:
                messages.error(request, "Incorrect password.")
                
        if not request.session.get(f'auth_{token}'):
            return render(request, 'collaboration/password_protect.html', {'token': token})

    project = link.project
    
    # Gather presentation data
    assets = BrandAsset.objects.filter(project=project, status='READY')
    logos = assets.filter(asset_type='LOGO')
    creatives = assets.filter(asset_type__in=['SOCIAL_GRAPHIC', 'POSTER', 'BANNER'])
    
    context = {
        'project': project,
        'logos': logos,
        'creatives': creatives,
        'link': link
    }
    return render(request, 'collaboration/presentation_mode.html', context)
