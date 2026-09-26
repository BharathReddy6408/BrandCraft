from django.urls import path
from . import views

app_name = 'branding'

urlpatterns = [
    path('create/', views.create_project_wizard, name='create_project'),
    path('project/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:pk>/generating/', views.generating, name='generating'),
    path('project/<int:pk>/results/', views.results, name='results'),
    
    # Project Scoped Workspace Hub
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/identity/', views.project_identity, name='brand_identity'),
    path('project/<int:pk>/names/', views.name_slogan_studio, name='name_slogan_studio'),
    path('project/<int:pk>/logos/', views.logo_studio, name='logo_studio'),
    path('project/<int:pk>/creative/', views.creative_studio, name='creative_studio'),
    path('project/<int:pk>/marketing/', views.marketing_studio, name='marketing_studio'),
    path('project/<int:pk>/social/', views.social_studio, name='social_studio'),
    path('project/<int:pk>/campaigns/', views.campaign_studio, name='campaign_studio'),
    path('project/<int:pk>/analytics/', views.project_analytics, name='analytics'),
    path('project/<int:pk>/reports/', views.project_reports, name='reports'),
    path('project/<int:pk>/downloads/', views.project_downloads, name='downloads'),
    path('project/<int:pk>/history/', views.project_history, name='history'),
    path('project/<int:pk>/settings/', views.project_settings, name='settings'),
    path('project/<int:pk>/chat-api/', views.project_chat_api, name='chat_api'),
    path('project/<int:pk>/audit/', views.run_brand_audit, name='run_brand_audit'),
    
    # Reports & Downloads Endpoints
    path('project/<int:pk>/generate-report/', views.generate_report, name='generate_report'),
    path('project/<int:pk>/generate-guidelines/', views.generate_guidelines, name='generate_guidelines'),
    path('project/<int:pk>/export-package/', views.export_brand_package, name='export_package'),
    path('project/<int:pk>/download/<str:file_type>/<int:file_id>/', views.download_file, name='download_file'),
    path('project/<int:pk>/presentation/', views.project_presentation, name='presentation_mode'),
    
    path('project/<int:pk>/generate-names/', views.generate_names, name='generate_names'),
]
