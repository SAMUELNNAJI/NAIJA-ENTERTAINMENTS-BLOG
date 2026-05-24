from django import template
import re

register = template.Library()

# Cloudinary cloud name – matches settings.py CLOUDINARY_STORAGE
CLOUD_NAME = 'dt6ti5ehx'


@register.filter(name='optimized_url')
def optimized_url(field_url):
    """Apply Cloudinary auto optimization (quality + format) to any Cloudinary URL.
    Works with image, video, and raw resources by adding q_auto,f_auto before the version segment.
    """
    if not field_url:
        return ''

    url = str(field_url)
    # Match Cloudinary URL pattern: https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{version}/{public_id}.{ext}
    pattern = re.compile(
        r'(https://res\.cloudinary\.com/' + re.escape(CLOUD_NAME) + r'/)'
        r'(image|video|raw|)/upload/',
        re.IGNORECASE
    )

    def replacement(match):
        # Add auto for resource type (if not already auto) and q_auto,f_auto for optimization
        resource_type = match.group(2)
        # Use auto for resource type to let Cloudinary decide based on file extension
        return match.group(1) + 'auto/upload/q_auto,f_auto,'

    return pattern.sub(replacement, url)
