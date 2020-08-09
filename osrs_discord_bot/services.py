"""Contains logic for sending requests and output messages.

Classes:
    ApiRequest

Functions:
    search_price
    search_items
    chance_message
    hiscore_message
    price_message
    tracker_message
    wiki_message
    get_trend_data
    parse_trend_data
    plot_graph
    name_to_id

"""

import string
import requests
import time
import datetime
import io

from requests.compat import urljoin
from requests.exceptions import Timeout
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from osrsbox import items_api

import osrs_discord_bot.formatter_discord as f
from osrs_discord_bot.constants import (
    SKILL_NAMES, WIKI_BASE_URL, WISE_BASE_URL, EXCHANGE_BASE_URL, 
    HISCORE_BASE_URL
)

ALL_DB_ITEMS = items_api.load()

def get_response(base_url, path=None, params=None, headers=None, timeout=5):
    """Sends a get request to the URL provided.

    The request timesout if the reponse takes longer than 5 seconds.
    
    Args:
        base_url (str): Base URL.
        path (str): Path from base URL.
        params (dict): key:value of param:value, defaults to None.
        headers (dict): header:value, defaults to None.
        timeout (int): Seconds until request is timed out, defaults to 5.
    
    """

    try:
        resp = requests.get(
            urljoin(base_url, path),
            params=params,
            timeout=timeout,
            headers=headers
        )
        return resp
    except Timeout:
        return 'timeout'


def search_price(item_dict):
    """Searches for the prices using the Exchange API.

    Args:
        item_dict (dict): Key, value of item ids, item names.

    Returns:
        Dictionary with prices from OSBuddy Exchange.
    
    """

    ge_prices = get_response(EXCHANGE_BASE_URL, "/exchange/summary.json")
    ge_prices_dict = ge_prices.json()
    for key in item_dict:
        try:
            single_item = ge_prices_dict[key]
            buy_price = single_item['buy_average']
            sell_price = single_item['sell_average']
            margin = buy_price - sell_price
            buy_price, sell_price, margin = f.formatNumbers(
                buy_price, sell_price, margin
            )
        except KeyError:
            buy_price, sell_price, margin = 'N/A', 'N/A', 'N/A'
        item_dict[key] = {'name':item_dict[key], 'buy_price':buy_price, 
            'sell_price':sell_price, 'margin':margin
        }
    return item_dict


def search_items(query, num):
    """Searches for items in the osrsbox database.

    Args:
        query (str): Name of item.
        num (int): Number of results to return.

    Returns:
        Dictionary of item id and name as well as number of items found.
    
    """

    # search osrsbox items list for query
    item_dict = {}
    counter = 0
    max_iter_flag = False
    for item in ALL_DB_ITEMS:
        if (f.formatSearch(query) in f.formatSearch(item.name) 
            and item.tradeable_on_ge == True 
            and item.noted == False 
            and item.placeholder == False
        ):
            item_dict[str(item.id)] = item.name
            counter += 1
            if counter == num:
                max_iter_flag = True
                break
    return item_dict, max_iter_flag
    

def chance_message(droprate, actions=None):
    """Creates the message response for the chance command.

    Args:
        droprate (int|float): Drop rate.
        actions (int): Number of actions.

    Retuns:
        String message response to be sent to the client.
    
    """

    if droprate.find('/') != -1:  # if fraction given convert to float
        droprate = f.fraction2Float(droprate)

    try:
        droprate = float(droprate)
        actions = int(actions)
    except ValueError:
        chance_message = (
            'Please enter the drop rate as a fraction '
            'or decimal and the number of actions as an integer.'
        )
    except TypeError:
        chance_message = 'Please enter the number of actions.'

    if type(droprate) == float and type(actions) == int:
        no_drop = (1 - droprate)**actions
        yes_drop = 1 - no_drop
        percent = yes_drop * 100
        chance_message = (
            f'{percent:.2f}% chance of getting '
            f'the drop within {actions} actions.'
        )
    return chance_message


def hiscore_message(skill, *args):
    """Creates the message response for the hiscore command.

    Args:
        skill (str): The skill to lookup.
        *args (str): Username.
    
    Returns:
        String message response to be sent to the client.

    """

    username = ' '.join(args)
    skill = skill.lower()
    if username == '' or skill not in SKILL_NAMES + ['all']:
        hiscore_message = 'Please enter a skill or all before the username.'
    else:
    # request data from OSRS Hiscores
        response = get_response(HISCORE_BASE_URL, 
            '/m=hiscore_oldschool/index_lite.ws',  params={"player":username}
        )
        if response.status_code == 404:
            hiscore_message = (f'Player {username} does not '
            f'exist or OSRS Hiscores are down.')
        elif response == 'timeout':
            hiscore_message = 'The request to OSRS Hiscores timed out.'
        else:
            hiscore_message = f.formatHiscore(username, skill, response.text)
    return hiscore_message 


