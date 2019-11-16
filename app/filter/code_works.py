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

import re, ast, tokenize

from io import StringIO
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from difflib import Differ

#===============================================
sLexer = PythonLexer()
sFormatter = HtmlFormatter()

def htmlCodePresentation(code):
    global sLexer, sFormatter
    h_lines = highlight("#START\n" + code + "\n#END",
        sLexer, sFormatter).splitlines()
    assert (h_lines[0].startswith('<div class="highlight"><pre>')
        and h_lines[0].endswith('<span class="c1">#START</span>'))
    assert h_lines[-2] == '<span class="c1">#END</span>'
    assert h_lines[-1] == '</pre></div>'
    return h_lines[1:-2]

#===============================================
def htmlCodeDecoration(code, marker_seq):
    code_sheet = code.splitlines()
    for check_no, instr_no, name_instr in sorted(marker_seq,
            reverse = True, key = lambda info:
            (info[2].lineno, info[2].col_offset)):
        line_text = code_sheet[name_instr.lineno - 1]
        name_id = (name_instr.func.id if isinstance(name_instr, ast.Call)
            else name_instr.id)
        col_offset = name_instr.col_offset + len(name_id)
        code_sheet[name_instr.lineno - 1] = (line_text[:col_offset]
            + ('__%d__%d__' % (check_no, instr_no)) + line_text[col_offset:])
    lines_base = htmlCodePresentation(code.rstrip())
    lines_upd  = htmlCodePresentation('\n'.join(code_sheet))
    assert len(lines_base) == len(lines_upd)
    cnt_points = 0
    for idx, l_base in enumerate(lines_base):
        l_upd = lines_upd[idx]
        j_base = 0
        j_upd = 0
        while True:
            jj_upd = l_upd.find('__', j_upd)
            if jj_upd < 0:
                assert l_base[j_base:] == l_upd[j_upd:]
                break
            dj = jj_upd - j_upd
            assert l_base[j_base:j_base + dj] == l_upd[j_upd:j_upd + dj]
            j_base += dj
            j_upd += dj
            if j_base < len(l_base) and l_base[j_base] == l_upd[j_upd]:
                continue
            j_upd_start = j_upd
            j_upd += 2
            jj_upd = l_upd.find('__', j_upd)
            check_no = int(l_upd[j_upd:jj_upd])
            j_upd = jj_upd + 2
            jj_upd = l_upd.find('__', j_upd)
            instr_no = int(l_upd[j_upd:jj_upd])
            j_upd = jj_upd + 2
            cnt_points += 1
            insert_code = ('<span class="point-edit" '
                + ('id="__mark_%d_%d" ' % (check_no, instr_no))
                + ('onclick="editMark(%d,%d);"' % (check_no, instr_no))
                + '>&#9874;</span>')
            l_upd = (l_upd[:j_upd_start] + insert_code + l_upd[j_upd:])
            j_upd += len(insert_code) - (j_upd - j_upd_start)
        lines_upd[idx] = l_upd
    assert cnt_points == len(marker_seq)
    return lines_upd

#===============================================
#===============================================
def reprConditionCode(cond_data):
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
def reprFilterCondition(cond_data):
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
    elif op_mode == "AND":
        output.write('%s in all({' % unit_operand)
        op_close = '})'
    else:
        assert op_mode == "ONLY"
        output.write('%s in only({' % unit_operand)
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

#===============================================
def findComment(code):
    if '#' not in code:
        return None
    code_obj = StringIO(code)
    try:
        for info in tokenize.generate_tokens(code_obj.readline):
            if info[0] == tokenize.COMMENT:
                return info[2]
    except tokenize.TokenError:
        pass
    return None


#===============================================
#===============================================
sDiff = Differ()

#===============================================
def cmpTrees(tree_code1, tree_code2):
    global sDiff
    result = []
    cur_reg = None
    cmp_res = "\n".join(sDiff.compare(
        tree_code1.splitlines(), tree_code2.splitlines()))
    for line in cmp_res.splitlines():
        if len(line) == 0:
            continue
        if cur_reg != line[0]:
            cur_reg = line[0]
            result.append([])
        result[-1].append(line)
    return result
