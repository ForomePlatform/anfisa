import pytest
from pytest_bdd import scenarios, parsers, when, given

from lib.api.tag_select_api import TagSelect
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor
from tests.step_defs.conftest import derive_ws

scenarios('../features/tag_select-get.feature')


@given(parsers.cfparse('ws Dataset is derived from it'), target_fixture='derived_ws')
def derived_ws(dataset):
    return derive_ws(dataset)


@when(parsers.cfparse(
    'tag_select request with "{ds:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def teg_select(dataset, ds):
    if (ds == 'ws Dataset') or (ds == 'xl Dataset'):
        ds = dataset
    parameters = Constructor.tag_select_payload(ds=ds)
    pytest.response = TagSelect.get(parameters)
    return pytest.response


@when(parsers.cfparse(
    'tag_select request with specified "ds" parameter is send'))
def teg_select(derived_ws):
    parameters = Constructor.tag_select_payload(ds=derived_ws)
    pytest.response = TagSelect.get(parameters)
    return pytest.response


