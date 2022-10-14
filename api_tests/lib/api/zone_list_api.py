"""
This module contains Zone_list requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='zone_list')


class ZoneList:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
