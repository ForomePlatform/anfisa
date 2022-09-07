# because there is no after all hook in pytest-bdd
import time

from pytest_bdd import scenarios, then, parsers
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.step_defs.conftest import delete_auto_ws_datasets, delete_auto_dtrees

scenarios('../features/аfter_all_hook.feature')


@then(parsers.cfparse('"{data_type:String}" should be deleted', extra_types=EXTRA_STRING_TYPES))
def delete_test_data(data_type):
    time.sleep(7)
    match data_type:
        case 'ws datasets':
            delete_auto_ws_datasets()
        case 'dtrees':
            delete_auto_dtrees()
