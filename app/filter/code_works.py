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

from xml.sax.saxutils import escape
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from difflib import Differ

#===============================================
#===============================================
def normalizeCode(code):
    return '\n'.join([line.rstrip().replace('\t', '    ')
        for line in code.splitlines()])


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


#===============================================
#===============================================
class HtmlPresentation:
    sLexer = PythonLexer()
    sFormatter = HtmlFormatter()

    @classmethod
    def presentProperCode(cls, code_lines, line_diap):
        line_from, line_to = line_diap
        h_lines = highlight("\n".join(["#START"]
            + code_lines[line_from - 1: line_to - 1] + ["#END"]),
            cls.sLexer, cls.sFormatter).splitlines()
        assert (h_lines[0].startswith('<div class="highlight"><pre>')
            and h_lines[0].endswith('<span class="c1">#START</span>'))
        assert h_lines[-2] == '<span class="c1">#END</span>'
        assert h_lines[-1] == '</pre></div>'
        return h_lines[1:-2]

    @classmethod
    def presentErrorCode(cls, code_lines, line_diap, err_info):
        ret = []
        err_msg, line_err, pos = err_info
        for line_no in range(*line_diap):
            line = code_lines[line_no - 1]
            if not line:
                ret.append(line)
                continue
            if line_no == line_err:
                ret.append(''.join(['<span class="line-err">',
                    escape(line[:pos]),
                    '<span class="note-err" title="%s">&x26a0;</span>' %
                    escape(err_msg),
                    escape(line[pos:]), '</span>']))
            elif line.strip().startswith('#'):
                ret.append(''.join(['<span class="c">',
                    escape(line), '</span>']))
            else:
                ret.append(''.join(['<span class="line-err">',
                    escape(line), '</span>']))
        return ret

    @classmethod
    def decorProperCode(cls, code_lines, line_diap, marker_seq = None):
        lines_base = cls.presentProperCode(code_lines, line_diap)
        if marker_seq is None:
            return lines_base
        code_sheet = code_lines[:]
        line_from, line_to = line_diap
        m_cnt1, m_cnt2 = 0, 0
        for check_no, instr_no, cond_loc in sorted(marker_seq,
                reverse = True, key = lambda info: info[2]):
            line_no, offset_from, offset_to = cond_loc
            if not (line_from <= line_no < line_to):
                continue
            m_cnt1 += 1
            line_text = code_sheet[line_no - 1]
            code_sheet[line_no - 1] = (line_text[:offset_to]
                + ('__%d__%d__' % (check_no, instr_no))
                + line_text[offset_to:])
        lines_upd = cls.presentProperCode(code_sheet, line_diap)
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
                m_cnt2 += 1
                insert_code = ('<span class="point-edit" '
                    + ('id="__mark_%d_%d" ' % (check_no, instr_no))
                    + ('onclick="editMark(%d,%d);"' % (check_no, instr_no))
                    + '>&#9874;</span>')
                l_upd = (l_upd[:j_upd_start] + insert_code + l_upd[j_upd:])
                j_upd += len(insert_code) - (j_upd - j_upd_start)
            lines_upd[idx] = l_upd
        assert m_cnt1 == m_cnt2
        return lines_upd
