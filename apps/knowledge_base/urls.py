from django.urls import path
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    path('', views.KnowledgebaseDashboardView.as_view(), name='dashboard'),
]
