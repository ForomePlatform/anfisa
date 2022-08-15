"""
This module contains Adm_drop_ds requests
"""

from lib.api.api_client import ApiRequest
apiRequest = ApiRequest(method='POST', path='adm_update')


class AdmUpdate:

    @staticmethod
    def post():
        response = apiRequest.request_without_params()
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
