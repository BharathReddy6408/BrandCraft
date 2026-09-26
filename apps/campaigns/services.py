from ai_services.services import AIService
from campaigns.models import Campaign, CampaignItem

class CampaignAgent:
    def generate_campaign(self, project_id, name, goal, duration, platforms):
        prompt = f"Create a marketing campaign for {name}. Goal: {goal}. Duration: {duration} days. Platforms: {platforms}. Return JSON with 'strategy' (string), 'audience_focus' (string), 'content_pillars' (list of strings), and 'timeline' (list of objects with 'day', 'platform', 'content_type', 'topic', 'objective')."
        return AIService.generate_structured(prompt)

class CampaignGenerationService:
    @staticmethod
    def generate(user, project, name, goal, duration, platforms):
        agent = CampaignAgent()
        
        result = agent.generate_campaign(
            project_id=project.id,
            name=name,
            goal=goal,
            duration=duration,
            platforms=platforms
        )
        
        if not result or 'strategy' not in result:
            platform = platforms[0] if platforms else 'Instagram'
            try:
                days = int(duration)
            except (ValueError, TypeError):
                days = 7
            result = {
                'strategy': f'{goal} campaign for {name} over {days} days using {", ".join(platforms) if platforms else "social media"}.',
                'audience_focus': f'Target audience interested in {name}.',
                'content_pillars': ['Educational', 'Entertaining', 'Promotional'],
                'timeline': [
                    {'day': d + 1, 'platform': platform,
                     'content_type': ['Post', 'Story', 'Reel', 'Carousel', 'Poll'][d % 5],
                     'topic': f'Day {d + 1}: {goal} Content',
                     'objective': goal}
                    for d in range(min(days, 14))
                ]
            }

        if result:
            campaign = Campaign.objects.create(
                user=user,
                project=project,
                name=name[:255],
                goal=goal[:255],
                duration=str(duration),
                platforms=platforms,
                strategy=result.get('strategy', ''),
                audience_focus=result.get('audience_focus', ''),
                content_pillars=result.get('content_pillars', []),
                status='GENERATED'
            )
            
            # Create Timeline Items
            timeline = result.get('timeline', [])
            for item in timeline:
                CampaignItem.objects.create(
                    campaign=campaign,
                    scheduled_day=item.get('day', 1),
                    platform=item.get('platform', '')[:50],
                    content_type=item.get('content_type', '')[:100],
                    topic=item.get('topic', '')[:255],
                    objective=item.get('objective', '')[:255],
                    status='PLANNED'
                )
                
            return campaign
        return None
