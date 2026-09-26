from django.urls import path
from . import views

app_name = 'brand_assets'

urlpatterns = [
    path('', views.BrandassetsDashboardView.as_view(), name='dashboard'),
]
