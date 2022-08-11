"""
This module contains Ds2ws requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ds2ws')


class Ds2ws:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response

    @staticmethod
    def post_with_payload(parameters):
        response = apiRequest.request_with_payload(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response


