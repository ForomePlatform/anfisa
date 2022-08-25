import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ws_tags-post.feature')


@when(parsers.cfparse('ws_tags request with "{ws:String}" and "{rec:String}" is send',extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(dataset, ws, rec):
    print('\nws', ws)
    if ws == 'generated ws':
        ws = dataset
    print('\nws', ws)
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec)
    print('parameters', parameters)
    pytest.response = WsTags.post(parameters)
