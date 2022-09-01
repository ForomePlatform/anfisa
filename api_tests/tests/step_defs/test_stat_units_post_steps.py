import json

import pytest
from pytest_bdd import scenarios, when, parsers, given, then

from lib.api.dtree_stat_api import DtreeStat
from lib.api.stat_units_api import StatUnits
from tests.helpers.constructors import Constructor

scenarios('../features/stat_units-post.feature')


@given(parsers.cfparse(
    'ds_stat response with incomplete units is returned'), target_fixture='dtree_stat_incomplete')
def dtree_stat_incomplete(dataset):
    parameters = Constructor.dtree_stat_payload(ds=dataset, code='return False', no='0', tm='0')
    response = DtreeStat.post(parameters)

    incomplete = ''
    for element in response.json()["stat-list"]:
        if incomplete == '':
            try:
                if element["incomplete"]:
                    incomplete = element["name"]
            except KeyError:
                continue
    return {"rq_id": response.json()["rq-id"], "units": incomplete}


@when(parsers.cfparse('stat_units request is send'))
def stat_units_response(dataset, dtree_stat_incomplete):
    dtree_stat_incomplete["tm"] = '1'
    dtree_stat_incomplete["no"] = '0'
    dtree_stat_incomplete["ds"] = dataset
    dtree_stat_incomplete["units"] = '["' + dtree_stat_incomplete["units"] + '"]'

    pytest.response = StatUnits.post(dtree_stat_incomplete)


@then(parsers.cfparse('response body "rq-id" should match the one in request'))
def assert_rq_id(dtree_stat_incomplete):
    response_json = json.loads(pytest.response.text)
    assert response_json["rq-id"] == dtree_stat_incomplete["rq_id"]
