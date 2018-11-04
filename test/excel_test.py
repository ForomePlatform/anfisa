import unittest
from export.excel import *


class ExcelExportTest(unittest.TestCase):
    BASE_DIR = "/home/sboon/processtech/a-setup/data/"

    def test_export(self):
        mapping = read_mapping(self.BASE_DIR + 'SEQaBOO_output_template_0730.xlsx')
        for column in range(len(mapping)):
            print "{}: {}".format(column, mapping[column])

        export = ExcelExport(mapping=mapping)
        export.new()
        n = 30
        with open(self.BASE_DIR + 'bgm9001_wgs.json') as json_file:
            for i in range(0, n):
                line = json_file.readline()
                export.add_variant(json.loads(line))

        export.save('test.xlsx')
        self.assertEqual('foo'.upper(), 'FOO')


if __name__ == '__main__':
    unittest.main()
