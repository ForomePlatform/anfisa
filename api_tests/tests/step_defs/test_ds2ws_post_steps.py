import json
from jsonschema import validate
from pytest_bdd import scenarios, parsers, given, when, then
from lib.api.ds2ws_api import Ds2ws
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_INT_TYPES
from lib.api.dirinfo_api import DirInfo
from tests.helpers.generators import Generator
from lib.jsonschema.ds2ws_schema import ds2ws_schema

scenarios('../features/ds2ws-post.feature')

dataset = ''
uniqueWsName = ''
conditions = ''
filter = ''
code = ''
dtree = ''
force = ''
response = ''


@given(parsers.cfparse('{dsType:String} Dataset is uploaded and processed by the system',extra_types=EXTRA_STRING_TYPES))
def getRandomDatasetName(dsType):
    global dataset
    response = DirInfo.get()
    dsDict = json.loads(response.content)["ds-dict"]
    for value in dsDict.values():
        if value['kind'] == dsType:
            dataset = value['name']
            break
    assert dataset != ''
    return dataset

@given(parsers.cfparse('unique {type:String} Dataset name is generated',extra_types=EXTRA_STRING_TYPES))
def generateUniqueName(type):
    global uniqueWsName
    uniqueWsName = Generator.uniqueName(type)
    assert uniqueWsName != ''
    return uniqueWsName

@when(parsers.cfparse('ds2ws request with ds and ws parameters is send'))
def ds2wsRequest():
    global dataset, uniqueWsName, code, conditions, filter, dtree, force, response
    parameters = {
        'ds': dataset,
        'ws': uniqueWsName,
        'code': code,
        'conditions': conditions,
        'filter': filter,
        'dtree': dtree,
        'force': force,
        }
    response = Ds2ws.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} OK',extra_types=EXTRA_INT_TYPES))
def assertStatus(status):
    global response
    assert response.status_code == status

@then(parsers.cfparse('response body schema should be valid'))
def assertJsonSchema():
    global response
    validate(response.json(), ds2ws_schema)