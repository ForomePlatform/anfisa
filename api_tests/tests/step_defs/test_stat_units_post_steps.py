import json

import pytest
from pytest_bdd import scenarios, when, parsers, given, then

from lib.api.ds_stat_api import DsStat
from lib.api.dtree_stat_api import DtreeStat
from lib.api.stat_units_api import StatUnits
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/stat_units-post.feature')


def find_incomplete(response):
    incomplete = ''
    for element in response.json()["stat-list"]:
        if incomplete == '':
            try:
                if element["incomplete"]:
                    incomplete = element["name"]
            except KeyError:
                continue
    return incomplete


@given(parsers.cfparse(
    'dtree_stat response with incomplete units is returned'), target_fixture='parameters')
def parameters(dataset):
    parameters = Constructor.dtree_stat_payload(ds=dataset, code='return False', no='0', tm='0')
    response = DtreeStat.post(parameters)
    incomplete = find_incomplete(response)

    parameters["rq_id"] = response.json()["rq-id"]
    parameters["units"] = '["' + incomplete + '"]'
    return parameters


@given(parsers.cfparse(
    'ds_stat response with incomplete units is returned'), target_fixture='parameters')
def parameters(dataset):
    parameters = Constructor.ds_stat_payload(ds=dataset, tm='0')
    response = DsStat.post(parameters)
    incomplete = find_incomplete(response)

    parameters["rq_id"] = response.json()["rq-id"]
    parameters["units"] = '["' + incomplete + '"]'
    parameters["code"] = ''
    return parameters


@when(parsers.cfparse('stat_units request is send'))
def stat_units_response(dataset, parameters):
    pytest.response = StatUnits.post(parameters)


@when(parsers.cfparse('stat_units request with "{ds:String}", "rq" and "{units:String}" parameters is send',
                      extra_types=EXTRA_STRING_TYPES))
def stat_units_response(ds, units, dataset, parameters):
    if ds == 'xl Dataset':
        ds = dataset
    if units == 'prepared unit':
        units = parameters["units"]
    parameters = Constructor.stat_units_payload(ds=ds, units=units, rq_id=parameters["rq_id"])
    pytest.response = StatUnits.post(parameters)


@then(parsers.cfparse('response body "rq-id" should match the one in request'))
def assert_rq_id(parameters):
    response_json = json.loads(pytest.response.text)
    assert response_json["rq-id"] == parameters["rq_id"]
