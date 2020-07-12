# test_functions.py

import pytest
import requests
import string
import functions as f

from functions import API_Request
from requests.exceptions import Timeout

class MockAPI:
    def __init__(self, requests_mock):
        self.mock_base_url = requests_mock.get('https://test.com')
        self.mock_404_url = requests_mock.get('https://test.com/404', text='Not Found', status_code=404)
        self.mock_json_url = requests_mock.get('https://test.com/json', json= {'abc': 'def'})
        self.mock_text_url = requests_mock.get('https://test.com/text', text='resp')
        self.mock_timeout_url = requests_mock.get('https://test.com/timeout', exc=Timeout)

@pytest.fixture
def test_API_Request_Object(requests_mock):
    requests_mock.get('https://test.com')
    return API_Request('https://test.com')

@pytest.fixture
def mockAPI(requests_mock): 
    return MockAPI(requests_mock)

def test_fraction2Float():
    assert f.fraction2Float('1/2') == 0.5
    assert f.fraction2Float('1.0/2.0') == 0.5

def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction2Float('abc')

def test_splitText():
    outputList = f.splitText(r'(.,.,.)', ',', '1,3,4 1,5,6 7,3,4')
    assert outputList == [['1','3','4'],['1','5','6'],['7','3','4']]    

def test_formatDiscord():
    assert f.formatDiscord('test') == '```test```'

def test_getResponse(requests_mock):
    requests_mock.get('https://test.com/404', text='Not Found', status_code=404)
    requests_mock.get('https://test.com/json', json= {'abc': 'def'})
    requests_mock.get('https://test.com/timeout', exc=Timeout)
    response_404 = f.getResponse('https://test.com/404')
    response_json = f.getResponse('https://test.com/json')
    response_timeout = f.getResponse('https://test.com/timeout')
    assert 404 == response_404
    assert {'abc': 'def'} == response_json
    assert 'timeout' == response_timeout

def test_API_Request_Class(test_API_Request_Object, mockAPI):
    assert test_API_Request_Object.GET('/404') == 404
    assert test_API_Request_Object.GET('/json') == {'abc': 'def'}
    assert test_API_Request_Object.GET('/text') == 'resp'
    assert test_API_Request_Object.GET('/timeout') == 'timeout'

def test_searchItems():
    num = 10
    assert f.searchItems('1321931', num) == ({}, False)
    assert len(f.searchItems('a', num)[0]) == num
    assert f.searchItems('Blood Rune', 1)[0] == {'565':'Blood rune'}

def test_searchPrice(requests_mock):
    test_json = {"4151":{"id":4151,"name":"Abyssal whip","members":True,
                "sp":120001,"buy_average":2864609,"buy_quantity":12,
                "sell_average":2859858,"sell_quantity":10,"overall_average":2862450,
                "overall_quantity":22}}
    mockURL = 'https://test.com/exchange'
    test_Response = {'4151':{'name':'Abyssal whip', 'buyPrice':2864609, 'sellPrice':2859858, 'margin':4751}}
    requests_mock.get(mockURL, json=test_json)
    test_itemDict = f.searchItems('Abyssal whip',1)[0]
    assert f.searchPrice(test_itemDict, mockURL) == test_Response