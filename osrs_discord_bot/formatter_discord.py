"""Format messages for output to discord client.

Functions:
    format_search
    fraction_to_float
    format_numbers
    format_discord
    format_hiscore

"""

import csv
import re
import string

from osrs_discord_bot.constants import SKILL_NAMES

def format_search(s):
    s = s.lower()
    s = s.replace(' ','')
    regexPunc = re.compile(f'[{re.escape(string.punctuation)}]')
    return regexPunc.sub('', s)


def fraction_to_float(frac):
    # convert fractions to floats
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac


def format_numbers(*args):
    for num in args:
        num = f'{num:n}'
    return args


def format_discord(message):
    # format message for discord
    formMessage = '```' + message + '```'
    return formMessage


def format_hiscore(username, skill, response):
    # format the response from OSRS Hiscore API
    splitLines = response.splitlines()
    reader = csv.reader(splitLines)
    skills = list(reader)
    skill_dict = dict(zip(SKILL_NAMES, skills))
    hiscore_message_header = format_discord(
        f'{username:<15s}{"Level":>10s}{"XP":>15s}'
    )
    hiscore_message_body = ''
    if skill == 'all':
        for s in skill_dict:
            hiscore_message_body = (hiscore_message_body 
                + f'\n{s.capitalize():<15s}{skill_dict[s][1]:>10s}'
                f'{int(skill_dict[s][2]):>15n}'
            )
    else:  
        hiscore_message_body = (hiscore_message_body 
            + f'\n{skill.capitalize():<15s}{skill_dict[skill][1]:>10s}'
            f'{int(skill_dict[skill][2]):>15n}'
        )
    hiscore_message = (hiscore_message_header 
    + format_discord(hiscore_message_body)
    )
    return hiscore_message