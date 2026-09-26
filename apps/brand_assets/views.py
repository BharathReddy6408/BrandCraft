from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class BrandassetsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'brand_assets/index.html'
