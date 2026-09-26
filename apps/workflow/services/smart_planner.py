from workflow.models import PlannerRecommendation
from workflow.services.workflow_service import WorkflowService

class SmartPlannerService:
    @staticmethod
    def generate_recommendations(project):
        """
        Calculates the Next Best Action based on the workflow state and existing project data.
        """
        # Clear old active recommendations
        PlannerRecommendation.objects.filter(project=project, is_active=True).update(is_active=False)
        
        # Determine state
        state = WorkflowService.update_stage(project)
        stage = state.current_stage
        
        recommendations = []
        
        if stage == 'DNA':
            recommendations.append({
                'action_type': 'GENERATE_LOGO',
                'title': 'Generate Primary Logo',
                'description': 'Your brand DNA is set. Let\'s create a logo that embodies your mission.',
                'reason': 'A logo is required before establishing visual identity colors and fonts.',
                'priority': 1
            })
        elif stage == 'LOGO':
            recommendations.append({
                'action_type': 'GENERATE_IDENTITY',
                'title': 'Establish Brand Identity',
                'description': 'Extract colors and fonts from your new logo to build a design system.',
                'reason': 'A cohesive visual identity ensures consistency across all future assets.',
                'priority': 1
            })
        elif stage == 'IDENTITY':
            recommendations.append({
                'action_type': 'GENERATE_CREATIVE',
                'title': 'Generate Creative Assets',
                'description': 'Create branded visuals like banners and patterns.',
                'reason': 'These assets will be used in your upcoming marketing campaigns.',
                'priority': 1
            })
        elif stage == 'CREATIVE':
            recommendations.append({
                'action_type': 'GENERATE_MARKETING',
                'title': 'Write Marketing Copy',
                'description': 'Generate landing page copy and value propositions.',
                'reason': 'You need core marketing messages before launching social campaigns.',
                'priority': 1
            })
        elif stage == 'MARKETING':
            recommendations.append({
                'action_type': 'GENERATE_SOCIAL',
                'title': 'Create Social Posts',
                'description': 'Draft your first week of social media content.',
                'reason': 'Build audience anticipation before your main campaign launch.',
                'priority': 1
            })
        elif stage == 'SOCIAL':
            recommendations.append({
                'action_type': 'GENERATE_CAMPAIGN',
                'title': 'Launch Campaign',
                'description': 'Generate a full 30-day cross-platform marketing campaign.',
                'reason': 'All individual assets are ready to be combined into a structured campaign.',
                'priority': 1
            })
        elif stage == 'CAMPAIGN':
            recommendations.append({
                'action_type': 'GENERATE_REPORTS',
                'title': 'Generate Executive Report',
                'description': 'Compile your strategy, identity, and campaign into a master PDF.',
                'reason': 'Required for stakeholder alignment and final review.',
                'priority': 1
            })
        elif stage == 'REPORTS':
            recommendations.append({
                'action_type': 'EXPORT_KIT',
                'title': 'Export Brand Kit',
                'description': 'Download your complete brand package as a ZIP file.',
                'reason': 'You are ready to hand off assets to your team or agency.',
                'priority': 1
            })
        else:
            recommendations.append({
                'action_type': 'REVIEW_HEALTH',
                'title': 'Review Brand Health',
                'description': 'Your core brand setup is complete. Monitor your health and consistency.',
                'reason': 'Continuous monitoring ensures your brand stays relevant.',
                'priority': 1
            })

        # Save new recommendations
        for rec in recommendations:
            PlannerRecommendation.objects.create(
                project=project,
                action_type=rec['action_type'],
                title=rec['title'],
                description=rec['description'],
                reason=rec['reason'],
                priority=rec['priority'],
                is_active=True
            )
            
        return PlannerRecommendation.objects.filter(project=project, is_active=True)
