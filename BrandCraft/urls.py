from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def favicon_view(request):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">✨</text></svg>'
    return HttpResponse(svg, content_type='image/svg+xml')

urlpatterns = [
    path('favicon.ico', favicon_view),
    path('admin/', admin.site.urls),
    path('portal/', include('system_admin.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('workflow/', include('workflow.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('branding/', include('branding.urls')),
    path('creative/', include('creative.urls')),
    path('marketing/', include('marketing.urls')),
    path('socialmedia/', include('socialmedia.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('assets/', include('brand_assets.urls')),
    path('reports/', include('brand_reports.urls')),
    path('knowledge/', include('knowledge_base.urls')),
    path('billing/', include('billing.urls')),
    path('preferences/', include('preferences.urls')),
    path('api/', include('api.urls')),
    path('', include('website.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
