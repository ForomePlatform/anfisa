

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='reccnt')


class Reccnt:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
