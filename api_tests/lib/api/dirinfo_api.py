"""
This module contains Dirinfo requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='GET', path='dirinfo')


class DirInfo:

    @staticmethod
    def get(success=True):
        response = apiRequest.request('')
        if success:
            assert response.status_code == 200
            print('responseCode:' + response.status_code.__str__())
            # pprint(response.json())
        else:
            assert response.status_code == 403
            print('responseCode:' + response.status_code.__str__())
            # print(response.text)
        return response
