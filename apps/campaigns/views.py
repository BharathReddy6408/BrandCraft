from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class CampaignsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'campaigns/index.html'
