from django import template
import re

register = template.Library()

@register.filter
def youtube_id(url):
    """
    Extract the YouTube video ID from the URL.
    """
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^\s&]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None
