# test_functions.py

import pytest
import requests
import string
import functions as f
from functions import API_Request

@pytest.fixture
def falseRequest():
    return requests.get('http://google.ca/404')

@pytest.fixture
def trueRequest():
    return requests.get('https://api.publicapis.org/health')

@pytest.fixture
def hiscoreRequest():
    return requests.get('http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=Bruhjeezy')

def test_fraction2Float():
    assert f.fraction2Float('1/2') == 0.5

def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction2Float('abc')

def test_splitText():
    outputList = f.splitText(r'(.,.,.)', ',', '1,3,4 1,5,6 7,3,4')
    assert outputList == [['1','3','4'],['1','5','6'],['7','3','4']]    

def test_getResponse_False(falseRequest):   
    response = f.getResponse(falseRequest)
    assert response == False

def test_getResponse_True(trueRequest):
    response = f.getResponse(trueRequest)
    assert isinstance(response, dict) == True

def test_API_Request_Class():
    testAPI = API_Request('https://api.publicapis.org')
    response = testAPI.GET('/health')
    assert testAPI.base_url == 'https://api.publicapis.org'
    assert isinstance(response, dict) == True 

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