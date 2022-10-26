

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='panels')


class Panels:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
