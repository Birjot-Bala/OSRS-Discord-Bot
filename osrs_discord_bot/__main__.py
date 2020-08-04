# osrs_discord_bot.py
"""Entry point module.

Functions:
    run_bot
    main
    
"""

import locale

from osrs_discord_bot.settings import DISCORD_TOKEN
from osrs_discord_bot.bot import bot


locale.setlocale(locale.LC_ALL, '')


def run_bot():
    bot.run(DISCORD_TOKEN)


def main():
    run_bot()


if __name__ == '__main__':
    main()
