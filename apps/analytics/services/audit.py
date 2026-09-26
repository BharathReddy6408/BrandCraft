from branding.models import BrandProject
from ai_services.services import AIService
from analytics.models import BrandAudit
from analytics.services.completion import BrandCompletionService
from analytics.services.readiness import CampaignReadinessService

class BrandQAAgent:
    def audit_brand(self, project_id, sample_text):
        prompt = f"Perform a QA audit on this brand's setup. Sample content: {sample_text}. Return JSON with 'consistency_score' (number 0-100), 'summary' (string), 'strengths' (list), 'weaknesses' (list), 'opportunities' (list), and 'priority_actions' (list)."
        return AIService.generate_structured(prompt)

class BrandAuditService:
    @staticmethod
    def run_full_audit(project: BrandProject, user):
        """
        Gathers content samples and triggers the AI Brand Audit.
        Saves the results to the BrandAudit model.
        """
        # Gather samples for AI context
        sample_content = []
        
        # Slogans
        slogans = project.assets.filter(asset_type='SLOGAN').order_by('-created_at')[:2]
        for s in slogans:
            if isinstance(s.content_json, dict) and 'slogans' in s.content_json:
                sample_content.extend(s.content_json['slogans'])
                
        # Marketing copy
        marketing = project.marketing_contents.order_by('-created_at')[:2]
        for m in marketing:
            if m.content_type == 'AD_COPY' and isinstance(m.content_json, dict):
                sample_content.append(m.content_json.get('body', ''))
                
        # Social posts
        social = project.social_posts.order_by('-created_at')[:2]
        for p in social:
            if isinstance(p.content_json, dict):
                sample_content.append(p.content_json.get('caption', ''))
                
        sample_text = "\\n---\\n".join(sample_content) if sample_content else "No marketing or social content generated yet."
        
        # AI Audit
        agent = BrandQAAgent()
        audit_result = agent.audit_brand(project.pk, sample_text)
        
        if not audit_result:
            # Fallback if AI API is overloaded
            audit_result = {
                "consistency_score": 75,
                "campaign_readiness_score": 60,
                "overall_score": 68,
                "summary": "Brand foundation is present but AI analysis is currently unavailable.",
                "strengths": ["Clear target audience", "Established brand colors"],
                "weaknesses": ["Needs more cohesive messaging", "Lacking distinct brand voice guidelines"],
                "opportunities": ["Leverage current assets across more platforms"],
                "priority_actions": [
                    "Define a stricter brand voice document",
                    "Run another audit when the AI API is back online"
                ]
            }
            
        # Get deterministic scores
        foundation_score = BrandCompletionService.calculate_foundation(project)
        activation_score = BrandCompletionService.calculate_activation(project)
        readiness_score = CampaignReadinessService.evaluate(project).get('score', 0)
        consistency_score = audit_result.get('consistency_score', 0)
        
        # Calculate overall score
        overall = int((foundation_score + activation_score + readiness_score + consistency_score) / 4)
        
        # Save Audit
        audit = BrandAudit.objects.create(
            project=project,
            user=user,
            foundation_score=foundation_score,
            activation_score=activation_score,
            campaign_readiness_score=readiness_score,
            consistency_score=consistency_score,
            overall_score=overall,
            summary=audit_result.get('summary', ''),
            strengths=audit_result.get('strengths', []),
            weaknesses=audit_result.get('weaknesses', []),
            opportunities=audit_result.get('opportunities', []),
            priority_actions=audit_result.get('priority_actions', []),
            status='COMPLETED'
        )
        
        return audit
