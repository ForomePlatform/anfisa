import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.tag_select_api import TagSelect
from tests.helpers.constructors import Constructor

scenarios('../features/tag_select-get.feature')

@when(parsers.cfparse(
    'tag_select request with correct "ds" parameter is send'))
def teg_select(dataset):
    parameters = Constructor.dtree_stat_payload(ds=dataset)
    pytest.response = TagSelect.get(parameters)
    return pytest.response