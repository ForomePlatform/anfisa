import os
import requests
import json

SLACK_REPORT_SECRET = os.environ.get("SLACK_REPORT_SECRET")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID")
GITHUB_REF_NAME = os.environ.get("GITHUB_REF_NAME")
GITHUB_ACTOR = os.environ.get("GITHUB_ACTOR")
GITHUB_RUN_NUMBER = os.environ.get("GITHUB_RUN_NUMBER")
green_color = "#008000"
read_color = "#B22222"
_text = '_____________________________________________' + '\n'
_color = ''
_passing = 0
_failing = 0
_count = 0
link_repository = 'https://github.com/' + str(GITHUB_REPOSITORY) + '/pull/' + str(GITHUB_REF_NAME)
link_action = 'https://github.com/' + str(GITHUB_REPOSITORY) + '/actions/runs/' + str(GITHUB_RUN_ID)
header_repository =\
    'Autotests passed on <repository #' + GITHUB_REF_NAME + '|' + link_repository + '>, author: ' + GITHUB_ACTOR + '\n'
header_action =\
    'Test Run <ID #' + GITHUB_RUN_NUMBER + '|' + link_action + '>\n'


with open('cucumber-report.json') as json_file:
    data = json.load(json_file)


def scenario_result(elements):
    _result = ''
    _duration = 0
    for element in elements:
        _duration = _duration + element['result']['duration']
        if element['result']['status'] == 'passed':
            _result = 'PASSED'
        elif element['result']['status'] == 'failed':
            _result = 'FAILED'
            break
    return _result



for feature in data:
    param = '\n*Feature*: ' + feature['name']
    for scenario in feature['elements']:
        param = scenario_result(scenario['steps'])
        if param == 'PASSED':
            _passing = _passing + 1
        else:
            _failing = _failing + 1
            _text = _text + '*Scenario*: ' + scenario['name'] + ' ' + '[*' + param + '*]\n'
_count = _failing + _passing

result = \
        'Tests: ' + str(_count) + '\n' \
        'Passing: ' + str(_passing) + '\n' \
        'Failing: ' + str(_failing) + '\n' \

if _failing == 0:
    _color = green_color
    text = result
else:
    _color = read_color
    text = result + _text


print(text)
BASE_URL = "https://hooks.slack.com/services/" + str(SLACK_REPORT_SECRET)
params = {
    "channel": "#forome-api-tests-reports",
    "username": "webhookbot",
    "attachments": [
        {
            "color": _color,
            "text": text
        }
    ],
    "icon_emoji": ":ghost:"
}
response = requests.post(BASE_URL, json=params)
print(response)
