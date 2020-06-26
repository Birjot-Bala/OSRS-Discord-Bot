# OSRS_Hiscore.py

import os
import requests
import re
import string
import locale
import functions as f
from functions import API_Request

from dotenv import load_dotenv
from discord.ext import commands

locale.setlocale(locale.LC_ALL, '')
load_dotenv()


# acquiring the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

skill_name = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
      'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing',
      'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
      'Farming', 'Runecraft', 'Hunter', 'Construction']

ExchangeURL = 'https://rsbuddy.com/exchange/summary.json'

WiseOldMan = API_Request('https://wiseoldman.net/api')
Hiscores = API_Request('http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=')

bot = commands.Bot(command_prefix='!')
        

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# !hiscore {skill} {username}
@bot.command(name='hiscore', help='Posts player hiscores.')
async def hiscore(ctx, oneSkill, *args):
    username = ' '.join(args)
    oneSkill = oneSkill.capitalize()
    if username == '' or oneSkill not in [skill_name, 'All']:
        hiscore_message = 'Please enter a skill or all before the username.'
    else:
# request data from OSRS Hiscores
        response = Hiscores.GET(username)
        if response == 404:
            hiscore_message = f'Player {username} does not exist or OSRS Hiscores are down.'
        else:
            hiscore_message = f.formatHiscore(username, oneSkill, skill_name,response)
    await ctx.send(hiscore_message)


# !ge X posts GE price information of first 10 items that include X
@bot.command(name='ge', help='Posts GE price of items')
async def ge(ctx, item, *args):
    if args is not None:
        item = item + ' ' + ' '.join(args)
    if len(item) < 3:
        ge_message = 'Please be more specific.'
    else:
        foundItems, maxIter_Flag = f.searchItems(item, 10)
        if foundItems == {}:
            ge_message = 'No item named' + ' "' + item + '" ' + 'found on GE.'
        else:
            ge_message_header = f.formatDiscord(f'{"Item":<40s}{"Offer Price":>15s}{"Sell Price":>15s}{"Margin":>15s}')
            ge_message_body = ''
            itemPrices = f.searchPrice(foundItems, ExchangeURL)
            for key in itemPrices:
                singleItem = itemPrices[key]
                ge_message_body = (ge_message_body + 
                f'\n{singleItem["name"]:<40s}{singleItem["buyPrice"]:>15}'
                f'{singleItem["sellPrice"]:>15}{singleItem["margin"]:>15}')
            if maxIter_Flag == True:
                ge_message_body = (ge_message_body +
                '\n\nShowing the first 10 results only. Please refine the search if the item is not listed.') 
            ge_message = ge_message_header + f.formatDiscord(ge_message_body)
    await ctx.send(ge_message)
        
# !wiki X posts a link to the wiki for X
@bot.command(name='wiki', help='Pulls up wiki link')
async def wiki(ctx, subject, *args):
    subject = subject + '_' + '_'.join(args)
    wiki_message = 'https://oldschool.runescape.wiki/w/' + subject
    if f.getResponse(wiki_message) == 404:
        await ctx.send('OSRS Wiki article with that title does not exist.')
    else:
        await ctx.send(wiki_message)


@bot.command(name='chance', help='Calculates the percent chance of getting a drop within a set number of actions.')
#!chance X, Y calculates the chance of hitting the X drop rate in Y actions
async def chance(ctx, droprate, actions=None):
    if droprate.find('/') != -1:  # if fraction given convert to float
        droprate = f.fraction2Float(droprate)

    try:
        droprate = float(droprate)
        actions = int(actions)
    except ValueError:
        await ctx.send('Please enter drop rates in fractions or decimals and actions in integers.')
    except TypeError:
        await ctx.send('Please enter the number of actions.')

    if type(droprate) == float and type(actions) == int:
        noDrop = (1 - droprate)**actions
        yesDrop = 1 - noDrop
        percent = yesDrop * 100
        chance_message = f'{percent:.2f} percent chance of getting getting the drop within {actions} actions.'
        await ctx.send(chance_message)


@bot.command(name='tracker', help='Uses the Wise Old Man API to track XP gains. !tracker (period) (username). Periods can be day, week, month or year.')
async def tracker(ctx, period, *args):
    tracker_message = ''
    Skill = 'Skill'
    username = ' '.join(args)
    delta_response = WiseOldMan.GET(f'/players/username/{username}/gained?period={period}')
    if 'message' in delta_response:
        tracker_message = f'Player {username} does not exist on Wise Old Man XP Tracker.'
    else:
        for skill in delta_response['data']:
            gains = delta_response['data'][skill]['experience']['gained']
            if gains > 0:
                tracker_message = (tracker_message + 
                f'\n{skill.capitalize():<20s}{gains:n}')
            if skill == "construction":
                break
        if tracker_message == '':
            tracker_message = 'No gains in the specified period.'   
        else:
            tracker_message = f'```{Skill:<20s}Experience```' + '```' + tracker_message + '```'

    await ctx.send(tracker_message)

    
bot.run(TOKEN)
