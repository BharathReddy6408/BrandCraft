from analytics.models import BrandRecommendation, BrandAudit
from branding.models import BrandProject
from brand_assets.models import BrandAsset

class BrandRecommendationService:
    @staticmethod
    def generate_recommendations(project: BrandProject, user):
        """
        Generates deterministic recommendations and merges with AI priority actions.
        Saves them to BrandRecommendation.
        """
        # Clear previous unresolved recommendations to keep it fresh
        BrandRecommendation.objects.filter(project=project, is_dismissed=False).delete()
        
        recs = []
        
        # 1. Deterministic Checks
        if not project.business_name:
            recs.append(BrandRecommendation(
                project=project, user=user, priority='HIGH',
                title="Define Business Name",
                reason="Your brand needs a core identity before generating assets.",
                module_destination="name_slogan_studio"
            ))
            
        if not BrandAsset.objects.filter(project=project, asset_type='LOGO').exists():
            recs.append(BrandRecommendation(
                project=project, user=user, priority='HIGH',
                title="Create Primary Logo",
                reason="A logo is required for almost all marketing materials and campaigns.",
                module_destination="logo_studio"
            ))
            
        if not project.marketing_contents.exists():
            recs.append(BrandRecommendation(
                project=project, user=user, priority='MEDIUM',
                title="Generate Initial Marketing Copy",
                reason="Kickstart your marketing with SEO and landing page copy.",
                module_destination="marketing_studio"
            ))
            
        if not project.campaigns.exists():
            recs.append(BrandRecommendation(
                project=project, user=user, priority='LOW',
                title="Launch a Campaign",
                reason="You have the assets ready. Time to plan a multi-day social campaign.",
                module_destination="campaign_studio"
            ))
            
        # 2. AI Driven Checks from latest Audit
        latest_audit = BrandAudit.objects.filter(project=project).order_by('-created_at').first()
        if latest_audit and latest_audit.priority_actions:
            for action in latest_audit.priority_actions:
                if isinstance(action, dict):
                    recs.append(BrandRecommendation(
                        project=project, user=user, 
                        priority=action.get('priority', 'MEDIUM').upper(),
                        title=action.get('title', 'AI Recommendation'),
                        reason=action.get('reason', 'Suggested by Brand QA Agent'),
                        module_destination="analytics"
                    ))
                    
        # Bulk Create
        if recs:
            BrandRecommendation.objects.bulk_create(recs)
            
        return BrandRecommendation.objects.filter(project=project, is_dismissed=False).order_by('priority')
