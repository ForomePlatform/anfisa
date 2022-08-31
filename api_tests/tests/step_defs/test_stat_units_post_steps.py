import pytest
from pytest_bdd import scenarios, when, parsers, given

from lib.api.dtree_stat_api import DtreeStat
from tests.helpers.constructors import Constructor

scenarios('../features/stat_units-post.feature')


@given(parsers.cfparse(
    'ds_stat response with incomplete units is returned'), target_fixture='dtree_stat')
def dtree_stat_incomplete(dataset, code, no, tm):
    parameters = Constructor.dtree_stat_payload(ds=dataset, code=code, no=no, tm=tm)
    response = DtreeStat.post(parameters)
    for element in response.json()["stat-list"]:
        print('element', element["incomplete"])
    return 1


@when(parsers.cfparse(
    'stat_units request is send'))
def dtree_stat_incomplete(dataset, code, no, tm):
    parameters = Constructor.dtree_stat_payload(ds=dataset, code=code, no=no, tm=tm)
    pytest.response = DtreeStat.post(parameters)