from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class PreferencesDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'preferences/index.html'
