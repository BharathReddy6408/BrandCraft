from django.urls import path
from . import views

app_name = 'brand_reports'

urlpatterns = [
    path('', views.BrandreportsDashboardView.as_view(), name='dashboard'),
]
