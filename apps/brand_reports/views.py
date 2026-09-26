from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class BrandreportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'brand_reports/index.html'
