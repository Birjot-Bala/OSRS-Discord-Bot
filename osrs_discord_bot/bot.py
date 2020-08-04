"""Creating a bot instance and adding commands.

Functions:
    on_ready
    hiscore
    ge
    wiki
    chance
    tracker

"""
import discord
from discord.ext import commands
from json.decoder import JSONDecodeError

import osrs_discord_bot.services as se



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
    help=('Calculates the percent chance of getting a drop '
        'within a set number of actions.'
    )
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


@bot.command(name='trend', 
    help='Shows the trend of the item price for the period.'
)
async def trend(ctx, item_id, period='month'):
    try:
        x, y = se.parse_trend_data(se.get_trend_data(item_id, period=period))
        await ctx.send(
            file=discord.File(se.plot_graph(item_id, x, y), 'trend.png')
        )
    except JSONDecodeError:
        await ctx.send("Error. Something went wrong. Check the id and period.")


@bot.command(name='id',
    help='Search the database for the item id.'
)
async def name_to_id(ctx, *args):
    item_name = ' '.join(args)
    await ctx.send(se.name_to_id(item_name))

