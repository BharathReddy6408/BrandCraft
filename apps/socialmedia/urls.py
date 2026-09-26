from django.urls import path
from . import views

app_name = 'socialmedia'

urlpatterns = [
    path('', views.SocialmediaDashboardView.as_view(), name='dashboard'),
]
