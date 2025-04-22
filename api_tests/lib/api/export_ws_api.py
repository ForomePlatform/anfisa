

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='export_ws')


class ExportWs:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)