

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='stat_func')


class StatFunc:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)