from django import template
import re

register = template.Library()

# Cloudinary cloud name – matches settings.py CLOUDINARY_STORAGE
CLOUD_NAME = 'dt6ti5ehx'


@register.filter(name='optimized_url')
def optimized_url(field_url):
    """Replace the raw/ delivery type in a Cloudinary URL with auto/ and add
    q_auto,f_auto so Cloudinary applies on-the-fly optimisation (quality + format)
    before the version segment: upload/vXXXXX/…
    """
    if not field_url:
        return ''

    url = str(field_url)
    pattern = re.compile(r'(https://res\.cloudinary\.com/' + re.escape(CLOUD_NAME) + r'/)raw(/upload/)')

    def replacement(match):
        return match.group(1) + 'auto' + match.group(2) + 'q_auto,f_auto,'

    return pattern.sub(replacement, url)
