"""
This module contains Ds2ws requests
"""

from lib.api.api_client import ApiRequest

headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
apiRequest = ApiRequest(method='POST', path='ds2ws', headers=headers)


class Ds2ws:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
