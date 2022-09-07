import json
import random
import time

from lib.api.adm_drop_ds_api import AdmDropDs
from lib.api.dirinfo_api import DirInfo
from lib.api.ds2ws_api import Ds2ws
from lib.api.ds_stat_api import DsStat
from lib.api.dsinfo_api import Dsinfo
from lib.api.dtree_set_api import DtreeSet
from lib.api.job_status_api import JobStatus
from tests.helpers.constructors import Constructor
from tests.helpers.generators import testDataPrefix, Generator


def delete_auto_ws_datasets():
    ws_to_drop = []
    response = DirInfo.get()
    ds_dict = json.loads(response.content)["ds-dict"]
    for value in ds_dict.values():
        try:
            if testDataPrefix + 'ws' in value['name']:
                ws_to_drop.append(value['name'])
        except ValueError:
            continue
        except TypeError:
            continue
    for wsDataset in ws_to_drop:
        AdmDropDs.post({'ds': wsDataset})
        time.sleep(1)


def delete_auto_dtrees():
    response_dir_info = DirInfo.get()
    dataset_list = json.loads(response_dir_info.content)["ds-list"]
    for ds in dataset_list:
        response = DtreeSet.post({"ds": ds, "code": 'return False'})
        dtree_list = response.json()["dtree-list"]
        for dtree in dtree_list:
            if testDataPrefix + 'dtree' in dtree["name"]:
                instr = '["DTREE","DELETE","%(dtree)s"]' % {'dtree': dtree["name"]}
                DtreeSet.post({"ds": ds, "code": 'return False', "instr": instr})


def successful_string_to_bool(successful):
    if successful == "successful":
        return True
    else:
        return False


def number_of_ds_records(ds_name):
    response = Dsinfo.get({'ds': ds_name})
    return response.json()['total']


def xl_dataset(required_records=0):
    _dataset = ''
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.text)["ds-dict"]
    xl_list = []
    for value in ds_dict.values():
        try:
            if (value['kind'] == 'xl') and (number_of_ds_records(value['name']) > required_records):
                xl_list.append(value['name'])
        except TypeError:
            continue
        except ValueError:
            continue
    print('xl_list', xl_list)
    _dataset = random.choice(xl_list)
    print('selected xl dataset', _dataset)
    assert _dataset != ''
    return _dataset


def find_dataset(dataset):
    found = False
    response_dir_info = DirInfo.get()
    ds_dict = json.loads(response_dir_info.content)["ds-dict"]
    for value in ds_dict.values():
        try:
            if value['name'] == dataset:
                found = True
                break
        except ValueError:
            continue
        except TypeError:
            continue
    assert found


def prepare_filter(dataset):
    parameters = Constructor.ds_stat_payload(ds=dataset)
    response = DsStat.post(parameters)
    stat_list = json.loads(response.text)["stat-list"]
    result = ''
    for element in stat_list:
        try:
            if element['kind'] == 'enum':
                for variant in element["variants"]:
                    if (variant[1] < 3000) and (variant[1] > 3):
                        result = '''if %(stat_name)s in {%(variant_name)s}:
    return True
return False''' % {'stat_name': element["name"], 'variant_name': variant[0]}
                        return result
        except TypeError:
            continue
    return result


def ds_creation_status(task_id):
    parameters = {'task': task_id}
    job_status_response = JobStatus.post(parameters)
    for i in range(60):
        if (job_status_response.json()[1] == 'Done') or (job_status_response.json()[0] is None):
            break
        else:
            time.sleep(1)
            job_status_response = JobStatus.post(parameters)
            continue
    return job_status_response.json()[1]


def derive_ws(dataset, code='return False'):
    print('derive_ws', dataset, code)
    # Deriving ws dataset
    unique_ws_name = Generator.unique_name('ws')
    parameters = Constructor.ds2ws_payload(ds=dataset, ws=unique_ws_name, code=code)
    response = Ds2ws.post(parameters)

    # Checking creation
    assert ds_creation_status(response.json()['task_id']) == 'Done'
    return unique_ws_name