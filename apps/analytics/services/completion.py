from branding.models import BrandProject
from brand_assets.models import BrandAsset

class BrandCompletionService:
    @staticmethod
    def calculate_foundation(project: BrandProject) -> int:
        from django.core.cache import cache
        cache_key = f'brand_foundation_{project.pk}'
        # Bypass cache for real-time updates
        # cached_score = cache.get(cache_key)
        # if cached_score is not None:
        #     return cached_score
            
        score = 0
        
        if project.business_name: score += 10
        if project.business_idea: score += 10
        if project.industry: score += 10
        if project.target_audience: score += 10
        if project.brand_personality: score += 10
        if project.preferred_style: score += 10
        if project.business_goal: score += 5
        if project.usp: score += 5
        
        has_color = bool(project.primary_color)
        has_typography = bool(project.heading_font)
        has_slogan = BrandAsset.objects.filter(project=project, asset_type='SLOGAN').exists()
        has_logo = BrandAsset.objects.filter(project=project, asset_type='LOGO').exists()
        
        if has_color: score += 5
        if has_typography: score += 5
        if has_slogan: score += 10
        if has_logo: score += 10
        
        final_score = min(score, 100)
        # cache.set(cache_key, final_score, 3600)  # cache for 1 hour
        return final_score

    @staticmethod
    def calculate_activation(project: BrandProject) -> int:
        from django.core.cache import cache
        cache_key = f'brand_activation_{project.pk}'
        # Bypass cache for real-time updates
        # cached_score = cache.get(cache_key)
        # if cached_score is not None:
        #     return cached_score
            
        score = 0
        
        has_marketing = project.marketing_contents.exists() if hasattr(project, 'marketing_contents') else False
        has_social = project.social_posts.exists() if hasattr(project, 'social_posts') else False
        has_campaign = project.campaigns.exists() if hasattr(project, 'campaigns') else False
        has_creative = project.assets.filter(asset_type__in=['SOCIAL_GRAPHIC', 'AD_CREATIVE', 'POSTER', 'BANNER']).exists()
        
        if has_creative: score += 25
        if has_marketing: score += 25
        if has_social: score += 25
        if has_campaign: score += 25
        
        final_score = min(score, 100)
        # cache.set(cache_key, final_score, 3600)
        return final_score
        
    @staticmethod
    def calculate_completion(project: BrandProject) -> int:
        f_score = BrandCompletionService.calculate_foundation(project)
        a_score = BrandCompletionService.calculate_activation(project)
        return (f_score + a_score) // 2
