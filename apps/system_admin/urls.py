from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'system_admin'

urlpatterns = [
    # Root redirect
    path('', RedirectView.as_view(pattern_name='system_admin:dashboard', permanent=False)),

    # Overview
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('analytics/', views.analytics_center, name='analytics'),
    path('reports/', views.reports_management, name='reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    
    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('organizations/', views.organization_management, name='organizations'),
    path('organizations/create/', views.create_organization, name='create_organization'),

    path('roles/', views.role_permissions, name='roles'),
    path('roles/create/', views.create_role, name='create_role'),
    path('subscriptions/', views.subscription_billing, name='subscriptions'),
    path('subscriptions/plan/<int:plan_id>/update/', views.update_subscription_plan, name='update_subscription_plan'),
    path('subscriptions/user/<int:user_sub_id>/manage/', views.manage_subscription, name='manage_subscription'),
    
    # AI & Content
    path('ai-generations/', views.ai_generations, name='ai_generations'),
    path('ai-generations/<int:asset_id>/approve-generation/', views.approve_generation, name='approve_generation'),
    path('ai-generations/<int:asset_id>/reject-generation/', views.reject_generation, name='reject_generation'),
    
    path('assets/', views.asset_management, name='assets'),
    path('brand-templates/', views.brand_templates, name='brand_templates'),
    path('brand-templates/add/', views.add_brand_template, name='add_brand_template'),
    path('brand-templates/<int:template_id>/edit/', views.edit_brand_template, name='edit_brand_template'),
    path('assets/<int:asset_id>/approve/', views.approve_asset, name='approve_asset'),
    path('assets/<int:asset_id>/flag/', views.flag_asset, name='flag_asset'),
    path('assets/<int:asset_id>/delete/', views.delete_asset, name='delete_asset'),
    
    path('asset-categories/', views.asset_categories, name='asset_categories'),
    path('asset-categories/add/', views.add_asset_category, name='add_asset_category'),
    path('asset-categories/<int:category_id>/edit/', views.edit_asset_category, name='edit_asset_category'),
    path('asset-categories/<int:category_id>/delete/', views.delete_asset_category, name='delete_asset_category'),
    
    path('models/', views.model_management, name='models'),
    path('models/add/', views.add_model, name='add_model'),
    path('models/<int:model_id>/remove/', views.remove_model, name='remove_model'),
    path('models/<int:model_id>/configure/', views.configure_model, name='configure_model'),
    
    path('fine-tuning/', views.fine_tuning_dashboard, name='fine_tuning'),
    path('fine-tuning/dataset/upload/', views.upload_dataset, name='upload_dataset'),
    path('fine-tuning/dataset/<int:dataset_id>/preprocess/', views.preprocess_dataset, name='preprocess_dataset'),
    path('fine-tuning/train/start/', views.start_training, name='start_training'),
    path('fine-tuning/train/<int:job_id>/complete/', views.complete_mock_training, name='complete_mock_training'),
    path('knowledge-base/', views.knowledge_base, name='knowledge_base'),
    path('knowledge-base/upload/', views.upload_document, name='upload_document'),
    path('knowledge-base/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    path('prompts/', views.prompt_library, name='prompts'),
    path('prompts/create/', views.create_prompt, name='create_prompt'),
    path('prompts/<int:prompt_id>/update/', views.update_prompt, name='update_prompt'),
    path('prompts/<int:prompt_id>/test/', views.test_prompt, name='test_prompt'),
    path('moderation/', views.content_moderation, name='moderation'),
    
    # System
    path('security/', views.security_center, name='security'),
    path('monitoring/', views.system_monitoring, name='monitoring'),
    path('settings/', views.platform_settings, name='settings'),
    path('settings/save/', views.save_settings, name='save_settings'),
    
    # Legacy URL Redirect (Catch-all for bookmarks)
    path('module/<str:module_name>/', views.legacy_redirect, name='placeholder'),
]
