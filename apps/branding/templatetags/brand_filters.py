import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def render_bold(text):
    if not isinstance(text, str):
        return text
    # Replace **text** with <strong>text</strong>
    return mark_safe(re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text))
