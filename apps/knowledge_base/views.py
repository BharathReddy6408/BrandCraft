from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class KnowledgebaseDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'knowledge_base/index.html'
