from tests.helpers.generators import Generator


class Constructor:
    @staticmethod
    def ds2ws_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {
            'ds': kwargs['ds'] if 'ds' in kwargs else '',
            'ws': kwargs['ws'] if 'ws' in kwargs else '',
            'code': kwargs['code'] if 'code' in kwargs else '',
            'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
            'filter': kwargs['filter'] if 'filter' in kwargs else '',
            'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
            'force': kwargs['force'] if 'force' in kwargs else ''
        }

    @staticmethod
    def dtree_check_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'code': kwargs['code'] if 'code' in kwargs else ''
                }

    @staticmethod
    def ds_list_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {
            'ds': kwargs['ds'] if 'ds' in kwargs else '',
            'filter': kwargs['filter'] if 'filter' in kwargs else '',
            'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
            'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
            'code': kwargs['code'] if 'code' in kwargs else '',
            'no': kwargs['no'] if 'no' in kwargs else '',
            'smpcnt': kwargs['smpcnt'] if 'smpcnt' in kwargs else ''
        }
