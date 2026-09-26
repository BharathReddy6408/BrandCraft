from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def studio_dashboard(request):
    """
    Central workspace showing all generated assets across the user's projects.
    """
    from brand_assets.models import BrandAsset
    
    asset_type = request.GET.get('type')
    project_id = request.GET.get('project')
    
    assets = BrandAsset.objects.filter(user=request.user).order_by('-created_at')
    
    if asset_type:
        assets = assets.filter(asset_type=asset_type)
        
    if project_id:
        assets = assets.filter(project_id=project_id)
        
    # Get distinct projects for filter
    projects = request.user.brand_projects.all()
    
    # Asset type choices for filter
    asset_types = BrandAsset.ASSET_TYPES
        
    return render(request, 'creative/dashboard.html', {
        'assets': assets,
        'projects': projects,
        'asset_types': asset_types,
        'current_type': asset_type,
        'current_project': int(project_id) if project_id else None
    })
