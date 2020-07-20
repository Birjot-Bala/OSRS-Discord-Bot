# discord_formatter.py

import csv
import re
import string

def formatSearch(s):
    s = s.lower()
    s = s.replace(' ','')
    regexPunc = re.compile(f'[{re.escape(string.punctuation)}]')
    return regexPunc.sub('', s)


def fraction2Float(frac):
    # convert fractions to floats
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac


def formatNumbers(*args):
    for num in args:
        num = f'{num:n}'
    return args


def formatDiscord(message):
    # format message for discord
    formMessage = '```' + message + '```'
    return formMessage


def formatHiscore(username, skill, skill_name, response):
    # format the response from OSRS Hiscore API
    splitLines = response.splitlines()
    reader = csv.reader(splitLines)
    skills = list(reader)
    skill_dict = dict(zip(skill_name, skills))
    hiscore_message_header = formatDiscord(f'{username:<15s}{"Level":>10s}{"XP":>15s}')
    hiscore_message_body = ''
    if skill == 'All':
        for s in skill_dict:
            hiscore_message_body = hiscore_message_body +\
                 f'\n{s:<15s}{skill_dict[s][1]:>10s}{int(skill_dict[s][2]):>15n}'
    else:  
        hiscore_message_body = hiscore_message_body +\
             f'\n{skill:<15s}{skill_dict[skill][1]:>10s}{int(skill_dict[skill][2]):>15n}'
    hiscore_message = hiscore_message_header + formatDiscord(hiscore_message_body)
    return hiscore_message