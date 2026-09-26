from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('features/', views.features_page, name='features'),
]
