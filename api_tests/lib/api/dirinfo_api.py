"""
This module contains Dirinfo requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='GET', path='dirinfo')


class DirInfo:

    @staticmethod
    def get():
        return apiRequest.request('')
