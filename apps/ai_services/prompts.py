class PromptLibrary:
    @staticmethod
    def get_strategy_prompt(context):
        return f"""
Analyze the following business and generate a core brand strategy.
Business Idea: {context['business_idea']}
Industry: {context['industry']}
Target Audience: {context['target_audience']}
Goal: {context['business_goal']}

Return ONLY a JSON object with the following keys:
- "mission": A short, powerful mission statement (1-2 sentences).
- "vision": A forward-looking vision statement.
- "usp": The Unique Selling Proposition.
- "brand_voice": A description of the brand's tone of voice.
- "values": A list of 3-5 core brand values (strings).
- "keywords": A list of 5-7 SEO/strategic keywords (strings).
"""

    @staticmethod
    def get_naming_prompt(context):
        return f"""
Generate 10 creative and catchy business names for the following business:
Idea: {context['business_idea']}
Industry: {context['industry']}
Audience: {context['target_audience']}
Personality: {context['personality']}

Return ONLY a JSON object with the key "names" containing a list of 10 strings.
"""

    @staticmethod
    def get_identity_prompt(context):
        return f"""
Generate visual identity recommendations based on the following:
Industry: {context['industry']}
Personality: {context['personality']}
Preferred Style: {context['visual_style']}
Goal: {context['business_goal']}

Return ONLY a JSON object with the following keys:
- "typography_direction": Advice on font styles.
- "color_psychology": What colors should represent and why.
- "imagery_style": Description of photo/illustration style to use.
"""

    @staticmethod
    def get_logo_prompt(context):
        return f"""
Generate a structured DALL-E/Midjourney prompt for a logo.
Business Name: {context['business_name']}
Industry: {context['industry']}
Personality: {context['personality']}
Style: {context['visual_style']}

Return ONLY a JSON object with the key "prompt" containing the exact string to use for generation.
"""

    @staticmethod
    def get_slogan_prompt(context):
        return f"""
Generate 5 catchy marketing slogans.
Business Name: {context['business_name']}
USP: {context['usp']}
Audience: {context['target_audience']}
Voice: {context['voice']}

Return ONLY a JSON object with the key "slogans" containing a list of 5 strings.
"""
