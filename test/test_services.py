# test_services.py
# contains tests for services.py

import pytest
import requests
import json

import osrs_discord_bot.services as se

from osrs_discord_bot.services import ApiRequest
from requests.exceptions import Timeout

class MockAPI:
    
    def __init__(self, requests_mock):
        
        self.mock_base_url = requests_mock.get('https://test.com')
        self.mock_404_url = requests_mock.get('https://test.com/404', text='Not Found', status_code=404)
        self.mock_json_url = requests_mock.get('https://test.com/json', json= {'abc': 'def'})
        self.mock_text_url = requests_mock.get('https://test.com/text', text='resp')
        self.mock_timeout_url = requests_mock.get('https://test.com/timeout', exc=Timeout)
        self.mock_exchange_url = requests_mock.get('https://test.com/summary.json', 
            json={
                "4151":{"id":4151,"name":"Abyssal whip","members":True,
                "sp":120001,"buy_average":2864609,"buy_quantity":12,
                "sell_average":2859858,"sell_quantity":10,"overall_average":2862450,
                "overall_quantity":22}
                }
            )
        with open('test/wise_response.json') as json_file:
            wise_response = json.load(json_file)
        self.mock_tracker_url = requests_mock.get(
            'https://wiseoldman.net/api/players/username/test/gained?period=test',
            json=wise_response
            )
        with open('test/hiscore_response.txt') as text_file:
            hiscore_response = text_file.read()
        self.mock_hiscore_url = requests_mock.get('https://test.com/test_user',
            text=hiscore_response
            )
         

@pytest.fixture
def test_API_Request_Object(requests_mock):
    return ApiRequest('https://test.com')

@pytest.fixture
def mockAPI(requests_mock): 
    return MockAPI(requests_mock)
   

@pytest.mark.parametrize(
    'url,response', [
        ('/404', 404), ('/json', {'abc': 'def'}), ('/text', 'resp'),
        ('/timeout', 'timeout')
        ]
    )
def test_API_Request_Class(test_API_Request_Object, mockAPI, url, response):
    assert test_API_Request_Object.GET(url) == response

@pytest.mark.parametrize(
    "item,result",[
        ("1321931",({}, False)),
        ("Blood Rune", ({'565':'Blood rune'}, True))
    ]
)
def test_search_items(item, result):
    num = 1
    assert se.search_items(item, num) == result

def test_search_price(test_API_Request_Object, mockAPI):
    test_Response = {'4151':{'name':'Abyssal whip', 'buyPrice':2864609, 'sellPrice':2859858, 'margin':4751}}
    test_itemDict = se.search_items('Abyssal whip',1)[0]
    assert se.search_price(test_itemDict, test_API_Request_Object) == test_Response

@pytest.mark.parametrize(
    "chance,actions,message", [
        ('1/100', 100, r'63.40% chance of getting the drop within 100 actions.'),
        ('1/100', None, 'Please enter the number of actions.'),
        ('abc', None, 'Please enter drop rates in fractions or decimals and actions in integers.')
    ]
)
def test_chance_message(chance, actions, message):
    assert se.chance_message(chance, actions) == message
    

def test_ge_message(test_API_Request_Object, mockAPI):
    ge_message = se.ge_message(test_API_Request_Object, 'Abyssal whip')
    assert isinstance(ge_message, str) == True


def test_tracker_message(mockAPI):
    tracker_message = se.tracker_message('test', 'test')
    assert isinstance(tracker_message, str) == True


def test_hiscore_message(test_API_Request_Object, mockAPI):
    hiscore_message = se.hiscore_message(test_API_Request_Object, 'All', '/test_user')
    assert isinstance(hiscore_message, str) == True
