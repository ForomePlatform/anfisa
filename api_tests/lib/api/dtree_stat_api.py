"""
This module contains Dtree_stat requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_stat')


class DtreeStat:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
