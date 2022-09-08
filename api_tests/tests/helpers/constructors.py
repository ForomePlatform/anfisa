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
    def csv_export_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'schema': kwargs['schema'] if 'schema' in kwargs else ''
                }

    def job_status_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'task': kwargs['task'] if 'task' in kwargs else '',
                }

    @staticmethod
    def adm_reload_ds(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''}

    @staticmethod
    def arm_drop_ds_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''
                }

    @staticmethod
    def ws_tags_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'rec': kwargs['rec'] if 'rec' in kwargs else '',
                'tags': kwargs['tags'] if 'tags' in kwargs else '',
                }

    @staticmethod
    def tag_select_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''
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

    @staticmethod
    def dtree_stat_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:4] == 'gen.':
                kwargs[key] = Generator.test_data(value[5:])
        return {
            'ds': kwargs['ds'] if 'ds' in kwargs else '',
            'code': kwargs['code'] if 'code' in kwargs else '',
            'no': kwargs['no'] if 'no' in kwargs else '',
            'tm': kwargs['tm'] if 'tm' in kwargs else ''
        }

    @staticmethod
    def ds_stat_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tm': kwargs['tm'] if 'tm' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'ctx': kwargs['ctx'] if 'ctx' in kwargs else '',
                'actsym': kwargs['actsym'] if 'actsym' in kwargs else '',
                'instr': kwargs['instr'] if 'instr' in kwargs else ''
                }

    @staticmethod
    def stat_units_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:4] == 'gen.':
                kwargs[key] = Generator.test_data(value[5:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tm': kwargs['tm'] if 'tm' in kwargs else '',
                'rq_id': kwargs['rq_id'] if 'rq_id' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
                'code': kwargs['code'] if 'code' in kwargs else '',
                'no': kwargs['no'] if 'no' in kwargs else '',
                'ctx': kwargs['ctx'] if 'ctx' in kwargs else '',
                'units': kwargs['units'] if 'units' in kwargs else ''
                }

    @staticmethod
    def dtree_set_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:4] == 'gen.':
                kwargs[key] = Generator.test_data(value[5:])
        return {
            'ds': kwargs['ds'] if 'ds' in kwargs else '',
            'tm': kwargs['tm'] if 'tm' in kwargs else '',
            'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
            'code': kwargs['code'] if 'code' in kwargs else '',
            'actsym': kwargs['actsym'] if 'actsym' in kwargs else '',
            'instr': kwargs['instr'] if 'instr' in kwargs else ''
        }

    @staticmethod
    def ws_list_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'zone': kwargs['zone'] if 'zone' in kwargs else '',
                }

    @staticmethod
    def zone_list_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'zone': kwargs['zone'] if 'zone' in kwargs else ''
                }

    @staticmethod
    def single_cnt_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'record': kwargs['record'] if 'record' in kwargs else ''
                }

    @staticmethod
    def defaults_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''
                }

    @staticmethod
    def reccnt_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'rec': kwargs['rec'] if 'rec' in kwargs else '',
                'details': kwargs['details'] if 'details' in kwargs else '',
                'samples': kwargs['samples'] if 'samples' in kwargs else ''
                }

    @staticmethod
    def recdata_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'rec': kwargs['rec'] if 'rec' in kwargs else ''
                }

    @staticmethod
    def tab_report_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'seq': kwargs['seq'] if 'seq' in kwargs else '',
                'schema': kwargs['schema'] if 'schema' in kwargs else '',
                }

    @staticmethod
    def vsetup_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''
                }

    @staticmethod
    def solutions_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else ''
                }

    @staticmethod
    def stat_func_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'rq_id': kwargs['rq_id'] if 'rq_id' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
                'code': kwargs['code'] if 'code' in kwargs else '',
                'no': kwargs['no'] if 'no' in kwargs else '',
                'unit': kwargs['unit'] if 'unit' in kwargs else '',
                'param': kwargs['param'] if 'param' in kwargs else '',
                'ctx': kwargs['ctx'] if 'ctx' in kwargs else '',
                }

    @staticmethod
    def dtree_counts_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'rq_id': kwargs['rq_id'] if 'rq_id' in kwargs else '',
                'tm': kwargs['tm'] if 'tm' in kwargs else '',
                'points': kwargs['points'] if 'points' in kwargs else '',
                'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
                'code': kwargs['code'] if 'code' in kwargs else ''
                }

    @staticmethod
    def dtree_cmp_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'other': kwargs['other'] if 'other' in kwargs else '',
                'dtree': kwargs['dtree'] if 'dtree' in kwargs else '',
                'code': kwargs['code'] if 'code' in kwargs else ''
                }

    @staticmethod
    def export_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'zone': kwargs['zone'] if 'zone' in kwargs else ''
                }

    @staticmethod
    def export_ws_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'support': kwargs['support'] if 'support' in kwargs else '',
                'doc': kwargs['doc'] if 'doc' in kwargs else ''
                }

    @staticmethod
    def import_ws_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'name': kwargs['name'] if 'name' in kwargs else '',
                'file': kwargs['file'] if 'file' in kwargs else ''
                }

    @staticmethod
    def panels_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tp': kwargs['tp'] if 'tp' in kwargs else '',
                'instr': kwargs['instr'] if 'instr' in kwargs else ''
                }

    @staticmethod
    def symbols_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tp': kwargs['tp'] if 'tp' in kwargs else '',
                'list': kwargs['list'] if 'list' in kwargs else '',
                'panel': kwargs['panel'] if 'panel' in kwargs else '',
                'pattern': kwargs['pattern'] if 'pattern' in kwargs else ''
                }

    @staticmethod
    def symbols_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tp': kwargs['tp'] if 'tp' in kwargs else '',
                'list': kwargs['list'] if 'list' in kwargs else '',
                'panel': kwargs['panel'] if 'panel' in kwargs else '',
                'pattern': kwargs['pattern'] if 'pattern' in kwargs else ''
                }

    @staticmethod
    def symbol_info_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tp': kwargs['tp'] if 'tp' in kwargs else '',
                'symbol': kwargs['symbol'] if 'symbol' in kwargs else ''
                }

    @staticmethod
    def macro_tagging_payload(**kwargs):
        for key, value in kwargs.items():
            if value[:9] == 'generated':
                kwargs[key] = Generator.test_data(value[10:])
        return {'ds': kwargs['ds'] if 'ds' in kwargs else '',
                'tag': kwargs['tag'] if 'tag' in kwargs else '',
                'off': kwargs['off'] if 'off' in kwargs else '',
                'filter': kwargs['filter'] if 'filter' in kwargs else '',
                'conditions': kwargs['conditions'] if 'conditions' in kwargs else '',
                'zone': kwargs['zone'] if 'zone' in kwargs else ''
                }