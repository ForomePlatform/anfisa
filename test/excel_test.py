import unittest

from export.excel import *


class ExcelExportTest(unittest.TestCase):
    BASE_DIR = "/Users/sboon/py/a-setup/data/"
    XLS_TEMPLATE = BASE_DIR + 'SEQaBOO_output_template_0730.xlsx'
    INPUT_JSON = BASE_DIR + 'bgm9001_wgs.json'

    def test_jsonpath(self):
        jsonpath_expr = parse('$.."Gene(s)"')
        with open(self.INPUT_JSON) as json_file:
            line = json_file.readline()
            for match in jsonpath_expr.find(json.loads(line)):
                print match.value

    def test_export(self):
        mapping = read_mapping(self.XLS_TEMPLATE)
        for column in range(len(mapping)):
            print "{}: {}".format(column, mapping[column])

        export = ExcelExport(mapping=mapping)
        export.new()
        with open(self.INPUT_JSON) as json_file:
            for idx, line in enumerate(json_file):
                export.add_variant(json.loads(line))
                if idx> 0 and idx % 100 == 0:
                    print "export lines: {}".format(idx)
            print "total: {}".format(idx)

        export.save('test.xlsx')


if __name__ == '__main__':
    unittest.main()
