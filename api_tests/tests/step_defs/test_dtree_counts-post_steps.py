import pytest
from pytest_bdd import scenarios, parsers, when, given
from lib.api.dtree_counts_api import DtreeCounts
from lib.api.dtree_set_api import DtreeSet
from tests.helpers.constructors import Constructor
from tests.helpers.generators import Generator

scenarios('../features/dtree_counts-post.feature')


@given(parsers.cfparse('"dtree_set" request with "xl Dataset" and "code" parameters is send'),
       target_fixture='dtree_set_response')
def dtree_set_response(dataset):
    code = Generator.code('valid')
    parameters = Constructor.dtree_set_payload(ds=dataset, code=code)
    response = DtreeSet.post(parameters)
    return response.json()


@when(parsers.cfparse('"dtree_counts" request with correct parameters is send'))
def dtree_counts_response(dataset, dtree_set_response):
    rq_id = dtree_set_response["rq-id"]
    code = dtree_set_response["code"]
    parameters = Constructor.dtree_counts_payload(ds=dataset, rq_id=rq_id, code=code, tm='1', points='[0]')
    pytest.response = DtreeCounts.post(parameters)
    return pytest.response
