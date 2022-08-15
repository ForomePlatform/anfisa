from pytest_bdd import scenarios, parsers, when, then
from lib.api.adm_update import AdmUpdate
from lib.interfaces.interfaces import EXTRA_INT_TYPES, EXTRA_STRING_TYPES

scenarios('../features/adm_update-post.feature')


@when(parsers.cfparse('adm_update request is send'), target_fixture='adm_update_response')
def adm_update_response():
    return AdmUpdate.post()


@then(parsers.cfparse('response status should be {status:Number} OK', extra_types=EXTRA_INT_TYPES))
def assert_status(status, adm_update_response):
    assert adm_update_response.status_code == status


@then(parsers.cfparse('response body should be equal {text:String}', extra_types=EXTRA_STRING_TYPES))
def assert_status(text, adm_update_response):
    assert adm_update_response.text == text
