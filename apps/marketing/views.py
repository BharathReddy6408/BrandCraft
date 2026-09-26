from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class MarketingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'marketing/index.html'
