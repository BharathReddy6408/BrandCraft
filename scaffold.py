import os

apps = ['marketing', 'socialmedia', 'campaigns', 'brand_assets', 'brand_reports', 'knowledge_base', 'billing', 'preferences']
base_dir = os.path.dirname(os.path.abspath(__file__))

for app in apps:
    app_dir = os.path.join(base_dir, 'apps', app)
    template_dir = os.path.join(base_dir, 'templates', app)
    
    # 1. Create urls.py
    urls_content = f"""from django.urls import path
from . import views

app_name = '{app}'

urlpatterns = [
    path('', views.{app.replace('_', '').capitalize()}DashboardView.as_view(), name='dashboard'),
]
"""
    with open(os.path.join(app_dir, 'urls.py'), 'w', encoding='utf-8') as f:
        f.write(urls_content)
        
    # 2. Update views.py
    views_content = f"""from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class {app.replace('_', '').capitalize()}DashboardView(LoginRequiredMixin, TemplateView):
    template_name = '{app}/index.html'
"""
    with open(os.path.join(app_dir, 'views.py'), 'w', encoding='utf-8') as f:
        f.write(views_content)
        
    # 3. Create basic template
    os.makedirs(template_dir, exist_ok=True)
    html_content = f"""{{% extends 'base.html' %}}

{{% block title %}}{app.replace('_', ' ').title()} | BrandCraft{{% endblock %}}

{{% block content %}}
<div class="container mt-5">
    <h1>{app.replace('_', ' ').title()} Dashboard</h1>
    <p>This module is currently being scaffolded.</p>
</div>
{{% endblock %}}
"""
    with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

print('Scaffolding complete!')
