import os
import requests
import json

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


text = ''

_passing = 0
_failing = 0
_count = 0
for feature in data:
    param = '\n*Feature*: ' + feature['name']
    text = text + param + '\n'
    for scenario in feature['elements']:
        param = scenario_result(scenario['steps'])
        text = text + '       *Scenario*: ' + scenario['name'] + ' ' + '[*' + param + '*]\n'
        if param == 'PASSED':
            _passing = _passing + 1
        else:
            _failing = _failing + 1
_count = _failing + _passing
print(text)
result = \
        '______________________________\n' \
        'Tests: ' + _count.__str__() + '\n' \
        'Passing: ' + _passing.__str__() + '\n' \
        'Failing: ' + _failing.__str__() + '\n'

print(result)

text = text + '\n\n' + result


SLACK_REPORT_SECRET = os.environ.get("SLACK_REPORT_SECRET")
BASE_URL = "https://hooks.slack.com/services/" + SLACK_REPORT_SECRET.__str__()
params = {"channel": "#forome-api-tests-reports", "username": "webhookbot", "text": text, "icon_emoji": ":ghost:"}
response = requests.post(BASE_URL, json=params)
print(response)
