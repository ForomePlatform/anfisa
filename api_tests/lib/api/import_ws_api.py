

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='import_ws')


class ImportWs:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)