def price_message(*args):
    """Creates the message response for the ge command.

    Args:
        *args (str): Item to look up the price for.

    Returns:
        String message response to be sent to the client.
    
    """

    item = ' '.join(args)
    if len(item) < 3:
        ge_message = 'Please be more specific.'
    else:
        foundItems, max_iter_flag = search_items(item, 10)
        if foundItems == {}:
            ge_message = 'No item named' + ' "' + item + '" ' + 'found on GE.'
        else:
            ge_message_header = f.formatDiscord(
                f'{"Item":<40s}{"Offer Price":>15s}'
                f'{"Sell Price":>15s}{"Margin":>15s}'
            )
            prices_dict = search_price(foundItems)
            ge_message_body = f.formatDiscord(
                _parse_ge_response(prices_dict, max_iter_flag)
            )
            ge_message = ge_message_header + ge_message_body
    return ge_message


def tracker_message(period, *args):
    """Creates the message response for the tracker command.

    Args:
        period (str): Time period to look at xp gained for.
        *args (str): Username.

    Returns:
        String message response to be sent to the client.
    
    """
    tracker_message = ''
    username = ' '.join(args)
    delta_response = get_response(
        WISE_BASE_URL,
        f'/api/players/username/{username}/gained',
        params={"period":period}
    )
    delta_dict = delta_response.json()
    if 'message' in delta_dict:
        tracker_message = (
            f'Player {username} does not '
            f'exist on Wise Old Man XP Tracker.'
        )
    else:
        tracker_message = _parse_tracker_response(delta_dict)
        if tracker_message == '':
            tracker_message = 'No gains in the specified period.'   
        else:
            tracker_message = (f'```{"Skill":<20s}Experience```' 
                + f.formatDiscord(tracker_message)
            )
    return tracker_message


def wiki_message(*args):
    """Creates the messages response for the wiki command.

    Args:
        *args (str): Query to search the wiki for.

    Returns:
        String message to be sent to the client.
    
    """

    subject = '_'.join(args)
    if get_response(WIKI_BASE_URL, path='/w/'+subject).status_code == 404:
        wiki_message = 'OSRS Wiki article with that title does not exist.'
    else:
        wiki_message = urljoin(WIKI_BASE_URL, '/w/' + subject)
    return wiki_message


def _parse_tracker_response(delta_dict):
    tracker_message = ""
    filtered_dict = {key:value 
        for key, value in delta_dict["data"].items() 
        if key in SKILL_NAMES
    }
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
        f'\n{single_item["name"]:<40s}{single_item["buy_price"]:>15n}'
        f'{single_item["sell_price"]:>15n}{single_item["margin"]:>15n}')
    if max_iter_flag == True:
        ge_message_body = (ge_message_body +
        '\n\nShowing the first 10 results only.'
        ' Please refine the search if the item is not listed.')
    return ge_message_body     

def get_trend_data(item_id, period='month'):
    period_dict = {'week':180, 'month':1440, 'quarter':4320}
    path = f'/exchange/graphs/{period_dict[period]}/{item_id}.json'
    resp = get_response(EXCHANGE_BASE_URL, path=path)
    return resp.json()

# data time is in milliseconds and points are daily
def parse_trend_data(resp_dict):
    x = []
    y = []
    for i in resp_dict:
        x.append(datetime.datetime.fromtimestamp(i['ts']/1000))
        y.append(i['overallPrice'])
        # print(time.strftime('%Y-%m-%d', time.localtime(i['ts']/1000)),
        #     i['overallPrice']
        # )
    return mdate.date2num(x), y

def plot_graph(item_id, x, y):
    item = ALL_DB_ITEMS.lookup_by_item_id(int(item_id))

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    plt.plot_date(x,y, fmt='o-')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(item.name)
    ax.xaxis.set_tick_params(rotation=30)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def name_to_id(item_name):
    item_dict, max_items_flag = search_items(item_name, 10)
    if item_dict == {}:
        return "No item found with that name."
    else:
        message_dict = [
            f'ID: {item_id:<10} Name: {item_name:<10}' 
            for item_id, item_name in item_dict.items()
        ]
        if max_items_flag:
            message_dict.append('\nShowing first 10 results.')
        name_to_id_message = f.formatDiscord('\n'.join(message_dict))
        return name_to_id_message