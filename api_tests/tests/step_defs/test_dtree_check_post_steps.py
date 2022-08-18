import pytest
from pytest_bdd import scenarios, parsers, when
from lib.api.dtree_check_api import DtreeCheck
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/dtree_check-post.feature')


@when(parsers.cfparse('dtree_check request with {code:String} and {ds:String} is send', extra_types=EXTRA_STRING_TYPES),
      target_fixture='dtree_check_response')
def dtree_check_response(code, ds, dataset):
    dataset_name = dataset if ds == 'xl dataset' else ds
    parameters = Constructor.dtree_check_payload(ds=dataset_name, code=code)
    pytest.response = DtreeCheck.post(parameters)
    return pytest.response




