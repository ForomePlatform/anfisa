"""
This module contains DsList requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ds_list')


class DsList:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response

