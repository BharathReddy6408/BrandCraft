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
def project_reports(request, pk):
    from brand_reports.models import BrandReport
    project = get_project_for_user(pk, request.user)
    reports = BrandReport.objects.filter(project=project, user=request.user).order_by('-created_at')
    
    reports_by_type = {
        'STRATEGY': reports.filter(report_type='STRATEGY'),
        'IDENTITY': reports.filter(report_type='IDENTITY'),
        'AUDIT': reports.filter(report_type='AUDIT'),
        'CAMPAIGN': reports.filter(report_type='CAMPAIGN'),
        'EXECUTIVE': reports.filter(report_type='EXECUTIVE'),
    }
    
    return render(request, 'branding/reports.html', {
        'project': project,
        'reports_by_type': reports_by_type
    })


@login_required
def project_downloads(request, pk):
    from brand_reports.models import BrandReport
    from downloads.models import ExportRecord
    from analytics.services.completion import BrandCompletionService
    
    project = get_project_for_user(pk, request.user)
    reports = BrandReport.objects.filter(project=project, user=request.user, status='READY')
    exports = ExportRecord.objects.filter(project=project, user=request.user)
    
    # Check Brand Kit Readiness
    foundation_score = BrandCompletionService.calculate_foundation(project)
    activation_score = BrandCompletionService.calculate_activation(project)
    readiness_pct = (foundation_score + activation_score) // 2
    
    has_slogan = project.assets.filter(asset_type='SLOGAN').exists()
    has_logo = project.assets.filter(asset_type='LOGO').exists()
    
    return render(request, 'branding/downloads.html', {
        'project': project,
        'reports': reports,
        'exports': exports,
        'readiness_pct': readiness_pct,
        'has_slogan': has_slogan,
        'has_logo': has_logo
    })


@login_required
def generate_report(request, pk):
    import json
    from django.http import JsonResponse
    from brand_reports.models import BrandReport
    from brand_reports.services.data_service import ReportDataService
    from brand_reports.services.renderer import ReportRenderer

    if request.method == 'POST':
        project = get_project_for_user(pk, request.user)
        try:
            data = json.loads(request.body)
            report_type = data.get('report_type')
            
            if report_type not in [c[0] for c in BrandReport.REPORT_TYPES]:
                return JsonResponse({'success': False, 'error': 'Invalid report type'})
                
            # Collect data based on type
            data_snapshot = {}
            if report_type == 'STRATEGY':
                data_snapshot = ReportDataService.collect_strategy_data(project)
            elif report_type == 'IDENTITY':
                data_snapshot = ReportDataService.collect_identity_data(project)
            elif report_type == 'AUDIT':
                data_snapshot = ReportDataService.collect_audit_data(project)
            elif report_type == 'EXECUTIVE':
                data_snapshot = ReportDataService.collect_executive_data(project)
            else:
                data_snapshot = {}
                
            # Determine version
            latest = BrandReport.objects.filter(project=project, report_type=report_type).order_by('-version').first()
            version = (latest.version + 1) if latest else 1
            
            report = BrandReport.objects.create(
                project=project,
                user=request.user,
                report_type=report_type,
                title=f"{project.business_name} {report_type.title()} Report",
                version=version,
                status='GENERATING',
                data_snapshot=data_snapshot
            )
            
            # Sync generation for MVP
            ReportRenderer.generate_pdf_from_html(f"pdf/{report_type.lower()}_report.html", {'report': report, 'data': data_snapshot}, report)
            
            ActivityLog.objects.create(project=project, user=request.user, action=f"Generated a new **{report_type.title()} Report**.", description="")
            
            return JsonResponse({'success': True, 'report_id': report.id, 'status': report.status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def generate_guidelines(request, pk):
    from django.http import JsonResponse
    from downloads.services.guidelines import BrandGuidelinesService
    if request.method == 'POST':
        try:
            project = get_project_for_user(pk, request.user)
            report = BrandGuidelinesService.generate_guidelines(project, request.user)
            if report:
                return JsonResponse({'success': True, 'report_id': report.id})
            return JsonResponse({'success': False, 'error': 'Failed to generate guidelines'})
        except Exception as e:
            import traceback
            return JsonResponse({'success': False, 'error': f"Exception: {str(e)}\n{traceback.format_exc()}"})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def export_brand_package(request, pk):
    import json
    from django.http import JsonResponse
    from downloads.services.packager import BrandKitService
    if request.method == 'POST':
        project = get_project_for_user(pk, request.user)
        try:
            data = json.loads(request.body)
            inclusions = data.get('inclusions', ['identity', 'logos', 'creative', 'guidelines'])
            export = BrandKitService.generate_zip(project, request.user, inclusions)
            ActivityLog.objects.create(project=project, user=request.user, action="Generated Complete **Brand Kit Archive** ZIP.", description="")
            return JsonResponse({'success': True, 'export_id': export.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def download_file(request, pk, file_type, file_id):
    from django.http import FileResponse, Http404
    from brand_reports.models import BrandReport
    from downloads.models import ExportRecord
    from brand_assets.models import BrandAsset
    
    project = get_project_for_user(pk, request.user)
    
    file_obj = None
    if file_type == 'report':
        file_obj = get_object_or_404(BrandReport, pk=file_id, project=project).file
    elif file_type == 'export':
        file_obj = get_object_or_404(ExportRecord, pk=file_id, project=project).file
    elif file_type == 'asset':
        file_obj = get_object_or_404(BrandAsset, pk=file_id, project=project).file
        
    if not file_obj or not file_obj.name:
        raise Http404("File not found")
        
    import os
    filename = os.path.basename(file_obj.name)
    ActivityLog.objects.create(project=project, user=request.user, action=f"Downloaded file: **{filename}**", description="")
    return FileResponse(file_obj, as_attachment=True, filename=filename)


@login_required
def project_presentation(request, pk):
    project = get_project_for_user(pk, request.user)
    return render(request, 'branding/presentation.html', {'project': project})


