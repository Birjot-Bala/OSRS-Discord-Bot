# osrs_discord_bot.py

import os
import locale

import services as se

from dotenv import load_dotenv
from discord.ext import commands

locale.setlocale(locale.LC_ALL, '')
load_dotenv()

# acquiring the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')


# selected prefix for discord commands
bot = commands.Bot(command_prefix='!')
        

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# !hiscore {skill} {username}
@bot.command(name='hiscore', help='Posts player hiscores.')
async def hiscore(ctx, skill, *args):
    hiscore_message = se.hiscore_message(skill, *args)
    await ctx.send(hiscore_message)


# !ge X posts GE price information of first 10 items that include X
@bot.command(name='ge', help='Posts GE price of items')
async def ge(ctx, *args):
    ge_message = se.ge_message(*args)
    await ctx.send(ge_message)
     
        
# !wiki X posts a link to the wiki for X
@bot.command(name='wiki', help='Pulls up wiki link')
async def wiki(ctx, *args):
    wiki_message = se.wiki_message(*args)
    await ctx.send(wiki_message)


@bot.command(
    name='chance',
    help='Calculates the percent chance of getting a drop within a set number of actions.'
)
#!chance X, Y calculates the chance of hitting the X drop rate in Y actions
async def chance(ctx, droprate, actions=None):
    chance_message = se.chance_message(droprate, actions)
    await ctx.send(chance_message)


@bot.command(
    name='tracker',
    help='Uses the Wise Old Man API to retrieve tracked XP gains.'
)
async def tracker(ctx, period, *args):
    tracker_message = se.tracker_message(period, *args)
    await ctx.send(tracker_message)

    
bot.run(TOKEN)
