# osrs_discord_bot.py

import os
import requests
import string
import locale

import lib.services as se
import lib.discord_formatter as f

from lib.services import ApiRequest
from dotenv import load_dotenv
from discord.ext import commands
from lib.constants import EXCHANGE_URL, WISE_BASE_URL, HISCORE_BASE_URL, SKILL_NAMES, WIKI_BASE_URL

locale.setlocale(locale.LC_ALL, '')
load_dotenv()

# acquiring the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')


# initializing class instances for APIs being used
WiseOldMan = ApiRequest(WISE_BASE_URL)
Hiscores = ApiRequest(HISCORE_BASE_URL)
GrandExchange = ApiRequest(EXCHANGE_URL)
Wiki = ApiRequest(WIKI_BASE_URL)


# selected prefix for discord commands
bot = commands.Bot(command_prefix='!')
        

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# !hiscore {skill} {username}
@bot.command(name='hiscore', help='Posts player hiscores.')
async def hiscore(ctx, skill, *args):
    hiscore_message = se.hiscore_message(Hiscores, skill, *args)
    await ctx.send(hiscore_message)


# !ge X posts GE price information of first 10 items that include X
@bot.command(name='ge', help='Posts GE price of items')
async def ge(ctx, *args):
    ge_message = se.ge_message(GrandExchange, *args)
    await ctx.send(ge_message)
        
# !wiki X posts a link to the wiki for X
@bot.command(name='wiki', help='Pulls up wiki link')
async def wiki(ctx, *args):
    subject = '_'.join(args)
    wiki_message = Wiki.base_url + subject
    if Wiki.GET(subject) == 404:
        wiki_message = 'OSRS Wiki article with that title does not exist.'
    await ctx.send(wiki_message)

@bot.command(name='chance', help='Calculates the percent chance of getting a drop within a set number of actions.')
#!chance X, Y calculates the chance of hitting the X drop rate in Y actions
async def chance(ctx, droprate, actions=None):
    chance_message = se.chance_message(droprate, actions)
    await ctx.send(chance_message)


@bot.command(name='tracker', help='Uses the Wise Old Man API to track XP gains. !tracker (period) (username). Periods can be day, week, month or year.')
async def tracker(ctx, period, *args):
    tracker_message = se.tracker_message(WiseOldMan, period, *args)
    await ctx.send(tracker_message)

    
bot.run(TOKEN)
