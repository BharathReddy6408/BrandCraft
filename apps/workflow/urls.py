from django.urls import path
from . import views

app_name = 'workflow'

urlpatterns = [
    # Global Universal Search
    path('search/', views.universal_search, name='search'),
    
    # Project Scoped Workspace Hub
    path('project/<int:pk>/workspace/', views.workspace_dashboard, name='dashboard'),
    path('project/<int:pk>/queue/', views.content_queue, name='queue'),
    path('project/<int:pk>/calendar/', views.brand_calendar, name='calendar'),
    path('project/<int:pk>/queue/<int:item_id>/action/', views.approval_action, name='approval_action'),
]
