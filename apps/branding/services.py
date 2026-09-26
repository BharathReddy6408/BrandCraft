class BrandCompletionService:
    @staticmethod
    def calculate_completion(project):
        """
        Calculates a real completion score based on populated fields.
        Returns an integer percentage 0-100.
        """
        score = 0
        total_weight = 100
        
        # 1. Core Identity (20%)
        if project.business_name: score += 5
        if project.industry: score += 5
        if project.target_audience: score += 5
        if project.business_idea: score += 5
        
        # 2. Strategy (30%)
        if project.business_goal: score += 5
        if project.brand_mission: score += 5
        if project.brand_vision: score += 5
        if project.usp: score += 5
        if project.brand_values and len(project.brand_values) > 0: score += 5
        if project.keywords and len(project.keywords) > 0: score += 5
        
        # 3. Personality & Voice (20%)
        if project.brand_personality: score += 10
        if project.brand_voice: score += 10
        
        # 4. Visual Identity (30%)
        # Check assets if fields are not present
        has_color = project.primary_color and project.secondary_color
        has_font = project.heading_font and project.body_font
        has_logo = False
        
        if not has_color:
            has_color = project.assets.filter(asset_type='COLOR').exists()
        if not has_font:
            has_font = project.assets.filter(asset_type='TYPOGRAPHY').exists()
            
        has_logo = project.assets.filter(asset_type='LOGO', is_selected=True).exists()
            
        if project.preferred_style: score += 10
        if has_color: score += 5
        if has_font: score += 5
        if has_logo: score += 10
        
        return min(score, 100)
