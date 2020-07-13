import requests
import re
import string
import csv

from osrsbox import items_api
from requests.exceptions import Timeout

all_db_items = items_api.load()
regexPunc = re.compile('[%s]' % re.escape(string.punctuation))

def formatSearch(s):
    s = s.lower()
    s = s.replace(' ','')
    return regexPunc.sub('', s)

def fraction2Float(frac):
    # convert fractions to floats
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac

def getResponse(target_url):
    # handle requests and acquire response
    try:
        # timeout parameter to avoid hanging waiting for response
        request = requests.get(target_url, timeout=6)
        response = request.status_code
        if response == 404:
            return response
        else:
        # check the response to return it as json or raw text
            try:
                message = request.json()
                return message
            except ValueError:
                return request.text #return raw text
    except Timeout:
        response = 'timeout'
        return response        
    

def formatNumbers(*args):
    for num in args:
        num = f'{num:n}'
    return args

def formatDiscord(message):
    # format message for discord
    formMessage = '```' + message + '```'
    return formMessage

def formatHiscore(username, oneSkill, skill_name, response):
    # format the response from OSRS Hiscore API
    splitLines = response.splitlines()
    reader = csv.reader(splitLines)
    skills = list(reader)
    skill_dict = dict(zip(skill_name, skills))
    hiscore_message_header = formatDiscord(f'{username:<15s}{"Level":>10s}{"XP":>15s}')
    hiscore_message_body = ''
    if oneSkill == 'All':
        for s in skill_dict:
            hiscore_message_body = hiscore_message_body +\
                 f'\n{s:<15s}{skill_dict[s][1]:>10s}{int(skill_dict[s][2]):>15n}'
    else:  
        hiscore_message_body = hiscore_message_body +\
             f'\n{oneSkill:<15s}{skill_dict[oneSkill][1]:>10s}{int(skill_dict[oneSkill][2]):>15n}'
    hiscore_message = hiscore_message_header + formatDiscord(hiscore_message_body)
    return hiscore_message

def searchItems(query, num):
    # search osrsbox items list for query
    itemDict = {}
    counter = 0
    maxIter_flag = False
    for item in all_db_items:
        if (formatSearch(query) in formatSearch(item.name) and 
        item.tradeable_on_ge == True and item.noted == False and item.placeholder == False):
            itemDict[str(item.id)] = item.name
            counter += 1
            if counter == num:
                maxIter_flag = True
                break
    return itemDict, maxIter_flag 

def searchPrice(itemDict, ExchangeURL):
    # search prices using OSBuddy Exchange
    ge_prices = getResponse(ExchangeURL)
    for key in itemDict:
        try:
            singleItem = ge_prices[key]
            buyPrice, sellPrice = singleItem['buy_average'], singleItem['sell_average']
            margin = buyPrice - sellPrice
            buyPrice, sellPrice, margin = formatNumbers(buyPrice, sellPrice, margin)
        except KeyError:
            buyPrice, sellPrice, margin = 'N/A', 'N/A', 'N/A'
        itemDict[key] = {'name':itemDict[key], 'buyPrice':buyPrice, 'sellPrice':sellPrice, 'margin':margin}
    return itemDict


class API_Request:
    def __init__(self, base_url):
        self.base_url = base_url

    def GET(self, url):
        request_url = self.base_url + url
        response = getResponse(request_url)
        return response