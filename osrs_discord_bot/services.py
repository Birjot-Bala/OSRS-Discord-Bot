# services.py

"""Contains logic for sending requests and output messages.

Classes:
    ApiRequest

Functions:
    search_price
    search_items
    chance_message
    hiscore_message
    ge_message
    tracker_message

"""

import requests
from requests.compat import urljoin
from requests.exceptions import Timeout

import formatter_discord as f


from osrsbox import items_api
from constants import (
    SKILL_NAMES, WIKI_BASE_URL, WISE_BASE_URL, EXCHANGE_URL, HISCORE_BASE_URL
)

ALL_DB_ITEMS = items_api.load()

def get_response(base_url, path, params=None, timeout=5):
    try:
        resp = requests.get(
            urljoin(base_url, path),
            params=params,
            timeout=timeout
        )
        return resp
    except Timeout:
        return 'timeout'

class ApiRequest:

    def __init__(self, base_url):
        self.base_url = base_url

    def GET(self, url=''):
    # handle requests and acquire response
        get_url = self.base_url + url
        try:
            # timeout parameter to avoid hanging waiting for response
            request = requests.get(get_url, timeout=6)
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


def search_price(itemDict, ApiRequest):
    """Searches for the prices using the GE API.

    Args:
        itemDict (dict): Key, value of item ids, item names.
    
    """
    # search prices using OSBuddy Exchange
    ge_prices = ApiRequest.GET('/summary.json')
    for key in itemDict:
        try:
            singleItem = ge_prices[key]
            buyPrice, sellPrice = singleItem['buy_average'], singleItem['sell_average']
            margin = buyPrice - sellPrice
            buyPrice, sellPrice, margin = f.formatNumbers(buyPrice, sellPrice, margin)
        except KeyError:
            buyPrice, sellPrice, margin = 'N/A', 'N/A', 'N/A'
        itemDict[key] = {'name':itemDict[key], 'buyPrice':buyPrice, 'sellPrice':sellPrice, 'margin':margin}
    return itemDict


def search_items(query, num):
    # search osrsbox items list for query
    itemDict = {}
    counter = 0
    maxIter_flag = False
    for item in ALL_DB_ITEMS:
        if (f.formatSearch(query) in f.formatSearch(item.name) and 
        item.tradeable_on_ge == True and item.noted == False and item.placeholder == False):
            itemDict[str(item.id)] = item.name
            counter += 1
            if counter == num:
                maxIter_flag = True
                break
    return itemDict, maxIter_flag
    

def chance_message(droprate, actions=None):
    if droprate.find('/') != -1:  # if fraction given convert to float
        droprate = f.fraction2Float(droprate)

    try:
        droprate = float(droprate)
        actions = int(actions)
    except ValueError:
        chance_message = 'Please enter drop rates in fractions or decimals and actions in integers.'
    except TypeError:
        chance_message = 'Please enter the number of actions.'

    if type(droprate) == float and type(actions) == int:
        noDrop = (1 - droprate)**actions
        yesDrop = 1 - noDrop
        percent = yesDrop * 100
        chance_message = f'{percent:.2f}% chance of getting the drop within {actions} actions.'
    return chance_message


def hiscore_message(HiscoreApi, skill, *args):
    username = ' '.join(args)
    skill = skill.lower()
    if username == '' or skill not in SKILL_NAMES + ['all']:
        hiscore_message = 'Please enter a skill or all before the username.'
    else:
    # request data from OSRS Hiscores
        response = HiscoreApi.GET(username)
        if response == 404:
            hiscore_message = f'Player {username} does not exist or OSRS Hiscores are down.'
        elif response == 'timeout':
            hiscore_message = 'The request to OSRS Hiscores timed out.'
        else:
            hiscore_message = f.formatHiscore(username, skill, response)
    return hiscore_message 


def ge_message(GEApi, *args):
    item = ' '.join(args)
    if len(item) < 3:
        ge_message = 'Please be more specific.'
    else:
        foundItems, maxIter_Flag = search_items(item, 10)
        if foundItems == {}:
            ge_message = 'No item named' + ' "' + item + '" ' + 'found on GE.'
        else:
            ge_message_header = f.formatDiscord(f'{"Item":<40s}{"Offer Price":>15s}{"Sell Price":>15s}{"Margin":>15s}')
            ge_message_body = ''
            itemPrices = search_price(foundItems, GEApi)
            for key in itemPrices:
                singleItem = itemPrices[key]
                ge_message_body = (ge_message_body + 
                f'\n{singleItem["name"]:<40s}{singleItem["buyPrice"]:>15n}'
                f'{singleItem["sellPrice"]:>15n}{singleItem["margin"]:>15n}')
            if maxIter_Flag == True:
                ge_message_body = (ge_message_body +
                '\n\nShowing the first 10 results only. Please refine the search if the item is not listed.') 
            ge_message = ge_message_header + f.formatDiscord(ge_message_body)
    return ge_message


def tracker_message(period, *args):
    tracker_message = ''
    username = ' '.join(args)
    delta_response = get_response(
        WISE_BASE_URL,
        f'players/username/{username}/gained',
        params={"period":period}
    )
    delta_dict = delta_response.json()
    if 'message' in delta_dict:
        tracker_message = f'Player {username} does not exist on Wise Old Man XP Tracker.'
    else:
        tracker_message = _parse_tracker_response(delta_dict)
        if tracker_message == '':
            tracker_message = 'No gains in the specified period.'   
        else:
            tracker_message = f'```{"Skill":<20s}Experience```' + f.formatDiscord(tracker_message)
    return tracker_message


def _parse_tracker_response(delta_dict):
    tracker_message = ""
    filtered_dict = {key:value for key, value in delta_dict["data"].items() if key in SKILL_NAMES}
    for skill in filtered_dict:
        gained = filtered_dict[skill]["experience"]["gained"]
        if gained > 0:
            tracker_message = (tracker_message + 
            f'\n{skill.capitalize():<20s}{gained:n}')
    return tracker_message



# initializing class instances for APIs being used
Hiscores = ApiRequest(HISCORE_BASE_URL)
GrandExchange = ApiRequest(EXCHANGE_URL)
Wiki = ApiRequest(WIKI_BASE_URL)