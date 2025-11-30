from django import template
from django.template.defaultfilters import stringfilter
import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value):
    # Extensions enable extra features like Tables, Code Blocks, and Auto-Linking
    return md.markdown(value, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables'])