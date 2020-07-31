# osrs_discord_bot.py

import locale

from osrs_discord_bot.settings import TOKEN
from osrs_discord_bot.bot import bot


locale.setlocale(locale.LC_ALL, '')


def run_bot():
    bot.run(TOKEN)


def main():
    run_bot()


if __name__ == '__main__':
    main()
