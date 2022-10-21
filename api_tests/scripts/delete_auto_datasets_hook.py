from tests.helpers.functions import delete_auto_ws_datasets, delete_auto_dtrees

print('deleting test datasets created automatically')
delete_auto_ws_datasets()
print('deleting test dtrees created automatically')
delete_auto_dtrees()
