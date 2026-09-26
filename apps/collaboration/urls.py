from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    # Project-specific collaboration routes
    path('project/<int:pk>/hub/', views.brand_hub, name='brand_hub'),
    path('project/<int:pk>/team/', views.team_management, name='team_management'),
    path('project/<int:pk>/tasks/api/', views.tasks_api, name='tasks_api'),
    
    # Global sharing routes
    path('invite/accept/<uuid:token>/', views.accept_invitation, name='accept_invitation'),
    path('share/<uuid:token>/', views.client_presentation, name='client_presentation'),
]
