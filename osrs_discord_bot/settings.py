# settings.py

import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GE_TRACKER_TOKEN = os.getenv('GE_TRACKER_TOKEN')