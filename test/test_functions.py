# test_functions.py

import pytest
import requests
import string
import functions as f

from functions import API_Request

class MockAPI:
    def __init__(self, requests_mock):
        self.mock_base_url = requests_mock.get('https://test.com')
        self.mock_404_url = requests_mock.get('https://test.com/404', text='Not Found', status_code=404)
        self.mock_json_url = requests_mock.get('https://test.com/json', json= {'abc': 'def'})
        self.mock_text_url = requests_mock.get('https://test.com/text', text='resp')

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

def test_getResponse_False(requests_mock):
    requests_mock.get('https://test.com/404', text='Not Found', status_code=404)  
    response = f.getResponse('https://test.com/404')
    assert 404 == response

def test_getResponse_True(requests_mock):
    requests_mock.get('https://test.com/json', json= {'abc': 'def'})
    response = f.getResponse('https://test.com/json')
    assert response == {'abc': 'def'}
    
def test_API_Request_Class(test_API_Request_Object, mockAPI):
    assert test_API_Request_Object.GET('/404') == 404
    assert test_API_Request_Object.GET('/json') == {'abc': 'def'}
    assert test_API_Request_Object.GET('/text') == 'resp'


# def test_API_Request_Class():
#     testAPI = API_Request('https://api.publicapis.org')
#     response = testAPI.GET('/health')
#     assert testAPI.base_url == 'https://api.publicapis.org'
#     assert isinstance(response, dict) == True 

# def test_formatHiscore(hiscoreRequest):

#     skill_name = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
#       'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking', 'Crafting', 'Smithing',
#       'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
#       'Farming', 'Runecraft', 'Hunter', 'Construction']

#     hiscoreRequest = ('128066,1956,91715105 373424,86,3742254 312833,87,4353424 360173,95,8832013 '
#     '299889,97,10728139 331040,94,8171902 160322,80,2041426 310718,94,7988204 308614,85,3263474 '
#     '188035,85,3260693 357705,80,2038511 229155,83,2678792 251877,85,3396807 193664,80,2007411 '
#     '133656,83,2676129 213443,78,1648291 152229,81,2223644 148548,79,1815842 156557,80,1988539 '
#     '132177,93,7363932 152191,88,4615805 87206,80,2005365 148772,80,2111186 119689,83,2763322 '
#     '-1,-1 -1,-1 -1,-1 140070,172 197677,4 127442,20 179204,29 110254,101 168955,6 46740,12 '
#     '-1,-1 -1,-1 -1,-1 163181,142 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 '
#     '121219,60 52264,385 93310,116 -1,-1 -1,-1 -1,-1 -1,-1 54994,40 -1,-1 -1,-1 67337,1449 '
#     '-1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 -1,-1 61186,28 -1,-1 -1,-1 -1,-1 71270,171 -1,-1 '
#     '-1,-1 -1,-1 -1,-1 176101,68 225712,146 -1,-1 -1,-1')
    
#     hiscore_message = formatHiscore('Bruhjeezy', 'All', skill_name, hiscoreRequest)
#     assert hiscore_message ==