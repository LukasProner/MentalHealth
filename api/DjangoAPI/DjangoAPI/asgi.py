"""
ASGI config for DjangoAPI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoAPI.settings')

application = get_asgi_application()

# Tento súbor v projekte Django (asgi.py) slúži na konfiguráciu rozhrania ASGI (Asynchronous Server Gateway Interface), čo je rozhranie medzi webovými servery a webovými aplikáciami alebo frameworkmi. V prípade Django sa používa na asynchrónne spracovanie požiadaviek, čo umožňuje lepší výkon pri práci s aplikáciami, ktoré vyžadujú vysokú škálovateľnosť alebo pracujú s WebSockets a inými asynchrónnymi úlohami.

# Konkrétne tento súbor robí nasledovné:

# Nastavuje premenné prostredia: Pomocou os.environ.setdefault sa nastaví predvolený modul s nastaveniami projektu (v tomto prípade DjangoAPI.settings).
# Inicializuje ASGI aplikáciu: Funkcia get_asgi_application() vytvorí inštanciu aplikácie, ktorá bude použitá na spracovanie prichádzajúcich asynchrónnych požiadaviek.
# Tento súbor je teda kľúčový pre nasadenie aplikácie na servery, ktoré podporujú asynchrónne spracovanie, napríklad pri použití serverov ako Uvicorn alebo Daphne.