
from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='tab_report')


class TabReport:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
