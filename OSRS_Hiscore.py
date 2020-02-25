
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

#acquiring the bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

def formatSearch(s):
    s = s.lower()
    return regexPunc.sub('', s)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='hiscore', help='Posts character hiscores') #!hiscore X, Y posts X skill of Y account
async def hiscore(ctx, oneSkill, *args):
    username = ''
    for arg in args:
        username = username + ' ' + str(arg)
#request data from OSRS Hiscores
    request = requests.get('http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + username)
    response = request.status_code
    if response == 404:
        hiscore_message = 'Player {} does not exist or OSRS Hiscores are down.'.format(username)

    else:
        raw = request.text

        skill_name = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
        'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing',
        'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
        'Farming', 'Runecraft', 'Hunter', 'Construction']

    #format raw text
        skills = re.findall(r'(.*,.*,.*)',raw)
        skills = [i.split(',') for i in skills]
        skill_dict = dict(zip(skill_name,skills))
        hiscore_message = '```{:<15s}{:>10s}{:>15s}```'.format(username, 'Level', 'XP') + '```'

        if oneSkill == 'all':
            for s in skill_dict:
                hiscore_message = hiscore_message + '\n{:<15s}{:>10s}{:>15s}'.format(s, skill_dict[s][1], skill_dict[s][2])
            hiscore_message = hiscore_message + '```'
        else:
            if oneSkill.capitalize() in skill_dict.keys():
                oneSkill = oneSkill.capitalize()
                hiscore_message = hiscore_message + '\n{:<15s}{:>10s}{:>15s}'.format(oneSkill, skill_dict[oneSkill][1], skill_dict[oneSkill][2]) + '```'
            else:
                hiscore_message = '{} is not a skill.'.format(oneSkill)

    await ctx.send(hiscore_message)

@bot.command(name='ge', help='Posts GE price of items') #!ge X posts GE price information of first 10 items that include X
async def ge(ctx, item, *args):
    for arg in args:
        item = item + ' ' + arg
    if len(item) < 3:
        await ctx.send('Please be more specific.')
    else:
        ge_message = '```{:<40s}{:>15s}{:>15s}{:>15s}```'.format('Item', 'Instant Buy', 'Sell', 'Margin') + '```'
        counter = 0
        itemrequest = requests.get('https://www.osrsbox.com/osrsbox-db/items-complete.json')
        itemrequest = itemrequest.json()
        ge_lookup = requests.get('https://rsbuddy.com/exchange/summary.json')
        ge_lookup = ge_lookup.json()

        for i in itemrequest: #search for item in item list up to first 10 results
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
                            ge_message = ge_message + '\n{:<40s}{:>15s}{:>15s}{:>15s}'.format(itemrequest[i]['name'], str(buyPrice), str(sellPrice), str(margin))
                        except KeyError:
                            ge_message = ge_message + '\n{:<40s}{:>15s}{:>15s}{:>15s}'.format(itemrequest[i]['name'], 'N/A', 'N/A', 'N/A')
                    elif counter == 11:
                        ge_message = ge_message + '\n\nShowing first 10 results only. Please refine search if item is not listed.'
                        break

        if counter == 0: #if no results found
            await ctx.send('No item found with ' + '"' + item + '" ' + 'name on GE.')
        else:
            ge_message = ge_message + '```'
            await ctx.send(ge_message)

@bot.command(name='wiki', help='Pulls up wiki link') #!wiki X posts a link to the wiki for X
async def wiki(ctx, subject, *args):
    for arg in args:
        subject = subject + '_' + arg
    wiki_message = 'https://oldschool.runescape.wiki/w/' + subject
    response = requests.get(wiki_message)
    if response.status_code == 200: #checks to see if page exists
        await ctx.send(wiki_message)
    elif response.status_code == 404:
        await ctx.send('OSRS Wiki article with that title does not exist.')

@bot.command(name='chance', help='Calculates the percent chance of getting a drop within a set number of actions.')
#!chance X, Y calculates the chance of hitting the X drop rate in Y actions 
async def chance(ctx, droprate, actions=None):
    if droprate.find('/') != -1: #if decimal given convert to float 
        droprate = droprate.split('/')
        droprate = float(droprate[0])/float(droprate[1])

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
        chance_message = '{:.2f} percent chance of getting getting the drop within {} actions.'.format(percent, actions)
        await ctx.send(chance_message)


   

bot.run(TOKEN)

