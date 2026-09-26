from branding.models import BrandProject
from ai_services.context import BrandContextService
from ai_services.services import AIService
from analytics.models import BrandAudit

class ReportDataService:
    @staticmethod
    def _get_base_context(project: BrandProject):
        return BrandContextService.build_context(project)

    @staticmethod
    def collect_strategy_data(project: BrandProject):
        context = ReportDataService._get_base_context(project)
        
        prompt = f"""
        Based on this brand strategy:
        Name: {context.get('business_name')}
        Mission: {context.get('mission')}
        Vision: {context.get('vision')}
        USP: {context.get('usp')}
        Target Audience: {context.get('target_audience')}
        
        Write a professional 2-paragraph narrative summarizing the strategic positioning of this brand.
        Return ONLY valid JSON: {{"narrative": "..."}}
        """
        try:
            import json
            response = AIService.generate_text(prompt, "You are a Brand Strategist. Output only valid JSON.")
            parsed = json.loads(response)
            ai_narrative = parsed.get("narrative", "")
        except:
            ai_narrative = f"{context.get('business_name')} is strategically positioned to serve {context.get('target_audience')} through its unique offering."

        return {
            'overview': {
                'name': context.get('business_name'),
                'industry': context.get('industry'),
                'target_audience': context.get('target_audience'),
                'business_goal': context.get('business_goal'),
            },
            'dna': {
                'mission': context.get('mission'),
                'vision': context.get('vision'),
                'values': context.get('values', []),
                'usp': context.get('usp'),
                'personality': context.get('brand_personality'),
                'voice': context.get('voice'),
                'keywords': context.get('keywords', []),
                'slogan': context.get('selected_slogan'),
            },
            'ai_narrative': ai_narrative
        }

    @staticmethod
    def collect_identity_data(project: BrandProject):
        context = ReportDataService._get_base_context(project)
        logo = project.assets.filter(asset_type='LOGO').first()
        logo_url = logo.file_upload.url if logo and logo.file_upload else None
        
        prompt = f"""
        Based on this brand identity:
        Name: {context.get('business_name')}
        Personality: {context.get('brand_personality')}
        Colors: {context.get('colors', {})}
        Typography: {context.get('typography', {})}
        
        Write a professional 1-2 paragraph narrative explaining how this visual identity supports the brand's personality.
        Return ONLY valid JSON: {{"narrative": "..."}}
        """
        try:
            import json
            response = AIService.generate_text(prompt, "You are a Brand Designer. Output only valid JSON.")
            parsed = json.loads(response)
            ai_narrative = parsed.get("narrative", "")
        except:
            ai_narrative = f"The visual identity of {context.get('business_name')} is designed to reflect its {context.get('brand_personality')} personality."

        return {
            'logo_url': logo_url,
            'primary_color': project.primary_color,
            'slogan': context.get('selected_slogan'),
            'colors': context.get('colors', {}),
            'typography': context.get('typography', {}),
            'personality': context.get('brand_personality'),
            'ai_narrative': ai_narrative
        }

    @staticmethod
    def collect_audit_data(project: BrandProject):
        audit = BrandAudit.objects.filter(project=project).order_by('-created_at').first()
        if not audit:
            return None
            
        prompt = f"""
        Based on these brand audit results for {project.business_name}:
        Overall Score: {audit.overall_score}
        Strengths: {audit.strengths}
        Weaknesses: {audit.weaknesses}
        Priority Actions: {audit.priority_actions}
        
        Write a professional 2-paragraph executive narrative summarizing the audit findings and recommended path forward.
        Return ONLY valid JSON: {{"narrative": "..."}}
        """
        try:
            import json
            response = AIService.generate_text(prompt, "You are a Brand Auditor. Output only valid JSON.")
            parsed = json.loads(response)
            ai_narrative = parsed.get("narrative", "")
        except:
            ai_narrative = f"The audit for {project.business_name} reveals an overall score of {audit.overall_score}%. Priority actions include addressing key weaknesses to improve brand consistency."

        return {
            'audit_date': audit.created_at.isoformat(),
            'foundation_score': audit.foundation_score,
            'activation_score': audit.activation_score,
            'readiness_score': audit.campaign_readiness_score,
            'consistency_score': audit.consistency_score,
            'overall_score': audit.overall_score,
            'summary': audit.summary,
            'strengths': audit.strengths,
            'weaknesses': audit.weaknesses,
            'opportunities': audit.opportunities,
            'priority_actions': audit.priority_actions,
            'ai_narrative': ai_narrative
        }

    @staticmethod
    def collect_campaign_data(campaign):
        return {
            'name': campaign.name,
            'objective': campaign.objective,
            'target_audience': campaign.target_audience,
            'duration': campaign.duration_days,
            'platforms': campaign.platforms,
            'status': campaign.status,
            'strategy': campaign.strategy_text,
            'pillars': campaign.content_pillars,
        }

    @staticmethod
    def collect_executive_data(project: BrandProject):
        strategy = ReportDataService.collect_strategy_data(project)
        identity = ReportDataService.collect_identity_data(project)
        audit = ReportDataService.collect_audit_data(project)
        
        # Aggregate stats
        marketing_count = project.marketing_contents.count()
        social_count = project.social_posts.count()
        campaign_count = project.campaigns.count()
        creative_count = project.assets.filter(asset_type='CREATIVE').count()
        
        # Get AI Executive Summary
        system_msg = "You are a Brand Strategist. Output only valid JSON."
        prompt = f"""
        Based on this brand context:
        Name: {strategy['overview']['name']}
        Mission: {strategy['dna']['mission']}
        USP: {strategy['dna']['usp']}
        
        And this activity:
        Marketing Content: {marketing_count}
        Social Posts: {social_count}
        Campaigns: {campaign_count}
        Creative Assets: {creative_count}
        
        Audit Overall Score: {audit['overall_score'] if audit else 'N/A'}%
        
        Write a concise, 2-3 paragraph executive summary of the brand's current state and strategy.
        Return ONLY valid JSON: {{"executive_summary": "..."}}
        """
        
        try:
            import json
            response = AIService.generate_text(prompt, system_msg)
            parsed = json.loads(response)
            summary = parsed.get("executive_summary", "")
        except:
            summary = "Executive summary could not be generated."

        return {
            'strategy': strategy,
            'identity': identity,
            'audit': audit,
            'stats': {
                'marketing_count': marketing_count,
                'social_count': social_count,
                'campaign_count': campaign_count,
                'creative_count': creative_count,
            },
            'executive_summary': summary
        }
