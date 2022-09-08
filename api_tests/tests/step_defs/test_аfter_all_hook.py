import time

from pytest_bdd import scenarios, then, parsers
from lib.interfaces.interfaces import EXTRA_STRING_TYPES
from tests.helpers.functions import delete_auto_ws_datasets, delete_auto_dtrees

scenarios('../features/аfter_all_hook.feature')


@then(parsers.cfparse('"{data_type:String}" should be deleted', extra_types=EXTRA_STRING_TYPES))
def delete_test_data(data_type):
    '''time.sleep(7)
    match data_type:
        case 'ws datasets':
            print('deleting test datasets created automatically')
            delete_auto_ws_datasets()
        case 'dtrees':
            print('deleting test dtrees created automatically')
            delete_auto_dtrees()'''
    files_list = ['macro_tagging', 'symbol_info', 'symbols', 'panels', 'import_ws', 'export_ws', 'export', 'dtree_cmp', 'dtree_counts', 'stat_func', 'solutions', 'vsetup', 'tab_report', 'recdata', 'reccnt', 'defaults', 'single_cnt']
    for file_name in files_list:
        print('hello')

        f = open("./lib/api/"+file_name+"_api.py", "w")
        text = f'''

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='{file_name}')


class {file_name.replace('_','').capitalize()}:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response'''
        f.write(text)
        f.close()