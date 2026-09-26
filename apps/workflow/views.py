from collaboration.shortcuts import get_project_for_user
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from branding.models import BrandProject
from workflow.models import ApprovalItem, ContentVersion
from workflow.services.smart_planner import SmartPlannerService
from workflow.services.workflow_service import WorkflowService
from workflow.services.approval_service import ApprovalService
from workflow.services.search_service import SearchService
from workflow.services.health_service import BrandHealthService
from activitylogs.models import ActivityLog
import json

@login_required
def workspace_dashboard(request, pk):
    project = get_project_for_user(pk, request.user)
    
    recommendations = SmartPlannerService.generate_recommendations(project)
    workflow_state = WorkflowService.get_or_create_state(project)
    health_data = BrandHealthService.calculate_health(project)
    recent_activity = ActivityLog.objects.filter(project=project)[:5]
    
    context = {
        'project': project,
        'recommendations': recommendations,
        'workflow_state': workflow_state,
        'health_data': health_data,
        'recent_activity': recent_activity
    }
    return render(request, 'workflow/dashboard.html', context)

@login_required
def content_queue(request, pk):
    project = get_project_for_user(pk, request.user)
    
    pending = ApprovalItem.objects.filter(project=project, status='PENDING')
    approved = ApprovalItem.objects.filter(project=project, status='APPROVED')
    rejected = ApprovalItem.objects.filter(project=project, status='REJECTED')
    
    context = {
        'project': project,
        'pending_items': pending,
        'approved_items': approved,
        'rejected_items': rejected
    }
    return render(request, 'workflow/queue.html', context)

@login_required
def brand_calendar(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'workflow/calendar.html', {'project': project})

@login_required
def approval_action(request, pk, item_id):
    if request.method == 'POST':
        project = get_project_for_user(pk, request.user)
        item = get_object_or_404(ApprovalItem, pk=item_id, project=project)
        
        try:
            data = json.loads(request.body)
            action = data.get('action') # 'APPROVE', 'REJECT'
            
            if action == 'APPROVE':
                ApprovalService.approve_item(item, request.user)
            elif action == 'REJECT':
                feedback = data.get('feedback', '')
                ApprovalService.reject_item(item, request.user, feedback)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
                
            return JsonResponse({'success': True, 'status': item.status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def universal_search(request):
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if len(query) < 2:
            return JsonResponse({'results': []})
            
        results = SearchService.universal_search(request.user, query)
        return JsonResponse({'results': results})
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)
