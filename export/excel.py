import json
import openpyxl
from copy import copy

def cell_value(ws, row, column):
    v = ws.cell(row, column).value
    if (not v):
        return v
    return v.strip()

def read_mapping(path):
    wb = openpyxl.load_workbook(path, read_only = False)
    ws = wb["key"]
    if (cell_value(ws, 1, 1) != "Column"):
        raise Exception('First column must be called "Column". '
            'Worksheet "key" of file {}'.format(path))
    key_column = 1
    map_column = None
    for c in range(1, 100):
        if (cell_value(ws, 1, c) == "Mapping"):
            map_column = c
            break
    if (not map_column):
        raise Exception('Mapping column is not found in Worksheet key '
            'of file {}'.format(path))

    mapping = []
    for r in range(2, ws.max_row):
        cell = ws.cell(r, key_column)
        key = cell.value
        if (not key):
            continue

        key = key.strip()
        style = dict()
        style["fill"] = copy(cell.fill)
        style["font"] = copy(cell.font)
        style["alignment"] = copy(cell.alignment)
        style["number_format"] = copy(cell.number_format)
        style["border"] = copy(cell.border)
        value = cell_value(ws, r, map_column)
        if (not value):
            continue
        mapping.append((len(mapping)+1, key, value, style))

    return mapping

def find_value(array, key):
    if (array.get(key)):
        return array[key]
    for x in array.values():
        value = None
        if (isinstance(x, dict)):
            value = find_value(x, key)
        elif (isinstance(x, list)):
            for element in x:
                if (isinstance(element, dict)):
                    value = find_value(element, key)
                    if (value):
                        break
        if (value):
            if (isinstance(value, list)):
                value = ','.join([str(item) for item in value])
            return value

    return None

class ExcelExport:
    def __init__(self, fname = None, mapping = None):
        if fname:
            self.mapping = read_mapping(fname)
        else:
            self.mapping = mapping
        self.workbook = None
        self.column_widths = {}

    def new(self, title = None):
        self.workbook = openpyxl.Workbook()
        ws = self.workbook.active
        ws.title = title if title else "Variants"
        for column, key, value, style in self.mapping:
            if (not value):
                continue
            cell = ws.cell(row = 1, column = column, value = key)
            self.column_widths[cell.column] = len(key)
            for s in style:
                setattr(cell, s, style[s])

    def add_variant(self, data):
        ws = self.workbook.active
        row = ws.max_row + 1
        for column, _, key, style in self.mapping:
            if (not key):
                continue
            value = find_value(data, key)
            cell = ws.cell(row=row, column=column, value=value)
            if (isinstance(value, basestring)):
                self.column_widths[cell.column] = max(
                    self.column_widths[cell.column], len(value))
            for s in style:
                setattr(cell, s, style[s])

    def save(self, file):
        ws = self.workbook.active
        for column, width in self.column_widths.iteritems():
            ws.column_dimensions[column].width = width + 3
        self.workbook.save(filename = file)


if __name__ == '__main__':
    mapping = read_mapping('/Users/misha/Dropbox/'
        'bgm/CLIA/SEQaBOO_output_template_0730.xlsx')
    for column in range(len(mapping)):
        print "{}: {}".format(column, mapping[column])

    export = ExcelExport(mapping = mapping)
    export.new()
    n = 30
    with open('/Users/misha/projects/bgm/cases/'
            'bgm9001/bgm9001_wgs_candidates.json') as json_file:
        for i in range(0, n):
            line = json_file.readline()
            export.add_variant(json.loads(line))

    export.save("/Users/misha/projects/bgm/cases/bgm9001/test.xlsx")
