from django.urls import path
from . import views

app_name = 'creative'

urlpatterns = [
    path('', views.studio_dashboard, name='dashboard'),
]
