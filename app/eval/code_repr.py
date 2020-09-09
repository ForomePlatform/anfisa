#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json
from io import StringIO

from forome_tools.ident import checkIdentifier
#===============================================
def formatIfCode(cond_data):
    cond_kind = cond_data[0]
    if cond_kind not in ("or", "and"):
        rep = StringIO()
        rep.write('if ')
        _reprConditionCode(cond_data, rep, False)
        rep.write(':')
        return _formatRep(rep.getvalue(), 0, 2)
    assert len(cond_data) > 2
    rep = StringIO()
    rep.write('if (')
    _reprConditionCode(cond_data[1], rep, True)
    rep.write(' ' + cond_kind)
    ret = [_formatRep(rep.getvalue(), 0, 2)]
    for idx in range(2, len(cond_data)):
        rep = StringIO()
        _reprConditionCode(cond_data[idx], rep, True)
        if idx + 1 < len(cond_data):
            rep.write(' ' + cond_kind)
        else:
            rep.write('):')
        ret.append(_formatRep(rep.getvalue(), 1, 2))
    return "\n".join(ret)

#===============================================
def formatConditionCode(cond_data):
    rep = StringIO()
    _reprConditionCode(cond_data, rep, False)
    return rep.getvalue().replace('\f', ' ')


#===============================================
def _reprConditionCode(cond_data, output, group_mode):
    cond_kind = cond_data[0]
    if cond_kind in ("or", "and"):
        if group_mode:
            output.write('(')
        q_first = True
        for sub_cond_data in cond_data[1:]:
            if q_first:
                q_first = False
            else:
                output.write(" " + cond_kind + "\f")
            _reprConditionCode(sub_cond_data, output, True)
        if group_mode:
            output.write(')')
        return
    if cond_kind == "not":
        output.write('not ')
        _reprConditionCode(cond_data[1], output, True)
        return
    if cond_kind == "numeric":
        if group_mode:
            output.write('(')
        unit_name, bounds = cond_data[1:]
        if bounds[0] == bounds[2]:
            output.write('%s == %s' % (unit_name, str(bounds[0])))
        else:
            seq = []
            if bounds[0] is not None:
                seq.append(str(bounds[0]))
                seq.append('<=' if bounds[1] else '<')
            seq.append(unit_name)
            if bounds[2] is not None:
                seq.append('<=' if bounds[3] else '<')
                seq.append(str(bounds[2]))
            assert len(seq) > 1
            output.write(' '.join(seq))
        if group_mode:
            output.write(')')
        return
    if cond_kind == "enum":
        if group_mode:
            output.write('(')
        unit_name, op_mode, values = cond_data[1:]
        _reprEnumCase(unit_name, op_mode, values, output)
        if group_mode:
            output.write(')')
        return
    if cond_kind == "func":
        if group_mode:
            output.write('(')
        unit_name, op_mode, values, func_info = cond_data[1:]
        output.write(unit_name + '(')
        q_first = True
        for arg, val in sorted(func_info.items()):
            if val is None:
                continue
            if q_first:
                q_first = False
            else:
                output.write(', ')
            output.write('%s = %s' % (arg, json.dumps(val, sort_keys = True)))
        output.write(')')
        _reprEnumCase('', op_mode, values, output)
        if group_mode:
            output.write(')')
        return
    assert False

#===============================================
def _reprEnumCase(unit_operand, op_mode, values, output):
    if op_mode in ("OR", ""):
        output.write('%s in {' % unit_operand)
        op_close = '}'
    elif op_mode == "NOT":
        output.write('%s not in {' % unit_operand)
        op_close = '}'
    else:
        assert op_mode == "AND"
        output.write('%s in all({' % unit_operand)
        op_close = '})'
    _reprValues(output, values)
    output.write(op_close)

#===============================================
def _reprValues(output, values):
    q_first = True
    for val in values:
        if q_first:
            q_first = False
        else:
            output.write(",\f")
        if checkIdentifier(val):
            output.write(val)
        else:
            output.write('"' + val.replace('"', '\\"') + '"')


#===============================================
TAB_LEN = 4
STR_LEN = 70

def _formatRep(text, start_indent, next_indent):
    global TAB_LEN, STR_LEN
    ret = StringIO()
    cur_len = 0
    if start_indent > 0:
        cur_len = TAB_LEN * start_indent
        if cur_len > 0:
            ret.write(' ' * cur_len)
    q_first = True
    for chunk in text.split('\f'):
        if q_first:
            ret.write(chunk)
            cur_len += len(chunk)
            q_first = False
            continue
        if cur_len + len(chunk) < STR_LEN:
            ret.write(' ')
            ret.write(chunk)
            cur_len += 1 + len(chunk)
            continue
        ret.write('\n')
        cur_len = TAB_LEN * next_indent
        if cur_len > 0:
            ret.write(' ' * cur_len)
        ret.write(chunk)
        cur_len += len(chunk)
    return ret.getvalue()
