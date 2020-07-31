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

import string
import requests
from requests.compat import urljoin
from requests.exceptions import Timeout

from osrsbox import items_api

import osrs_discord_bot.formatter_discord as f
from osrs_discord_bot.constants import (
    SKILL_NAMES, WIKI_BASE_URL, WISE_BASE_URL, EXCHANGE_BASE_URL, HISCORE_BASE_URL
)

ALL_DB_ITEMS = items_api.load()

def get_response(base_url, path=None, params=None, timeout=5):
    try:
        resp = requests.get(
            urljoin(base_url, path),
            params=params,
            timeout=timeout
        )
        return resp
    except Timeout:
        return 'timeout'


def search_price(item_dict):
    """Searches for the prices using the Exchange API.

    Args:
        item_dict (dict): Key, value of item ids, item names.
    
    """
    # search prices using OSBuddy Exchange
    ge_prices = get_response(EXCHANGE_BASE_URL, "summary.json")
    ge_prices_dict = ge_prices.json()
    for key in item_dict:
        try:
            single_item = ge_prices_dict[key]
            buyPrice, sellPrice = single_item['buy_average'], single_item['sell_average']
            margin = buyPrice - sellPrice
            buyPrice, sellPrice, margin = f.formatNumbers(buyPrice, sellPrice, margin)
        except KeyError:
            buyPrice, sellPrice, margin = 'N/A', 'N/A', 'N/A'
        item_dict[key] = {'name':item_dict[key], 'buyPrice':buyPrice, 'sellPrice':sellPrice, 'margin':margin}
    return item_dict


def search_items(query, num):
    # search osrsbox items list for query
    item_dict = {}
    counter = 0
    max_iter_flag = False
    for item in ALL_DB_ITEMS:
        if (f.formatSearch(query) in f.formatSearch(item.name) and 
        item.tradeable_on_ge == True and item.noted == False and item.placeholder == False):
            item_dict[str(item.id)] = item.name
            counter += 1
            if counter == num:
                max_iter_flag = True
                break
    return item_dict, max_iter_flag
    

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
        no_drop = (1 - droprate)**actions
        yes_drop = 1 - no_drop
        percent = yes_drop * 100
        chance_message = f'{percent:.2f}% chance of getting the drop within {actions} actions.'
    return chance_message


def hiscore_message(skill, *args):
    username = ' '.join(args)
    skill = skill.lower()
    if username == '' or skill not in SKILL_NAMES + ['all']:
        hiscore_message = 'Please enter a skill or all before the username.'
    else:
    # request data from OSRS Hiscores
        response = get_response(HISCORE_BASE_URL, params={"player":username})
        if response.status_code == 404:
            hiscore_message = f'Player {username} does not exist or OSRS Hiscores are down.'
        elif response == 'timeout':
            hiscore_message = 'The request to OSRS Hiscores timed out.'
        else:
            hiscore_message = f.formatHiscore(username, skill, response.text)
    return hiscore_message 


def ge_message(*args):
    item = ' '.join(args)
    if len(item) < 3:
        ge_message = 'Please be more specific.'
    else:
        foundItems, max_iter_flag = search_items(item, 10)
        if foundItems == {}:
            ge_message = 'No item named' + ' "' + item + '" ' + 'found on GE.'
        else:
            ge_message_header = f.formatDiscord(f'{"Item":<40s}{"Offer Price":>15s}{"Sell Price":>15s}{"Margin":>15s}')
            prices_dict = search_price(foundItems)
            ge_message_body = f.formatDiscord(_parse_ge_response(prices_dict, max_iter_flag))
            ge_message = ge_message_header + ge_message_body
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


def wiki_message(*args):
    subject = '_'.join(args)
    if get_response(WIKI_BASE_URL, path=subject).status_code == 404:
        wiki_message = 'OSRS Wiki article with that title does not exist.'
    else:
        wiki_message = urljoin(WIKI_BASE_URL, subject)
    return wiki_message


def _parse_tracker_response(delta_dict):
    tracker_message = ""
    filtered_dict = {key:value for key, value in delta_dict["data"].items() if key in SKILL_NAMES}
    for skill in filtered_dict:
        gained = filtered_dict[skill]["experience"]["gained"]
        if gained > 0:
            tracker_message = (tracker_message + 
            f'\n{skill.capitalize():<20s}{gained:n}')
    return tracker_message


def _parse_ge_response(prices_dict, max_iter_flag):
    ge_message_body = ""
    for key in prices_dict:
        single_item = prices_dict[key]
        ge_message_body = (ge_message_body + 
        f'\n{single_item["name"]:<40s}{single_item["buyPrice"]:>15n}'
        f'{single_item["sellPrice"]:>15n}{single_item["margin"]:>15n}')
    if max_iter_flag == True:
        ge_message_body = (ge_message_body +
        '\n\nShowing the first 10 results only. Please refine the search if the item is not listed.')
    return ge_message_body     