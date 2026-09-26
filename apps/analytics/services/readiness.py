from branding.models import BrandProject
from brand_assets.models import BrandAsset

class CampaignReadinessService:
    @staticmethod
    def evaluate(project: BrandProject) -> dict:
        """
        Evaluates if the brand is ready for a marketing campaign.
        Returns a dictionary with score, ready criteria, missing criteria, and recommendations.
        """
        checks = [
            {'id': 'audience', 'name': 'Target Audience Defined', 'passed': bool(project.target_audience)},
            {'id': 'voice', 'name': 'Brand Voice Established', 'passed': bool(project.brand_personality)},
            {'id': 'logo', 'name': 'Primary Logo Selected', 'passed': BrandAsset.objects.filter(project=project, asset_type='LOGO').exists()},
            {'id': 'palette', 'name': 'Color Palette Defined', 'passed': BrandAsset.objects.filter(project=project, asset_type='COLOR').exists()},
            {'id': 'marketing', 'name': 'Marketing Copy Available', 'passed': project.marketing_contents.exists()},
        ]
        
        passed_checks = [c for c in checks if c['passed']]
        failed_checks = [c for c in checks if not c['passed']]
        
        score = int((len(passed_checks) / len(checks)) * 100) if checks else 0
        
        return {
            'score': score,
            'ready_items': [c['name'] for c in passed_checks],
            'missing_items': [c['name'] for c in failed_checks],
            'is_ready': score >= 80
        }
