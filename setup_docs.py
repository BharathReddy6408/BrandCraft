import os
import urllib.request
from django.core.files.base import ContentFile
from knowledge_base.models import Document

print("Creating Document 1...")
doc1_content = """# Brand Voice & Tone Framework

## 1. Overview
The BrandCraft voice is authoritative, visionary, and empowering. We speak to marketing professionals and brand strategists with confidence, showing them that generative AI is a tool to enhance human creativity, not replace it.

## 2. Core Pillars
- **Authoritative, not arrogant:** We know our stuff. We use data and clear examples.
- **Visionary, not unrealistic:** We talk about the future of branding, but ground it in tools available today.
- **Empowering, not condescending:** We guide the user and celebrate their wins.

## 3. Formatting Rules
- Always use active voice.
- Keep paragraphs under 4 sentences.
- Avoid AI buzzwords like 'synergy' or 'disruptive' unless quoting a source.
"""
doc1 = Document(title="Brand Voice Framework")
doc1.file.save("brand_voice_framework.txt", ContentFile(doc1_content.encode('utf-8')))

print("Creating Document 2...")
doc2_content = """# Target Audience Personas

## Persona 1: Sarah, The Creative Director
- **Age:** 35-45
- **Goal:** Wants to scale her agency's output without compromising on quality or hiring 50 new designers.
- **Pain Point:** Managing brand consistency across multiple freelance copywriters and designers.
- **How we help:** BrandCraft centralizes the brand guidelines and forces AI generations to adhere to the style guide.

## Persona 2: David, The Startup Founder
- **Age:** 25-35
- **Goal:** Needs a professional brand identity fast, so he can focus on building the product.
- **Pain Point:** Cannot afford a $20k branding agency.
- **How we help:** BrandCraft generates a complete brand board and initial assets within minutes for a fraction of the cost.
"""
doc2 = Document(title="Target Audience Personas")
doc2.file.save("audience_personas.txt", ContentFile(doc2_content.encode('utf-8')))

print("Creating Document 3 (Comprehensive Style Guide)...")
doc3_content = """# Comprehensive Visual Identity Guidelines

## Logo Usage
- **Clear Space:** Always maintain a minimum clear space around the logo equal to the height of the 'B' in BrandCraft.
- **Minimum Size:** The logo must never appear smaller than 1 inch wide in print or 72 pixels wide on screen.
- **Improper Use:** Do not stretch, distort, or apply drop shadows to the logo. Do not place the logo on busy photographic backgrounds without a solid color overlay.

## Color Palette
### Primary Colors
- **BrandCraft Navy:** HEX #0A2540 | RGB 10, 37, 64 | CMYK 100, 80, 40, 50
- **Accent Gold:** HEX #F6B846 | RGB 246, 184, 70 | CMYK 5, 28, 82, 0

### Secondary Colors
- **Slate Gray:** HEX #4A5568
- **Off-White:** HEX #F7FAFC

## Typography
- **Primary Heading Font:** 'Playfair Display' (Serif) - Used for all major headings and quotes.
- **Body Font:** 'Inter' (Sans-Serif) - Used for all body copy, UI elements, and subheadings.
- **Hierarchy:** Headings should be 2.5x the size of body text. (e.g. Body 16px, Heading 40px).

## Imagery Style
- Photography should feel authentic, unposed, and well-lit.
- Avoid generic stock photography involving handshakes or puzzle pieces.
- Use a slight cool-toned overlay (10% opacity BrandCraft Navy) on hero images to maintain brand consistency.
"""
doc3 = Document(title="Visual Identity Guidelines")
doc3.file.save("visual_identity_guidelines.md", ContentFile(doc3_content.encode('utf-8')))

print("Downloading PDF...")
# Public PDF: A lightweight public document from W3C
pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
try:
    req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    pdf_content = response.read()
    doc4 = Document(title="Sample Branding PDF")
    doc4.file.save("sample_branding.pdf", ContentFile(pdf_content))
    print("PDF Downloaded and Saved.")
except Exception as e:
    print("Error downloading PDF:", e)

print("All documents added successfully!")
