"""
WSGI config for DjangoAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoAPI.settings')
# Táto funkcia nastavuje predvolenú hodnotu pre premennú prostredia DJANGO_SETTINGS_MODULE, 
# ktorá určuje, kde sa nachádzajú nastavenia projektu. V tomto prípade je to DjangoAPI.settings.
#  To znamená, že Django bude používať konfiguračný súbor settings.py z projektu DjangoAPI.

application = get_wsgi_application()
# Toto vytvára WSGI aplikáciu, ktorá bude použitá webovým serverom na obsluhu požiadaviek. 
# Server spustí tento kód pri každej prichádzajúcej požiadavke a odošle odpoveď z Django aplikácie.