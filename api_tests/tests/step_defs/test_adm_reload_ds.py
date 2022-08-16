from pytest_bdd import scenarios, parsers, when, then
from lib.api.adm_reload_ds_api import AdmReloadDs
from lib.interfaces.interfaces import EXTRA_STRING_TYPES, EXTRA_INT_TYPES

scenarios('../features/adm_reload_ds-post.feature')


@when(parsers.cfparse('adm_reload_ds request with ds parameter is send'), target_fixture='adm_reload_ds_response')
def adm_reload_ds_response(dataset):
    parameters = {'ds': dataset}
    return AdmReloadDs.post(parameters)


@then(parsers.cfparse('response status should be {status:Number} OK', extra_types=EXTRA_INT_TYPES))
def assert_status(status, adm_reload_ds_response):
    assert adm_reload_ds_response.status_code == status


@then(parsers.cfparse('response body should be equal "{text:String} DatasetName"', extra_types=EXTRA_STRING_TYPES))
def assert_body(text, adm_reload_ds_response, dataset):
    text = '"%s %s"' % (text, dataset)
    assert adm_reload_ds_response.text == text
