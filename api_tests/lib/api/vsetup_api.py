
from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='vsetup')


class Vsetup:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
