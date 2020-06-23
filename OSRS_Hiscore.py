# OSRS_Hiscore.py

import os
import requests
import re
import string
import locale


from dotenv import load_dotenv
from discord.ext import commands

locale.setlocale(locale.LC_ALL, '')
load_dotenv()
regexPunc = re.compile('[%s]' % re.escape(string.punctuation))

# acquiring the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

skill_name = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
      'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing',
      'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
      'Farming', 'Runecraft', 'Hunter', 'Construction']


bot = commands.Bot(command_prefix='!')


def formatSearch(s):
    s = s.lower()
    return regexPunc.sub('', s)

def fraction2Float(frac):
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac

def formatUsername(args):
    # format username to string
    username = ''
    for arg in args:
        username = username + ' ' + str(arg)
    return username

def lookupHiscores(playerName):
    request = requests.get(
        'http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + playerName)
    return request

def getResponse(request):
    response = request.status_code
    if response == 404:
        return False
    else:
        try:
            message = request.json()
            return message
        except ValueError:
            return request.text #return raw text

        

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# !hiscore X, Y posts X skill of Y account
@bot.command(name='hiscore', help='Posts character hiscores')
async def hiscore(ctx, oneSkill, *args):
    username = formatUsername(args)
# request data from OSRS Hiscores
    request = lookupHiscores(username)
    response = getResponse(request)
    if response == False:
        hiscore_message = f'Player {username} does not exist or OSRS Hiscores are down.'
    else:
        skills = re.findall(r'(.*,.*,.*)', response)
        skills = [i.split(',') for i in skills]
        skill_dict = dict(zip(skill_name, skills))
        hiscore_message = '```{:<15s}{:>10s}{:>15s}```'.format(
            username, 'Level', 'XP') + '```'

        if oneSkill == 'all':
            for s in skill_dict:
                hiscore_message = hiscore_message + \
                    '\n{:<15s}{:>10s}{:>15s}'.format(
                        s, skill_dict[s][1], skill_dict[s][2])
            hiscore_message = hiscore_message + '```'
        else:
            if oneSkill.capitalize() in skill_dict.keys():
                oneSkill = oneSkill.capitalize()
                hiscore_message = hiscore_message + '\n{:<15s}{:>10s}{:>15s}'.format(
                    oneSkill, skill_dict[oneSkill][1], skill_dict[oneSkill][2]) + '```'
            else:
                hiscore_message = '{} is not a skill.'.format(oneSkill)

    await ctx.send(hiscore_message)


# !ge X posts GE price information of first 10 items that include X
@bot.command(name='ge', help='Posts GE price of items')
async def ge(ctx, item, *args):
    for arg in args:
        item = item + ' ' + arg
    if len(item) < 3:
        await ctx.send('Please be more specific.')
    else:
        ge_message = '```{:<40s}{:>15s}{:>15s}{:>15s}```'.format(
            'Item', 'Buy Order', 'Sell', 'Margin') + '```'
        counter = 0
        itemrequest = requests.get(
            'https://www.osrsbox.com/osrsbox-db/items-complete.json')
        itemrequest = itemrequest.json()
        ge_lookup = requests.get('https://rsbuddy.com/exchange/summary.json')
        ge_lookup = ge_lookup.json()

        for i in itemrequest:  # search for item in item list up to first 10 results
            if formatSearch(item) in formatSearch(itemrequest[i]['name']):
                if itemrequest[i]['noted'] == False and itemrequest[i]['placeholder'] == False and itemrequest[i]['tradeable_on_ge'] == True:
                    counter += 1
                    if counter < 11:
                        try:
                            buyPrice = ge_lookup[i]['buy_average']
                            sellPrice = ge_lookup[i]['sell_average']
                            margin = buyPrice - sellPrice
                            buyPrice = f'{buyPrice:n}'
                            sellPrice = f'{sellPrice:n}'
                            margin = f'{margin:n}'
                            ge_message = ge_message + '\n{:<40s}{:>15s}{:>15s}{:>15s}'.format(
                                itemrequest[i]['name'], str(buyPrice), str(sellPrice), str(margin))
                        except KeyError:
                            ge_message = ge_message + \
                                '\n{:<40s}{:>15s}{:>15s}{:>15s}'.format(
                                    itemrequest[i]['name'], 'N/A', 'N/A', 'N/A')
                    elif counter == 11:
                        ge_message = ge_message + \
                            '\n\nShowing first 10 results only. Please refine search if item is not listed.'
                        break

        if counter == 0:  # if no results found
            await ctx.send('No item found with ' + '"' + item + '" ' + 'name on GE.')
        else:
            ge_message = ge_message + '```'
            await ctx.send(ge_message)


# !wiki X posts a link to the wiki for X
@bot.command(name='wiki', help='Pulls up wiki link')
async def wiki(ctx, subject, *args):
    for arg in args:
        subject = subject + '_' + arg
    wiki_message = 'https://oldschool.runescape.wiki/w/' + subject
    response = requests.get(wiki_message)
    
    if getResponse(response) == False:
        await ctx.send('OSRS Wiki article with that title does not exist.')
    else:
        await ctx.send(wiki_message)


@bot.command(name='chance', help='Calculates the percent chance of getting a drop within a set number of actions.')
#!chance X, Y calculates the chance of hitting the X drop rate in Y actions
async def chance(ctx, droprate, actions=None):
    if droprate.find('/') != -1:  # if fraction given convert to float
        droprate = fraction2Float(droprate)

    try:
        droprate = float(droprate)
        actions = int(actions)
    except ValueError:
        await ctx.send('Please enter drop rates in fractions or decimals and actions in integers.')
    except TypeError:
        await ctx.send('Please enter the number of actions. ')

    if type(droprate) == float and type(actions) == int:
        noDrop = (1 - droprate)**actions
        yesDrop = 1 - noDrop
        percent = yesDrop * 100
        chance_message = '{:.2f} percent chance of getting getting the drop within {} actions.'.format(
            percent, actions)
        await ctx.send(chance_message)


@bot.command(name='tracker', help='Uses the Wise Old Man API to track XP gains. !tracker (period) (username). Periods can be day, week, month or year.')
async def tracker(ctx, period, *args):
    tracker_message = ''
    Skill = 'Skill'
    username = formatUsername(args)
    delta_request = requests.get(f'https://wiseoldman.net/api/players/username/{username}/gained?period={period}')
    delta_response = getResponse(delta_request)
    if 'message' in delta_response:
        tracker_message = f'Player {username} does not exist on Wise Old Man XP Tracker.'
    else:
        for skill in delta_response['data']:
            gains = delta_response['data'][skill]['experience']['gained']
            if gains > 0:
                tracker_message = tracker_message + \
                    f'\n{skill.capitalize():<20s}{gains:n}'
            if skill == "construction":
                break
        if tracker_message == '':
            tracker_message = 'No gains in the specified period.'   
        else:
            tracker_message = f'```{Skill:<20s}Experience```' + '```' + tracker_message + '```'

    await ctx.send(tracker_message)

    
bot.run(TOKEN)
