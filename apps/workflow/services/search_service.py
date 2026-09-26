from branding.models import BrandProject
from brand_assets.models import BrandAsset
from marketing.models import MarketingContent
from campaigns.models import Campaign
from brand_reports.models import BrandReport
from django.db.models import Q

class SearchService:
    @staticmethod
    def universal_search(user, query):
        """
        Searches across projects, assets, campaigns, marketing, and reports.
        """
        results = []
        
        # 1. Projects
        projects = BrandProject.objects.filter(
            Q(user=user) & 
            (Q(business_name__icontains=query) | Q(business_idea__icontains=query) | Q(industry__icontains=query))
        )[:5]
        for p in projects:
            results.append({
                'type': 'Project',
                'title': p.business_name,
                'subtitle': p.industry,
                'url': f"/branding/project/{p.id}/"
            })
            
        # 2. Campaigns
        campaigns = Campaign.objects.filter(
            Q(project__user=user) & 
            (Q(name__icontains=query) | Q(objective__icontains=query))
        )[:5]
        for c in campaigns:
            results.append({
                'type': 'Campaign',
                'title': c.name,
                'subtitle': f"Project: {c.project.business_name}",
                'url': f"/branding/project/{c.project.id}/campaigns/"
            })
            
        # 3. Assets
        assets = BrandAsset.objects.filter(
            Q(project__user=user) & 
            Q(asset_type__icontains=query)
        )[:5]
        for a in assets:
            results.append({
                'type': 'Asset',
                'title': f"{a.get_asset_type_display()} Asset",
                'subtitle': f"Project: {a.project.business_name}",
                'url': f"/branding/project/{a.project.id}/identity/" if a.asset_type == 'LOGO' else f"/branding/project/{a.project.id}/creative/"
            })
            
        # 4. Reports
        reports = BrandReport.objects.filter(
            Q(user=user) & 
            (Q(title__icontains=query) | Q(report_type__icontains=query))
        )[:5]
        for r in reports:
            results.append({
                'type': 'Report',
                'title': r.title,
                'subtitle': f"Version {r.version}",
                'url': f"/branding/project/{r.project.id}/reports/"
            })
            
        return results
