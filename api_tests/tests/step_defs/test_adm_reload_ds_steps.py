from pytest_bdd import scenarios, parsers, when, then
from lib.api.adm_reload_ds_api import AdmReloadDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_TYPES
from tests.helpers.generators import Generator

scenarios('../features/adm_reload_ds-post.feature')

unique_name = ''


@when(parsers.cfparse('adm_reload_ds request with {ds:String} parameter is send', extra_types=EXTRA_STRING_TYPES),
      target_fixture='adm_reload_ds_response')
def adm_reload_ds_response(dataset):
    parameters = {'ds': dataset}
    return AdmReloadDs.post(parameters)


@when(parsers.cfparse('adm_reload_ds request with incorrect {ds:String} parameter is send',
                      extra_types=EXTRA_STRING_TYPES),
      target_fixture='adm_reload_ds_response')
def adm_reload_ds_response(ds):
    global unique_name
    match ds:
        case 'Empty string':
            dataset_name = ''
        case '<Non registered dataset>':
            unique_name = Generator.unique_name('nonRegistered')
            dataset_name = unique_name
        case other:
            dataset_name = ds
    parameters = {'ds': dataset_name}
    return AdmReloadDs.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} {text:String}', extra_types=EXTRA_TYPES))
def assert_status(status, adm_reload_ds_response, text):
    assert adm_reload_ds_response.status_code == status


@then(parsers.cfparse('response body should be equal "{text:String}"', extra_types=EXTRA_STRING_TYPES))
def assert_body(text, adm_reload_ds_response, dataset):
    text = '"%s %s"' % (text[:8], dataset)
    assert adm_reload_ds_response.text == text


@then(parsers.cfparse('response body should contain {error:String}', extra_types=EXTRA_STRING_TYPES))
def assert_string_error(error, adm_reload_ds_response):
    global unique_name
    if "<Non registered dataset>" in error:
        error = error[:11] + unique_name

    response = adm_reload_ds_response.text
    assert error in response
