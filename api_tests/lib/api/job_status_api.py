"""
This module contains JobStatus requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='job_status')


class JobStatus:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
