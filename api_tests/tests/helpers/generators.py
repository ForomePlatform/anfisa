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
    def test_data(test_data_type):
        print('IIIIINNNNNNN GENERATOR')
        match test_data_type:
            case 'generated unique ws name':
                return Generator.unique_name('ws')
            case 'one space string':
                return ' '
            case 'empty string':
                return ''
            case 'space separated string':
                return f'{testDataPrefix} {Generator.random_literal_string(10)}'
            case 'duplicated ws name':
                duplicated_name = ''
                ds_dict = json.loads(DirInfo.get().content)["ds-dict"]
                for value in ds_dict.values():
                    if value['kind'] == 'ws':
                        duplicated_name = value['name']
                        break
                return duplicated_name
            case '251 literal string':
                return  Generator.random_literal_string(251)
            case 'numbers only string':
                return Generator.random_numeral_string(10)
            case 'symbols only string':
                return (int(time()) % 4 * '!') + (int(time()) % 6 * '@')
