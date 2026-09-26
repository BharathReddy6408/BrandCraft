from django.urls import path
from . import views

app_name = 'preferences'

urlpatterns = [
    path('', views.PreferencesDashboardView.as_view(), name='dashboard'),
]
