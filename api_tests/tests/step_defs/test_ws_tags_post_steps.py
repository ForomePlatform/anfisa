import pytest
from pytest_bdd import scenarios, parsers, when

from lib.api.ws_tags_api import WsTags
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/ws_tags-post.feature')


@when(parsers.cfparse('ws_tags request with "{ws:String}" and "{rec:String}" is send',extra_types=EXTRA_STRING_TYPES))
def ws_tags_response(ws_less_9000_rec, ws, rec):
    if ws == 'generated ws':
        ws = ws_less_9000_rec
    parameters = Constructor.ws_tags_payload(ds=ws, rec=rec)
    pytest.response = WsTags.post(parameters)
