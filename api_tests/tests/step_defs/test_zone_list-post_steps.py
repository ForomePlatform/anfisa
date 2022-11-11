import pytest
import random
from pytest_bdd import scenarios, when, parsers, given
from lib.api.zone_list_api import ZoneList
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.constructors import Constructor

scenarios('../features/zone_list-post.feature')


@given(parsers.cfparse('"{zone_type}" zone is selected', extra_types=EXTRA_STRING_TYPES), target_fixture='random_zone')
def random_zone(ws_less_9000_rec, zone_type):
    parameters = Constructor.zone_list_payload(ds=ws_less_9000_rec)
    response = ZoneList.post(parameters)
    zone_list = []
    for zone_descriptor in response.json():
        zone_list.append(zone_descriptor["zone"])
    match zone_type:
        case 'random':
            return random.choice(zone_list)
        case 'first':
            return zone_list[0]


@when(parsers.cfparse('zone_list request with "{ds:String}" parameter is send', extra_types=EXTRA_STRING_TYPES))
def zone_list_response(dataset, ws_less_9000_rec, ds):
    if ds == 'xl Dataset':
        ds = dataset
    elif ds == 'ds':
        ds = ws_less_9000_rec
    parameters = Constructor.zone_list_payload(ds=ds)
    pytest.response = ZoneList.post(parameters)


@when(parsers.cfparse('zone_list request with "ds", "zone" parameters is send'))
def zone_list_response(ws_less_9000_rec, random_zone):
    parameters = Constructor.zone_list_payload(ds=ws_less_9000_rec, zone=random_zone)
    pytest.response = ZoneList.post(parameters)

