# services.py

import requests

import lib.discord_formatter as f


from osrsbox import items_api
from requests.exceptions import Timeout

ALL_DB_ITEMS = items_api.load()

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


def searchPrice(itemDict, ApiRequest):
    # search prices using OSBuddy Exchange
    ge_prices = ApiRequest.GET()
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


def searchItems(query, num):
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