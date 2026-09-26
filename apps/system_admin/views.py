import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count
from django.contrib import messages

# Importing available models for real data
from accounts.models import Role, Permission, RolePermission, Organization
from branding.models import BrandProject
from subscriptions.models import SubscriptionPlan, UserSubscription
from model_management.models import AIModel
from knowledge_base.models import Document
from ai_services.models import PromptTemplate
from brand_assets.models import BrandAsset, AssetCategory, BrandTemplate
from audit.models import AuditLog
from monitoring.models import SystemPerformance, SystemError

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def admin_dashboard(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_projects = BrandProject.objects.count()
    total_generations = BrandAsset.objects.count()
    total_assets = BrandAsset.objects.count()
    
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_generations = BrandAsset.objects.order_by('-created_at')[:5]
    recent_logs = AuditLog.objects.order_by('-timestamp')[:5]
    
    context = {
        'active_module': 'Overview',
        'metrics': {
            'total_users': total_users,
            'active_users': active_users,
            'total_projects': total_projects,
            'total_generations': total_generations,
            'total_assets': total_assets,
        },
        'recent_users': recent_users,
        'recent_generations': recent_generations,
        'recent_logs': recent_logs,
    }
    return render(request, 'system_admin/dashboard.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def analytics_center(request):
    from django.db.models.functions import TruncDate
    
    # 1. KPI Metrics
    total_users = User.objects.count()
    total_projects = BrandProject.objects.count()
    total_generations = BrandAsset.objects.count()
    total_assets = BrandAsset.objects.count()
    
    # 2. Daily Generation Trend (Last 30 Days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    generation_trend = (BrandAsset.objects.filter(created_at__gte=thirty_days_ago)
                        .annotate(date=TruncDate('created_at'))
                        .values('date')
                        .annotate(count=Count('id'))
                        .order_by('date'))
    
    trend_labels = [str(g['date']) for g in generation_trend]
    trend_data = [g['count'] for g in generation_trend]

    # 3. Popular Generator Types
    popular_types = (BrandAsset.objects
                     .values('asset_type')
                     .annotate(count=Count('id'))
                     .order_by('-count')[:5])
    
    type_labels = [g['asset_type'] if g['asset_type'] else 'Unknown' for g in popular_types]
    type_data = [g['count'] for g in popular_types]

    context = {
        'active_module': 'Analytics',
        'metrics': {
            'total_users': total_users,
            'total_projects': total_projects,
            'total_generations': total_generations,
            'total_assets': total_assets,
        },
        'chart_trend_labels': json.dumps(trend_labels),
        'chart_trend_data': json.dumps(trend_data),
        'chart_type_labels': json.dumps(type_labels),
        'chart_type_data': json.dumps(type_data),
    }
    return render(request, 'system_admin/analytics.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def reports_management(request):
    from django.db.models.functions import TruncDate
    import json
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # User Registrations Trend
    user_trend = (User.objects.filter(date_joined__gte=thirty_days_ago)
                  .annotate(date=TruncDate('date_joined'))
                  .values('date')
                  .annotate(count=Count('id'))
                  .order_by('date'))
    user_labels = [str(u['date']) for u in user_trend]
    user_data = [u['count'] for u in user_trend]
    
    # Project Creation Trend
    project_trend = (BrandProject.objects.filter(created_at__gte=thirty_days_ago)
                     .annotate(date=TruncDate('created_at'))
                     .values('date')
                     .annotate(count=Count('id'))
                     .order_by('date'))
    project_labels = [str(p['date']) for p in project_trend]
    project_data = [p['count'] for p in project_trend]

    context = {
        'active_module': 'Reports Management',
        'user_labels': json.dumps(user_labels),
        'user_data': json.dumps(user_data),
        'project_labels': json.dumps(project_labels),
        'project_data': json.dumps(project_data)
    }
    return render(request, 'system_admin/reports_management.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    context = {'active_module': 'User Management', 'users': users, 'query': query}
    return render(request, 'system_admin/user_list.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        user_to_toggle = get_object_or_404(User, id=user_id)
        if user_to_toggle.id != request.user.id:
            user_to_toggle.is_active = not user_to_toggle.is_active
            user_to_toggle.save()
            status = "activated" if user_to_toggle.is_active else "suspended"
            messages.success(request, f"User {user_to_toggle.username} has been {status}.")
    return redirect('system_admin:user_list')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            if role in ['superadmin', 'staff']: user.is_staff = True
            if role == 'superadmin': user.is_superuser = True
            user.save()
            return redirect('system_admin:user_list')
    return render(request, 'system_admin/user_form.html', {'active_module': 'User Management'})

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def organization_management(request):
    organizations = Organization.objects.all().order_by('-created_at')
    context = {'active_module': 'Organization Management', 'organizations': organizations}
    return render(request, 'system_admin/organization_management.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def create_organization(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        org_type = request.POST.get('org_type')
        if name and org_type:
            Organization.objects.create(
                name=name,
                org_type=org_type,
                owner=request.user
            )
            messages.success(request, f"Organization '{name}' created successfully.")
    return redirect('system_admin:organizations')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def role_permissions(request):
    from accounts.models import Role, Permission
    roles = Role.objects.prefetch_related('permissions__permission').all()
    permissions = Permission.objects.all()
    context = {'active_module': 'Role & Permissions Management', 'roles': roles, 'permissions': permissions}
    return render(request, 'system_admin/role_permissions.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def create_role(request):
    if request.method == 'POST':
        from accounts.models import Role
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            if Role.objects.filter(name=name).exists():
                messages.error(request, f"A role with the name '{name}' already exists.")
            else:
                Role.objects.create(name=name, description=description)
                messages.success(request, f"Role '{name}' created successfully.")
    return redirect('system_admin:roles')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def subscription_billing(request):
    plans = SubscriptionPlan.objects.all()
    subscriptions = UserSubscription.objects.select_related('user', 'plan').all()
    context = {'active_module': 'Subscription & Billing', 'plans': plans, 'active_subs': subscriptions}
    return render(request, 'system_admin/subscription_billing.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def update_subscription_plan(request, plan_id):
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        plan.monthly_price = request.POST.get('monthly_price', plan.monthly_price)
        plan.max_brands = request.POST.get('max_brands', plan.max_brands)
        plan.max_generations_per_month = request.POST.get('max_generations_per_month', plan.max_generations_per_month)
        plan.save()
        messages.success(request, f"Plan '{plan.name}' updated successfully.")
    return redirect('system_admin:subscriptions')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def manage_subscription(request, user_sub_id):
    if request.method == 'POST':
        sub = get_object_or_404(UserSubscription, id=user_sub_id)
        action = request.POST.get('action')
        if action == 'cancel':
            sub.is_active = False
            sub.save()
            messages.success(request, f"Subscription for {sub.user.username} cancelled.")
        elif action == 'activate':
            sub.is_active = True
            sub.save()
            messages.success(request, f"Subscription for {sub.user.username} activated.")
    return redirect('system_admin:subscriptions')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def ai_generations(request):
    generations = BrandAsset.objects.select_related('project', 'project__user').order_by('-created_at')
    context = {'active_module': 'AI Generation Center', 'generations': generations}
    return render(request, 'system_admin/ai_generations.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def approve_generation(request, asset_id):
    if request.method == 'POST':
        asset = get_object_or_404(BrandAsset, id=asset_id)
        asset.status = 'APPROVED'
        asset.save()
        messages.success(request, f"Generation '{asset.get_asset_type_display()}' approved.")
    return redirect('system_admin:ai_generations')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def reject_generation(request, asset_id):
    if request.method == 'POST':
        asset = get_object_or_404(BrandAsset, id=asset_id)
        asset.status = 'REJECTED'
        asset.save()
        messages.success(request, f"Generation '{asset.get_asset_type_display()}' rejected.")
    return redirect('system_admin:ai_generations')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def model_management(request):
    models = AIModel.objects.all()
    context = {'active_module': 'AI Model Management', 'models': models}
    return render(request, 'system_admin/model_management.html', context)

import csv
from django.http import HttpResponse

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type', 'report')
        date_range = request.POST.get('date_range', 'unknown')
        
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{report_type.lower().replace(" ", "_")}_{date_range.lower().replace(" ", "_")}.csv"'},
        )
        
        writer = csv.writer(response)
        
        if report_type == "Marketing Analytics":
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Users', User.objects.count()])
            writer.writerow(['Total Projects', BrandProject.objects.count()])
            writer.writerow(['Total Generations', BrandAsset.objects.count()])
            writer.writerow(['Total Assets', BrandAsset.objects.count()])
        elif report_type == "User Engagement":
            writer.writerow(['Username', 'Email', 'Date Joined', 'Active'])
            for u in User.objects.all().order_by('-date_joined')[:100]:
                writer.writerow([u.username, u.email, u.date_joined.strftime("%Y-%m-%d"), u.is_active])
        elif report_type == "Brand Usage":
            writer.writerow(['Project Name', 'Owner', 'Created At'])
            for p in BrandProject.objects.select_related('user').all()[:100]:
                writer.writerow([p.business_name, p.user.username if p.user else 'N/A', p.created_at.strftime("%Y-%m-%d")])
        else:
            writer.writerow(['Report Type', 'Date Range'])
            writer.writerow([report_type, date_range])
            writer.writerow(['Note', 'This is a system generated report.'])
            
        return response
        
    return redirect('system_admin:reports')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def add_model(request):
    if request.method == 'POST':
        predefined_model = request.POST.get('predefined_model')
        
        models_data = {
            'groq_llama3': {
                'name': 'Groq Llama 3 70B',
                'model_type': 'TEXT',
                'version': '3-70b',
                'provider_name': 'Groq',
                'api_identifier': 'llama3-70b-8192',
                'status': 'ACTIVE'
            },
            'local_sd': {
                'name': 'Local Stable Diffusion',
                'model_type': 'IMAGE',
                'version': 'XL',
                'provider_name': 'Local ML',
                'api_identifier': 'local-sd-xl',
                'status': 'ACTIVE'
            },
            'local_embedding': {
                'name': 'Local Sentence Transformers',
                'model_type': 'EMBEDDING',
                'version': 'v1',
                'provider_name': 'Local ML',
                'api_identifier': 'local-all-MiniLM-L6-v2',
                'status': 'ACTIVE'
            }
        }
        
        if predefined_model in models_data:
            data = models_data[predefined_model]
            if not AIModel.objects.filter(api_identifier=data['api_identifier']).exists():
                AIModel.objects.create(
                    name=data['name'],
                    model_type=data['model_type'],
                    version=data['version'],
                    provider_name=data['provider_name'],
                    api_identifier=data['api_identifier'],
                    status=data['status']
                )
                messages.success(request, f"Model {data['name']} added successfully.")
            else:
                messages.warning(request, f"Model {data['name']} is already configured.")
        else:
            messages.error(request, "Invalid model selection.")
            
    return redirect('system_admin:models')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def remove_model(request, model_id):
    if request.method == 'POST':
        model = get_object_or_404(AIModel, id=model_id)
        model.delete()
        messages.success(request, f"Model '{model.name}' removed.")
    return redirect('system_admin:models')

# --- Fine-Tuning & Datasets ---
from model_management.models import Dataset, ModelTrainingJob
import random
from django.utils import timezone

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def fine_tuning_dashboard(request):
    datasets = Dataset.objects.all().order_by('-created_at')
    jobs = ModelTrainingJob.objects.select_related('base_model', 'dataset').order_by('-started_at')
    models = AIModel.objects.filter(status='ACTIVE')
    context = {
        'active_module': 'Fine-Tuning & Datasets',
        'datasets': datasets,
        'jobs': jobs,
        'models': models
    }
    return render(request, 'system_admin/fine_tuning.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def upload_dataset(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        dataset_type = request.POST.get('dataset_type')
        file = request.FILES.get('file')
        
        if name and file:
            Dataset.objects.create(
                name=name,
                dataset_type=dataset_type,
                file=file,
                record_count=random.randint(500, 10000) # mock record count
            )
            messages.success(request, f"Dataset '{name}' uploaded successfully.")
    return redirect('system_admin:fine_tuning')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def preprocess_dataset(request, dataset_id):
    if request.method == 'POST':
        dataset = get_object_or_404(Dataset, id=dataset_id)
        dataset.status = 'READY'
        dataset.save()
        messages.success(request, f"Dataset '{dataset.name}' preprocessed successfully and is ready for training.")
    return redirect('system_admin:fine_tuning')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def start_training(request):
    if request.method == 'POST':
        model_id = request.POST.get('model_id')
        dataset_id = request.POST.get('dataset_id')
        epochs = int(request.POST.get('epochs', 3))
        
        if model_id and dataset_id:
            base_model = get_object_or_404(AIModel, id=model_id)
            dataset = get_object_or_404(Dataset, id=dataset_id)
            
            ModelTrainingJob.objects.create(
                base_model=base_model,
                dataset=dataset,
                epochs=epochs,
                status='TRAINING',
                started_at=timezone.now()
            )
            messages.success(request, f"Training job started for {base_model.name} on dataset {dataset.name}.")
    return redirect('system_admin:fine_tuning')

from django.http import JsonResponse
@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def complete_mock_training(request, job_id):
    # This is a mock endpoint called via AJAX to finish training
    if request.method == 'POST':
        job = get_object_or_404(ModelTrainingJob, id=job_id)
        if job.status == 'TRAINING':
            # generate mock logs
            import json
            logs = []
            acc = 0.5
            loss = 2.0
            for i in range(1, job.epochs + 1):
                acc += random.uniform(0.01, 0.1)
                loss -= random.uniform(0.05, 0.2)
                if acc > 0.99: acc = 0.99
                if loss < 0.05: loss = 0.05
                logs.append({"epoch": i, "accuracy": round(acc, 4), "loss": round(loss, 4)})
                
            job.status = 'COMPLETED'
            job.final_accuracy = logs[-1]['accuracy']
            job.final_loss = logs[-1]['loss']
            job.training_logs = json.dumps(logs)
            job.completed_at = timezone.now()
            job.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def configure_model(request, model_id):
    if request.method == 'POST':
        model = get_object_or_404(AIModel, id=model_id)
        api_key = request.POST.get('api_key')
        status = request.POST.get('status')
        
        if api_key is not None:
            model.api_key = api_key
        if status in ['ACTIVE', 'INACTIVE', 'TESTING', 'DEPRECATED']:
            model.status = status
            
        model.save()
        messages.success(request, f"Configuration for {model.name} updated successfully.")
    return redirect('system_admin:models')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def knowledge_base(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    context = {'active_module': 'AI Knowledge Base', 'documents': documents}
    return render(request, 'system_admin/knowledge_base.html', context)

from django.http import JsonResponse

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def upload_document(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if request.FILES.getlist('document'):
            from knowledge_base.models import Document
            docs_data = []
            for file in request.FILES.getlist('document'):
                title = file.name
                # For this prototype, we immediately set it to processed so it doesn't get stuck.
                doc = Document.objects.create(title=title, file=file, is_processed=True)
                
                # Format date to match template 'Aug 27, 2026'
                docs_data.append({
                    'id': doc.id, 
                    'title': doc.title, 
                    'is_processed': doc.is_processed,
                    'uploaded_at': doc.uploaded_at.strftime("%b %d, %Y")
                })
                
            if is_ajax:
                return JsonResponse({'success': True, 'documents': docs_data})
                
            messages.success(request, f"Documents uploaded successfully.")
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'No document file was uploaded'})
            messages.error(request, "No document file was uploaded in the request.")
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request method.'})
        messages.error(request, "Invalid request method.")
    return redirect('system_admin:knowledge_base')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def delete_document(request, document_id):
    if request.method == 'POST':
        from knowledge_base.models import Document
        doc = get_object_or_404(Document, id=document_id)
        title = doc.title
        doc.file.delete(save=False) # Delete actual file
        doc.delete() # Delete DB record
        messages.success(request, f"Document '{title}' deleted successfully.")
    return redirect('system_admin:knowledge_base')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def prompt_library(request):
    prompts = PromptTemplate.objects.all().order_by('name')
    active_prompt_id = request.GET.get('id')
    if active_prompt_id:
        active_prompt = get_object_or_404(PromptTemplate, id=active_prompt_id)
    else:
        active_prompt = prompts.first() if prompts.exists() else None
        
    test_result = request.session.pop('test_result', None)
        
    context = {'active_module': 'Prompt Library', 'prompts': prompts, 'active_prompt': active_prompt, 'test_result': test_result}
    return render(request, 'system_admin/prompt_library.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def create_prompt(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        template_content = request.POST.get('template_content', '')
        if name:
            prompt = PromptTemplate.objects.create(name=name, description=description, template_content=template_content)
            messages.success(request, "New prompt template created.")
            return redirect(f'/portal/prompts/?id={prompt.id}')
    return redirect('system_admin:prompts')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def update_prompt(request, prompt_id):
    if request.method == 'POST':
        prompt = get_object_or_404(PromptTemplate, id=prompt_id)
        content = request.POST.get('template_content')
        if content is not None:
            prompt.template_content = content
            prompt.save()
            messages.success(request, f"Prompt '{prompt.name}' saved successfully.")
    return redirect(f'/portal/prompts/?id={prompt_id}')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def test_prompt(request, prompt_id):
    if request.method == 'POST':
        prompt = get_object_or_404(PromptTemplate, id=prompt_id)
        test_input = request.POST.get('test_input', '{}')
        unsaved_template = request.POST.get('unsaved_template_content')
        try:
            import json
            from django.template import Template, Context
            
            variables = json.loads(test_input)
            template_string = unsaved_template if unsaved_template else prompt.template_content
            t = Template(template_string)
            c = Context(variables)
            rendered_prompt = t.render(c)
            
            request.session['test_result'] = rendered_prompt
            messages.success(request, "Prompt rendered successfully!")
        except json.JSONDecodeError:
            request.session['test_result'] = "ERROR: Invalid JSON input. Please ensure you are using double quotes for keys and values, e.g. {\"brand_name\": \"Apple\"}."
            messages.error(request, "Invalid JSON input for test variables.")
        except Exception as e:
            request.session['test_result'] = f"ERROR rendering template: {str(e)}"
            messages.error(request, f"Error rendering template: {str(e)}")
            
    return redirect(f'/portal/prompts/?id={prompt_id}')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def asset_management(request):
    from brand_assets.models import AssetCategory
    
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    category_id = request.GET.get('type', '')
    project_id = request.GET.get('project', '')
    
    assets = BrandAsset.objects.select_related('project', 'project__user', 'category').all().order_by('-created_at')
    
    if q:
        assets = assets.filter(
            Q(title__icontains=q) | 
            Q(project__business_name__icontains=q) | 
            Q(project__user__username__icontains=q)
        )
    if status:
        assets = assets.filter(status=status)
    if category_id:
        assets = assets.filter(category_id=category_id)
    if project_id:
        assets = assets.filter(project_id=project_id)
        
    categories = AssetCategory.objects.all()
    projects = BrandProject.objects.all().order_by('business_name')
    
    context = {
        'active_module': 'Creative Asset Management', 
        'assets': assets,
        'categories': categories,
        'projects': projects,
        'current_q': q,
        'current_status': status,
        'current_type': category_id,
        'current_project': project_id,
    }
    return render(request, 'system_admin/asset_management.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def content_moderation(request):
    # For now, just show recent assets as an example
    assets = BrandAsset.objects.select_related('project', 'project__user').all()[:10]
    context = {'active_module': 'Content Moderation', 'assets': assets}
    return render(request, 'system_admin/content_moderation.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def approve_asset(request, asset_id):
    if request.method == 'POST':
        asset = get_object_or_404(BrandAsset, id=asset_id)
        asset.status = 'APPROVED'
        asset.save()
        messages.success(request, f"Asset '{asset.title}' has been approved.")
    return redirect('system_admin:assets')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def flag_asset(request, asset_id):
    if request.method == 'POST':
        asset = get_object_or_404(BrandAsset, id=asset_id)
        asset.status = 'FLAGGED'
        asset.save()
        messages.warning(request, f"Asset '{asset.title}' has been flagged.")
    return redirect('system_admin:assets')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def delete_asset(request, asset_id):
    if request.method == 'POST':
        asset = get_object_or_404(BrandAsset, id=asset_id)
        title = asset.title
        if asset.file_upload:
            asset.file_upload.delete(save=False)
        asset.delete()
        messages.success(request, f"Asset '{title}' deleted.")
    return redirect('system_admin:assets')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def security_center(request):
    logs = AuditLog.objects.all().order_by('-timestamp')[:50]
    context = {'active_module': 'Security Center', 'logs': logs}
    return render(request, 'system_admin/security_center.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def system_monitoring(request):
    perf = SystemPerformance.objects.order_by('-timestamp')[:1]
    errors = SystemError.objects.order_by('-timestamp')[:10]
    context = {'active_module': 'System Monitoring', 'performance': perf, 'errors': errors}
    return render(request, 'system_admin/system_monitoring.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def platform_settings(request):
    context = {'active_module': 'Platform Settings'}
    return render(request, 'system_admin/platform_settings.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def save_settings(request):
    if request.method == 'POST':
        platform_name = request.POST.get('platform_name')
        messages.success(request, f"Platform settings updated successfully.")
    return redirect('system_admin:settings')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def legacy_redirect(request, module_name):
    mapping = {
        'creative-asset-mgmt': 'system_admin:assets',
        'analytics-center': 'system_admin:analytics',
        'reports-management': 'system_admin:reports',
        'organization-management': 'system_admin:organizations',
        'role-and-permissions': 'system_admin:roles',
        'subscription-and-billing': 'system_admin:subscriptions',
        'ai-generation-center': 'system_admin:ai_generations',
        'ai-model-management': 'system_admin:models',
        'ai-knowledge-base': 'system_admin:knowledge_base',
        'prompt-library': 'system_admin:prompts',
        'content-moderation': 'system_admin:moderation',
        'security-center': 'system_admin:security',
        'system-monitoring': 'system_admin:monitoring',
        'platform-settings': 'system_admin:settings',
    }
    return redirect(mapping.get(module_name, 'system_admin:dashboard'))

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def brand_templates(request):
    templates = BrandTemplate.objects.select_related('category').order_by('-created_at')
    categories = AssetCategory.objects.all()
    context = {
        'active_module': 'Brand Templates',
        'templates': templates,
        'categories': categories,
    }
    return render(request, 'system_admin/brand_templates.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def add_brand_template(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category_id')
        
        if not title:
            messages.error(request, 'Title is required for a brand template.')
            return redirect('system_admin:brand_templates')
            
        template = BrandTemplate(
            title=title,
            description=description,
            category_id=category_id if category_id else None
        )
        
        if 'thumbnail' in request.FILES:
            template.thumbnail = request.FILES['thumbnail']
            
        if 'file' in request.FILES:
            template.file = request.FILES['file']
            
        template.save()
        messages.success(request, f"Brand template '{title}' added successfully.")
        
    return redirect('system_admin:brand_templates')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def edit_brand_template(request, template_id):
    template = get_object_or_404(BrandTemplate, id=template_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category_id')
        
        if not title:
            messages.error(request, 'Title is required for a brand template.')
            return redirect('system_admin:brand_templates')
            
        template.title = title
        template.description = description
        
        if category_id:
            template.category_id = category_id
        else:
            template.category = None
            
        if 'thumbnail' in request.FILES:
            template.thumbnail = request.FILES['thumbnail']
            
        if 'file' in request.FILES:
            template.file = request.FILES['file']
            
        template.save()
        messages.success(request, f"Brand template '{title}' updated successfully.")
        
    return redirect('system_admin:brand_templates')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def asset_categories(request):
    categories = AssetCategory.objects.all().order_by('name')
    context = {
        'active_module': 'Asset Categories',
        'categories': categories,
    }
    return render(request, 'system_admin/asset_categories.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def add_asset_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if not name:
            messages.error(request, 'Category name is required.')
        elif AssetCategory.objects.filter(name=name).exists():
            messages.error(request, f'Category "{name}" already exists.')
        else:
            AssetCategory.objects.create(name=name, description=description)
            messages.success(request, f'Category "{name}" added successfully.')
            
    return redirect('system_admin:asset_categories')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def edit_asset_category(request, category_id):
    category = get_object_or_404(AssetCategory, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if not name:
            messages.error(request, 'Category name is required.')
        elif AssetCategory.objects.filter(name=name).exclude(id=category_id).exists():
            messages.error(request, f'Category "{name}" already exists.')
        else:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, f'Category "{name}" updated successfully.')
            
    return redirect('system_admin:asset_categories')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def delete_asset_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(AssetCategory, id=category_id)
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
    return redirect('system_admin:asset_categories')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def organization_management(request):
    organizations = Organization.objects.all().order_by('-created_at')
    context = {
        'organizations': organizations,
        'active_module': 'Organization Management'
    }
    return render(request, 'system_admin/organization_management.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def create_organization(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if Organization.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Organization "{name}" already exists.')
            else:
                Organization.objects.create(name=name, owner=request.user)
                messages.success(request, f'Organization "{name}" created successfully.')
    return redirect('system_admin:organizations')

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def role_permissions(request):
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    context = {
        'roles': roles,
        'permissions': permissions,
        'active_module': 'Roles & Permissions'
    }
    return render(request, 'system_admin/role_permissions.html', context)

@user_passes_test(is_admin, login_url='/accounts/admin-login/')
def create_role(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        if name:
            if Role.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Role "{name}" already exists.')
            else:
                Role.objects.create(name=name, description=description)
                messages.success(request, f'Role "{name}" created successfully.')


