"""
This module contains Adm_drop_ds requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='adm_drop_ds')


class Adm_drop_ds:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response

    @staticmethod
    def post(parameters):
        response = apiRequest.request_with_payload(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
