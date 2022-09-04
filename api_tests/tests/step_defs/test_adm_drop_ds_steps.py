import pytest
from pytest_bdd import scenarios, parsers, when, then

from lib.api.adm_drop_ds_api import AdmDropDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/adm_drop_ds-post.feature')


@when(parsers.cfparse('adm_drop_ds requests with "ds" parameter is send'))
def adm_drop_ds_response(dataset):
    parameters = Constructor.arm_drop_ds_payload(ds=dataset)
    pytest.response = AdmDropDs.post(parameters)
    return pytest.response


@when(parsers.cfparse('adm_drop_ds requests with incorrect "{ds:String}" parameter is send', EXTRA_STRING_TYPES))
def adm_drop_ds_response(ds):
    parameters = Constructor.arm_drop_ds_payload(ds=ds)
    pytest.response = AdmDropDs.post(parameters)
    return pytest.response


@then(parsers.cfparse('response body should be equal "{text:String}" DatasetName', extra_types=EXTRA_STRING_TYPES))
def assert_response_body(text, dataset):
    text = f'"{text} {dataset}"'
    assert pytest.response.text == text


