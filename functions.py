import requests
import re
import string
from osrsbox import items_api

all_db_items = items_api.load()
regexPunc = re.compile('[%s]' % re.escape(string.punctuation))

def formatSearch(s):
    s = s.lower()
    return regexPunc.sub('', s)

def splitText(regex, delimiter, text):
    outputList = re.findall(regex, text)
    outputList = [i.split(delimiter) for i in outputList]
    return outputList

def fraction2Float(frac):
    # convert fractions to floats
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac

def getResponse(target_url):
    # handle requests and acquire response
    request = requests.get(target_url)
    response = request.status_code
    if response == 404:
        return response
    else:
        try:
            message = request.json()
            return message
        except ValueError:
            return request.text #return raw text

def formatDiscord(message):
    # format message for discord
    formMessage = '```' + message + '```'
    return formMessage

def formatHiscore(username, oneSkill, skill_name, response):
    # format the response from OSRS Hiscore API
    skills = splitText(r'(.*,.*,.*)', ',', response)
    skill_dict = dict(zip(skill_name, skills))
    hiscore_message_header = formatDiscord(f'{username:<15s}{"Level":>10s}{"XP":>15s}')
    hiscore_message_body = ''
    if oneSkill == 'All':
        for s in skill_dict:
            hiscore_message_body = hiscore_message_body +\
                 f'\n{s:<15s}{skill_dict[s][1]:>10s}{skill_dict[s][2]:>15s}'
    else:  
        hiscore_message_body = hiscore_message_body +\
             f'\n{oneSkill:<15s}{skill_dict[oneSkill][1]:>10s}{skill_dict[oneSkill][2]:>15s}'
    hiscore_message = hiscore_message_header + formatDiscord(hiscore_message_body)
    return hiscore_message

def searchItems(query, num):
    # search osrsbox items list for query
    itemDict = {}
    counter = 0
    for item in all_db_items:
        if query in item.name:
            itemDict[str(item.id)] = item.name
            counter += 1
            if counter == num:
                break
    return itemDict 

def searchPrice(itemDict, ExchangeURL):
    # search prices using OSBuddy Exchange
    ge_prices = getResponse(ExchangeURL)
    for key in itemDict:
        try:
            buyPrice, sellPrice = ge_prices[key]['buy_average'], ge_prices[key]['sell_average']
            margin = buyPrice - sellPrice
        except KeyError:
            buyPrice, sellPrice, margin = 'N/A', 'N/A', 'N/A'
        itemDict[key] = [itemDict[key], buyPrice, sellPrice, margin]
    return itemDict


class API_Request:
    def __init__(self, base_url):
        self.base_url = base_url

    def GET(self, url):
        request_url = self.base_url + url
        response = getResponse(request_url)
        return response