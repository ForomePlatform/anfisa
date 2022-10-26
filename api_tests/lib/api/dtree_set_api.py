"""
This module contains DtreeSet requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_set')


class DtreeSet:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
