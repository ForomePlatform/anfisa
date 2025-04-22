"""
This module contains AdmReloadDs requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='adm_reload_ds')


class AdmReloadDs:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
