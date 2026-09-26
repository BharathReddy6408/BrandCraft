"""
WSGI config for BrandCraft project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'apps'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BrandCraft.settings')

application = get_wsgi_application()
