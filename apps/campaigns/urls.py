from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.CampaignsDashboardView.as_view(), name='dashboard'),
]
