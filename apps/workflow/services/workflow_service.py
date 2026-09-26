from workflow.models import WorkflowState
from branding.models import BrandProject
from analytics.services.completion import BrandCompletionService

class WorkflowService:
    @staticmethod
    def get_or_create_state(project):
        state, created = WorkflowState.objects.get_or_create(project=project)
        return state

    @staticmethod
    def calculate_progress(project):
        # We reuse BrandCompletionService from analytics to get scores
        foundation = BrandCompletionService.calculate_foundation(project)
        activation = BrandCompletionService.calculate_activation(project)
        
        # Simple weighted average for workflow progress
        total = (foundation * 0.4) + (activation * 0.6)
        
        state = WorkflowService.get_or_create_state(project)
        state.completion_percentage = int(total)
        state.save()
        
        return state.completion_percentage

    @staticmethod
    def update_stage(project):
        """
        Calculates the current stage based on completed assets.
        """
        state = WorkflowService.get_or_create_state(project)
        
        # Check DNA
        has_dna = bool(project.business_name and project.brand_mission)
        # Check Logo
        has_logo = project.assets.filter(asset_type='LOGO').exists()
        # Check Identity
        has_identity = bool(project.primary_color and project.heading_font)
        # Check Creative
        has_creative = project.assets.filter(asset_type='CREATIVE').exists()
        # Check Marketing
        has_marketing = project.marketing_contents.exists()
        # Check Social
        has_social = project.social_posts.exists()
        # Check Campaign
        has_campaign = project.campaigns.exists()
        # Check Reports
        from brand_reports.models import BrandReport
        has_reports = BrandReport.objects.filter(project=project, report_type='EXECUTIVE').exists()
        # Check Kit
        from downloads.models import ExportRecord
        has_kit = ExportRecord.objects.filter(project=project, export_type='BRAND_KIT').exists()

        if has_kit:
            state.current_stage = 'LAUNCH'
        elif has_reports:
            state.current_stage = 'KIT'
        elif has_campaign:
            state.current_stage = 'REPORTS'
        elif has_social:
            state.current_stage = 'CAMPAIGN'
        elif has_marketing:
            state.current_stage = 'SOCIAL'
        elif has_creative:
            state.current_stage = 'MARKETING'
        elif has_identity:
            state.current_stage = 'CREATIVE'
        elif has_logo:
            state.current_stage = 'IDENTITY'
        elif has_dna:
            state.current_stage = 'LOGO'
        else:
            state.current_stage = 'DNA'
            
        state.save()
        return state
