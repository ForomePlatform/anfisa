

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='single_cnt')


class SingleCnt:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
