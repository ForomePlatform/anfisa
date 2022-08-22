import pytest
from pytest_bdd import scenarios, parsers, when
from lib.api.adm_update import AdmUpdate

scenarios('../features/adm_update-post.feature')


@when(parsers.cfparse('adm_update request is send'), target_fixture='adm_update_response')
def adm_update_response():
    pytest.response = AdmUpdate.post()
    return pytest.response
