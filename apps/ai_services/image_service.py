import uuid
import io
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ai_services.services import AIService
from brand_assets.models import BrandAsset

class ImageService:
    @staticmethod
    def compose_brand_text(image_bytes: bytes, text: str) -> bytes:
        """
        STAGE 2 VISUAL PIPELINE: Programmatically composite EXACT text over the AI generated artwork.
        """
        if not text:
            return image_bytes
            
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            # Create a transparent overlay for text
            txt = Image.new('RGBA', image.size, (255,255,255,0))
            d = ImageDraw.Draw(txt)
            
            # Simple scaling based on image width
            font_size = int(image.width * 0.1)
            # Try to load a generic font, fallback to default
            try:
                # Windows default, or could use a downloaded TTF
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
                
            # Use getbbox to calculate text dimensions
            bbox = d.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (image.width - text_width) / 2
            y = (image.height - text_height) / 2
            
            # Draw shadow
            d.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 180))
            # Draw text
            d.text((x, y), text, font=font, fill=(255, 255, 255, 255))
            
            out = Image.alpha_composite(image, txt)
            out = out.convert("RGB")
            
            img_byte_arr = io.BytesIO()
            out.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        except Exception as e:
            print("Pillow compositing failed:", e)
            return image_bytes # Fallback to original image if compositing fails

    @staticmethod
    def generate_and_save_asset(project, user, prompt: str, asset_type: str, require_text: bool = False):
        image_bytes = AIService.generate_image(prompt)
        if not image_bytes:
            return None
            
        if require_text and project.business_name:
            image_bytes = ImageService.compose_brand_text(image_bytes, project.business_name)
            
        filename = f"generated_assets/{uuid.uuid4().hex}.png"
        path = default_storage.save(filename, ContentFile(image_bytes))
        url = default_storage.url(path)
        
        asset = BrandAsset.objects.create(
            project=project,
            asset_type=asset_type.upper(),
            title=f"Generated {asset_type.replace('_', ' ').title()}",
            content_json={"prompt": prompt, "image_url": url},
            user=user
        )
        return asset

class BrandAssetGenerationService:
    @staticmethod
    def generate_multi_asset_package(project, user, assets_to_generate: list) -> list:
        """
        Generates an array of assets based on asset types requested.
        e.g. ['logo', 'brand_board', 'business_card']
        """
        from ai_services.agents import VisualBrandAgent
        results = []
        for asset_type in assets_to_generate:
            try:
                # Generate specific prompt for this asset
                prompt = VisualBrandAgent.assemble_specific_asset_prompt(project, asset_type)
                require_text = asset_type in ['logo', 'brand_board', 'business_card']
                
                asset = ImageService.generate_and_save_asset(project, user, prompt, asset_type, require_text=require_text)
                if asset:
                    results.append({"type": asset_type, "url": asset.content_json.get("image_url"), "status": "SUCCESS"})
                else:
                    results.append({"type": asset_type, "status": "FAILED"})
            except Exception as e:
                results.append({"type": asset_type, "status": "FAILED", "error": str(e)})
        return results
