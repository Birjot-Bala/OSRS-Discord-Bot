# test_functions.py

import pytest
import requests
import string
import lib.discord_formatter as f
import lib.services as se

from lib.services import ApiRequest
from requests.exceptions import Timeout

class MockAPI:
    def __init__(self, requests_mock):
        
        self.mock_base_url = requests_mock.get('https://test.com')
        self.mock_404_url = requests_mock.get('https://test.com/404', text='Not Found', status_code=404)
        self.mock_json_url = requests_mock.get('https://test.com/json', json= {'abc': 'def'})
        self.mock_text_url = requests_mock.get('https://test.com/text', text='resp')
        self.mock_timeout_url = requests_mock.get('https://test.com/timeout', exc=Timeout)
        self.mock_exchange_url = requests_mock.get('https://test.com/exchange', 
            json={"4151":{"id":4151,"name":"Abyssal whip","members":True,
                "sp":120001,"buy_average":2864609,"buy_quantity":12,
                "sell_average":2859858,"sell_quantity":10,"overall_average":2862450,
                "overall_quantity":22}})

@pytest.fixture
def test_API_Request_Object(requests_mock):
    return ApiRequest('https://test.com')

@pytest.fixture
def mockAPI(requests_mock): 
    return MockAPI(requests_mock)

def test_formatSearch():
    assert f.formatSearch('a,2.5 G / ') == 'a25g'

def test_fraction2Float():
    assert f.fraction2Float('1/2') == 0.5
    assert f.fraction2Float('1.0/2.0') == 0.5

def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction2Float('abc')
   
def test_formatDiscord():
    assert f.formatDiscord('test') == '```test```'

def test_API_Request_Class(test_API_Request_Object, mockAPI):
    assert test_API_Request_Object.GET('/404') == 404
    assert test_API_Request_Object.GET('/json') == {'abc': 'def'}
    assert test_API_Request_Object.GET('/text') == 'resp'
    assert test_API_Request_Object.GET('/timeout') == 'timeout'

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
