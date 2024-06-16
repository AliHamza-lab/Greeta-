# chater/context_processors.py

from django.conf import settings

def extra_context(request):
    return {
        'SCRIPT_URL': settings.SCRIPT_URL,
        'CONFIG_SCRIPT_URL': settings.CONFIG_SCRIPT_URL,
    }
