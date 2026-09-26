from ai_services.services import AIService
from socialmedia.models import SocialPost

class SocialMediaAgent:
    def generate_post(self, project_id, platform, goal, topic, message, style):
        prompt = f"Create a social media post for {platform}. Goal: {goal}. Topic: {topic}. Message: {message}. Style: {style}. Return JSON with 'caption' (string), 'hashtags' (list of strings), and 'image_prompt' (string describing an ideal accompanying photo or graphic)."
        return AIService.generate_structured(prompt)

class SocialGenerationService:
    @staticmethod
    def generate(user, project, platform, **kwargs):
        agent = SocialMediaAgent()
        
        result = agent.generate_post(
            project_id=project.id,
            platform=platform,
            goal=kwargs.get('goal', ''),
            topic=kwargs.get('topic', ''),
            message=kwargs.get('message', ''),
            style=kwargs.get('style', '')
        )
        if not result or 'caption' not in result:
            result = {
                'caption': f"Check out our latest update on {kwargs.get('topic', 'our business')}! {kwargs.get('message', '')} #update #business",
                'hashtags': ['update', 'business', 'news'],
                'image_prompt': f"A high quality professional photo illustrating {kwargs.get('topic', 'our business')}."
            }
        if result:
            title = kwargs.get('topic') or 'Social Post'
            safe_platform = (platform or 'INSTAGRAM').upper()
            safe_tags = result.get('hashtags') or []
            if isinstance(safe_tags, str):
                safe_tags = [safe_tags]
            elif not isinstance(safe_tags, list):
                safe_tags = []
                
            post = SocialPost.objects.create(
                user=user,
                project=project,
                platform=safe_platform,
                title=title[:255],
                content_json=result,
                caption=result.get('caption', ''),
                hashtags=', '.join(safe_tags),
                status='GENERATED',
                prompt_metadata=kwargs
            )
            return post
        return None
