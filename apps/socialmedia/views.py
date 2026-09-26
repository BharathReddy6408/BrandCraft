from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class SocialmediaDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'socialmedia/index.html'
