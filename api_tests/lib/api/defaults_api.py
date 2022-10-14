

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='defaults')


class Defaults:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
