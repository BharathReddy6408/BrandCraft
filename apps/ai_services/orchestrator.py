import json
from ai_services.models import ChatConversation, ChatMessage
from ai_services.context import BrandContextService
from ai_services.services import AIService
from ai_services.intent import IntentDetector
from ai_services.module_registry import MODULE_REGISTRY
from ai_services.tools import CopilotTools
from ai_services.agents import BrandStrategistAgent, BrandModificationAgent
from django.urls import reverse

class CopilotOrchestrator:
    @staticmethod
    def process_message(user, project, message_content: str, conversation_id: int = None):
        """Main entry point for the AI Copilot."""
        # 1. Get or Create Conversation
        if conversation_id:
            try:
                conversation = ChatConversation.objects.get(id=conversation_id, user=user, brand_project=project)
            except ChatConversation.DoesNotExist:
                return {"success": False, "error": "Conversation not found"}
        else:
            conversation = ChatConversation.objects.create(
                user=user, 
                brand_project=project,
                title="New Conversation"
            )

        ChatMessage.objects.create(conversation=conversation, role='user', content=message_content)

        # 2. Extract context if missing in project
        if not project.business_name or not project.industry:
            extracted = BrandContextService.extract_from_message(message_content)
            project.business_name = extracted.get('business_name', project.business_name)
            project.industry = extracted.get('industry', project.industry)
            project.save()

        # 3. Detect Intent
        intent_data = IntentDetector.detect_intent(message_content)
        intent = intent_data.get('intent', 'GENERAL_BRAND_CHAT')
        module = intent_data.get('module')
        asset_type = intent_data.get('asset_type')
        
        actions = []
        response_type = "text"
        structured_content = {}
        response_text = ""

        # 4. Determine Links
        if module and module in MODULE_REGISTRY:
            try:
                route_name = MODULE_REGISTRY[module]["route"]
                url = reverse(route_name, kwargs={"pk": project.id})
                actions.append({
                    "type": "navigate",
                    "label": f"Open {module.replace('_', ' ').title()}",
                    "url": url
                })
            except Exception:
                pass

        # 5. Route & Execute
        if intent == "CREATE_BRAND":
            strategy_result = BrandStrategistAgent.execute(project, message_content)
            image_result = CopilotTools.execute_generation(project, user, intent, module, message_content, asset_type)
            
            response_type = "multi_asset"
            structured_content = {
                "strategy": strategy_result,
                "visuals": image_result
            }
            response_text = f"I have successfully created your entire brand package for {project.business_name}!"
            
        elif intent in ["REDESIGN_BRAND", "CHANGE_COLORS", "CHANGE_TYPOGRAPHY", "UPDATE_BRAND_IDENTITY"]:
            mod_result = BrandModificationAgent.execute(project, message_content)
            response_type = "card"
            structured_content = mod_result
            response_text = "I've updated your brand identity based on your request."
            
        elif intent in ["GENERATE_BRAND_VISUAL", "GENERATE_LOGO", "GENERATE_BRAND_BOARD", "GENERATE_PROMOTIONAL_ASSET", "REDESIGN_UI", "REFINE_ASSET", "GENERATE_MARKETING_CONTENT", "GENERATE_SOCIAL_MEDIA", "GENERATE_CAMPAIGN"]:
            result = CopilotTools.execute_generation(project, user, intent, module, message_content, asset_type)
            if "error" not in result:
                response_type = "multi_asset" if isinstance(result, list) else "card"
                structured_content = {"assets": result} if isinstance(result, list) else result
                response_text = f"Here is the {asset_type or 'generated content'} you requested."
            else:
                response_type = "text"
                structured_content = {"text": f"{result['error']}"}
                response_text = structured_content["text"]
            
        elif intent == "OUT_OF_DOMAIN":
            response_type = "text"
            response_text = "I’m BrandCraft AI Copilot, specialized in building and managing brands. I can help with branding, visual identity, marketing, social media, campaigns, creative assets, and brand UI. I cannot assist with unrelated topics."
            structured_content = {"text": response_text}
            
        else:
            context = BrandContextService.build_summary_context(project)
            context_str = json.dumps(context, indent=2)
            system_prompt = (
                f"You are BrandCraft AI Copilot. You are an expert brand strategist and designer.\n"
                f"IMPORTANT CAPABILITY RULES:\n"
                f"1. You DO have the ability to generate images, logos, marketing copy, and social media posts. The system handles this automatically.\n"
                f"2. CRITICAL RESTRICTION: You MUST ONLY discuss topics related to brand building, naming, visual design, UI updates, color palettes, and marketing.\n\n"
                f"CURRENT PROJECT CONTEXT:\n{context_str}\n\n"
            )
            response_text = AIService.generate_text(prompt=message_content, system_message=system_prompt)
            structured_content = {"text": response_text}

        if response_text:
            ChatMessage.objects.create(
                conversation=conversation,
                role='ai',
                content=response_text,
                metadata={"intent": intent, "module": module, "response_type": response_type}
            )
            
            return {
                "success": True,
                "conversation_id": conversation.id,
                "response_type": response_type,
                "message": response_text,
                "content": structured_content,
                "actions": actions
            }
        else:
            return {"success": False, "error": "AI system failed to generate a response."}
