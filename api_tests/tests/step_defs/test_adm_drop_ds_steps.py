from pytest_bdd import scenarios, given, parsers, when, then

from lib.api.adm_drop_ds_api import AdmDropDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from tests.helpers.generators import Generator
from tests.step_defs.conftest import derive_ws

scenarios('../features/adm_drop_ds-post.feature')


@given(parsers.cfparse('unique ws Dataset with appropriate name is derived from it'), target_fixture='derived_ws')
def derived_ws(dataset):
    return derive_ws(dataset)


@when(parsers.cfparse('adm_drop_ds requests with correct "ds" parameter is send'), target_fixture='adm_drop_ds_response')
def adm_drop_ds_response(derived_ws):
    return AdmDropDs.post({'ds': derived_ws})


@when(parsers.cfparse('adm_drop_ds requests with incorrect {ds:String} parameter is send', EXTRA_STRING_TYPES),
      target_fixture='adm_drop_ds_response')
def adm_drop_ds_response(ds):
    if 'generated' in ds:
        parameter = Generator.test_data(ds[10:])
        return AdmDropDs.post({'ds': parameter})
    else:
        return AdmDropDs.post({'ds': ds})


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, text, adm_drop_ds_response):
    assert adm_drop_ds_response.status_code == status


@then(parsers.cfparse('response body should be equal "{text:String} DatasetName"', extra_types=EXTRA_STRING_TYPES))
def assert_response_body(text, adm_drop_ds_response, derived_ws):
    print('adm_drop_ds_response.text',adm_drop_ds_response.text)
    text = f'"{text} {derived_ws}"'
    print('text', text)
    assert adm_drop_ds_response.text == text


@then(parsers.cfparse('response body should include {text:String}', extra_types=EXTRA_STRING_TYPES))
def assert_response_body(text, adm_drop_ds_response):
    print('text',text)
    print('adm_drop_ds_response.text',adm_drop_ds_response.text)
    assert text in adm_drop_ds_response.text

