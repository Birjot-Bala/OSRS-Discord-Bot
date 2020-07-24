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
        self.mock_exchange_url = requests_mock.get('https://test.com/exchange', 
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
            'https://test.com/players/username/test/gained?period=test',
            json=wise_response
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

def test_searchItems():
    num = 10
    assert se.searchItems('1321931', num) == ({}, False)
    assert len(se.searchItems('a', num)[0]) == num
    assert se.searchItems('Blood Rune', 1)[0] == {'565':'Blood rune'}

def test_searchPrice(test_API_Request_Object, mockAPI):
    test_API_Request_Object.base_url = 'https://test.com/exchange'
    test_Response = {'4151':{'name':'Abyssal whip', 'buyPrice':2864609, 'sellPrice':2859858, 'margin':4751}}
    test_itemDict = se.searchItems('Abyssal whip',1)[0]
    assert se.searchPrice(test_itemDict, test_API_Request_Object) == test_Response

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
    test_API_Request_Object.base_url = 'https://test.com/exchange'
    ge_message = se.ge_message(test_API_Request_Object, 'Abyssal whip')
    assert isinstance(ge_message, str) == True

def test_tracker_message(test_API_Request_Object, mockAPI):
    tracker_message = se.tracker_message(test_API_Request_Object, 'test', 'test')
    assert isinstance(tracker_message, str) == True

