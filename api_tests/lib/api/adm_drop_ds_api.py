"""
This module contains Adm_drop_ds requests
"""

from lib.api.api_client import ApiRequest
headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
apiRequest = ApiRequest(method='POST', path='adm_drop_ds', headers=headers)


class AdmDropDs:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
