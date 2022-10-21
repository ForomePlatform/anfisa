import json
import os
import time
import requests
testDataPrefix = 'Autotest-'
url = os.getenv("BASE_URL")
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

print('deleting test datasets created automatically')
print('deleting test dtrees created automatically')

ws_to_drop = []
response = requests.request(
            method='GET',
            url=url + 'dirinfo',
            params='dirinfo',
            headers=headers,
        )
print('responseCode:' + str(response.status_code))
print('responseBody:', response.text)

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
    responseWsDataset = requests.request(
        method='POST',
        url=url + 'adm_drop_ds',
        params={'ds': wsDataset},
        headers=headers,
    )
    print('responseCode:' + str(responseWsDataset.status_code))
    print('responseBody:', responseWsDataset.text)
    time.sleep(1)

dataset_list = json.loads(response.content)["ds-list"]
for ds in dataset_list:
    try:
        responseSet = requests.request(
            method='POST',
            url=url + 'dtree_set',
            params={"ds": ds, "code": 'return False'},
            headers=headers,
        )
        print('responseCode:' + str(responseSet.status_code))
        print('responseBody:', responseSet.text)
        dtree_list = responseSet.json()["dtree-list"]
        for dtree in dtree_list:
            if testDataPrefix + 'dtree' in dtree["name"]:
                instr = '["DTREE","DELETE","%(dtree)s"]' % {'dtree': dtree["name"]}
                responseSetInstr = requests.request(
                    method='POST',
                    url=url + 'dtree_set',
                    params={"ds": ds, "code": 'return False', "instr": instr},
                    headers=headers,
                )
                print('responseCode:' + str(responseSetInstr.status_code))
                print('responseBody:', responseSetInstr.text)
    except requests.exceptions.JSONDecodeError:
        continue
pass
