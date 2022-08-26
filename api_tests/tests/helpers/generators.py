import json
import random
import string
from time import gmtime, strftime, time
from lib.api.dirinfo_api import DirInfo


testDataPrefix = 'Autotest-'


class Generator:
    @staticmethod
    def unique_name(instance_type):
        return testDataPrefix + instance_type + strftime("-%y-%m-%d_%H-%M-%S", gmtime())

    @staticmethod
    def random_literal_string(length):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

    @staticmethod
    def random_numeral_string(length):
        return ''.join(random.choice(string.digits) for _ in range(length))

    @staticmethod
    def space_separated_string():
        return f'{testDataPrefix} {Generator.random_literal_string(10)}'

    @staticmethod
    def symbols_only_string():
        return (int(time()) % 4 * '!') + (int(time()) % 6 * '@')

    @staticmethod
    def tag(tag, tag_type):
        if tag_type == 'generated true Tag' or tag_type == 'generated false Tag':
            return '{"%(tag)s": true}' % {'tag': tag}
        elif tag_type == 'generated _note Tag':
            return '{"_note": "%(text)s"}' % {'text': tag}

    @staticmethod
    def code(code):
        match code:
            case 'valid':
                return 'return False'
            case 'invalid':
                return Generator.space_separated_string()
            case 'complex':
                return '''if Callers in {GATK_HOMOZYGOUS}:
    return True
return False'''
            case _:
                return code

    @staticmethod
    def test_data(test_data_type):
        match test_data_type:
            case 'unique ws name':
                return Generator.unique_name('ws')
            case 'one space string':
                return ' '
            case 'empty string':
                return ''
            case 'space separated string':
                return Generator.space_separated_string()
            case 'duplicated ws name':
                _dataset = ''
                ds_dict = json.loads(DirInfo.get().content)["ds-dict"]
                for value in ds_dict.values():
                    if value['kind'] == 'ws':
                        _dataset = value['name']
                        break
                assert _dataset != ''
                return _dataset
            case '251 literal string':
                return Generator.random_literal_string(251)
            case 'random literal string':
                return Generator.random_literal_string(10)
            case 'numbers only string':
                return Generator.random_numeral_string(10)
            case 'symbols only string':
                return Generator.symbols_only_string()
