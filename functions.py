import requests
import re
import string


regexPunc = re.compile('[%s]' % re.escape(string.punctuation))

def formatSearch(s):
    s = s.lower()
    return regexPunc.sub('', s)

def splitText(regex, delimiter, text):
    outputList = re.findall(regex, text)
    outputList = [i.split(delimiter) for i in outputList]
    return outputList

def fraction2Float(frac):
    # convert fractions to floats
    frac = frac.split('/')
    frac = float(frac[0])/float(frac[1])
    return frac

def formatUsername(args):
    # format username to string
    username = ''
    for arg in args:
        username = username + ' ' + str(arg)
    return username

def lookupHiscores(playerName):
    request = requests.get(
        'http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player=' + playerName)
    return request

def getResponse(target_url):
    # handle requests and acquire response
    request = requests.get(target_url)
    response = request.status_code
    if response == 404:
        return response
    else:
        try:
            message = request.json()
            return message
        except ValueError:
            return request.text #return raw text

def formatHiscore(username, oneSkill, skill_name, response):
    # format the response from OSRS Hiscore API
    skills = splitText(r'(.*,.*,.*)', ',', response)
    skill_dict = dict(zip(skill_name, skills))
    hiscore_message = f'```{username:<15s}{"Level":>10s}{"XP":>15s}```' + '```'
    if oneSkill == 'All':
        for s in skill_dict:
            hiscore_message = hiscore_message +\
                 f'\n{s:<15s}{skill_dict[s][1]:>10s}{skill_dict[s][2]:>15s}'
        hiscore_message = hiscore_message + '```'
    else:  
        hiscore_message = hiscore_message +\
             f'\n{oneSkill:<15s}{skill_dict[oneSkill][1]:>10s}{skill_dict[oneSkill][2]:>15s}' + '```'
    return hiscore_message

class API_Request:
    def __init__(self, base_url):
        self.base_url = base_url

    def GET(self, url):
        request_url = self.base_url + url
        response = getResponse(request_url)
        return response