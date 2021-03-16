# settings.py

import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CONTACT = os.getenv('DISCORD_CONTACT')