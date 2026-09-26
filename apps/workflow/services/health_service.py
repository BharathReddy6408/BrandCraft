from analytics.models import BrandAudit
from analytics.services.completion import BrandCompletionService
from workflow.services.workflow_service import WorkflowService

class BrandHealthService:
    @staticmethod
    def calculate_health(project):
        """
        Combines completion score, latest audit scores, and workflow progress
        into a single unified Brand Health percentage.
        """
        foundation = BrandCompletionService.calculate_foundation(project)
        activation = BrandCompletionService.calculate_activation(project)
        workflow_progress = WorkflowService.calculate_progress(project)
        
        audit = BrandAudit.objects.filter(project=project).order_by('-created_at').first()
        audit_score = audit.overall_score if audit else 0
        
        # If no audit exists, weight the others heavier
        if audit_score == 0:
            health = int((foundation * 0.4) + (activation * 0.2) + (workflow_progress * 0.4))
        else:
            health = int((foundation * 0.3) + (activation * 0.2) + (workflow_progress * 0.2) + (audit_score * 0.3))
            
        return {
            'health_score': health,
            'foundation': foundation,
            'activation': activation,
            'workflow': workflow_progress,
            'audit': audit_score
        }
