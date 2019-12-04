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

import re
from io import StringIO
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
    return rep.getvalue()


#===============================================
sIdPatt = re.compile("^[A-Z_][A-Z0-9_]*$", re.I)
def _reprConditionCode(cond_data, output, group_mode):
    global sIdPatt
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
        unit_name, bounds, use_undef = cond_data[1:]
        seq = []
        if bounds[0] is not None:
            seq.append(str(bounds[0]))
        seq.append(unit_name)
        if bounds[1] is not None:
            seq.append(str(bounds[1]))
        assert len(seq) > 1
        output.write(' <= '.join(seq))
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
    if cond_kind == "zygosity":
        if group_mode:
            output.write('(')
        unit_name, p_group, op_mode, values = cond_data[1:]
        if not p_group:
            unit_operand = unit_name + '()'
        else:
            unit_operand = (unit_name + '({'
                + ','.join(map(str, sorted(p_group))) + '})')
        _reprEnumCase(unit_operand, op_mode, values, output)
        if group_mode:
            output.write(')')
        return
    if cond_kind == "import":
        output.write('import %s' % cond_data[1])
        return
    assert False

#===============================================
def _reprEnumCase(unit_operand, op_mode, values, output, panel_name = None):
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
    if panel_name is not None:
        output.write('panel(' + panel_name + ')')
    else:
        q_first = True
        for val in values:
            if q_first:
                q_first = False
            else:
                output.write(",\f")
            if sIdPatt.match(val):
                output.write(val)
            else:
                output.write('"' + val.replace('"', '\\"') + '"')
    output.write(op_close)


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
