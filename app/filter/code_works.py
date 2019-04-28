from StringIO import StringIO
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
    assert (h_lines[0] ==
        '<div class="highlight"><pre><span class="c1">#START</span>')
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
        col_offset = name_instr.col_offset + len(name_instr.id)
        code_sheet[name_instr.lineno - 1] = (line_text[:col_offset] +
            ('__%d__%d__' % (check_no, instr_no)) + line_text[col_offset:])
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
            insert_code = ('<span class="point-edit" ' +
                ('id="__mark_%d_%d" ' % (check_no, instr_no)) +
                ('onclick="editMark(%d,%d);"' % (check_no, instr_no)) +
                '>&#9874;</span>')
            l_upd = (l_upd[:j_upd_start] + insert_code + l_upd[j_upd:])
            j_upd += len(insert_code) - (j_upd - j_upd_start)
        lines_upd[idx] = l_upd
    assert cnt_points == len(marker_seq)
    return lines_upd

#===============================================








#===============================================
STR_TAB = "    "
sDiff = Differ()
#===============================================
def _reprCondition(cond, output, repr_level):
    global STR_TAB
    cond_kind = cond[0]
    if cond_kind in ("or", "and"):
        cond_seq = cond[1:]
        output.write('(')
        _reprCondition(cond_seq[0], output, repr_level)
        for sub_cond in cond_seq[1:]:
            output.write('\n' + (repr_level + 1) * STR_TAB + cond_kind + " ")
            _reprCondition(sub_cond, output, repr_level + 1)
        output.write(')')
    elif cond_kind == "numeric":
        unit_name, bounds, use_undef = cond[1:]
        seq = []
        if bounds[0] is not None:
            seq.append(str(bounds[0]))
        seq.append(unit_name)
        if bounds[1] is not None:
            seq.append(str(bounds[1]))
        assert len(seq) > 1
        output.write('(' + ' <= '.join(seq) + ')')
    else:
        assert cond_kind == "enum"
        unit_name, filter_mode, variants = cond[1:]
        output.write('(' + ' '.join([unit_name, 'in',
            '{' + ', '.join(variants) + '}']) + ')')

#===============================================
def treeToText(tree_data):
    global STR_TAB
    output = StringIO();

    for instr in tree_data:
        if instr[0] == "comment":
            print >> output, "# " + instr[1]
            continue
        point_kind, point_level = instr[:2]
        if point_level > 0:
            output.write(point_level * STR_TAB)
        if point_kind == "Return":
            p_decision = "True" if instr[2] else "False"
            print >> output, "return", p_decision
            continue
        assert point_kind == "If"
        output.write("if ")
        _reprCondition(instr[2], output, point_level)
        print >> output

    return output.getvalue().splitlines()


#===============================================
def cmpTrees(tree_code1, tree_code2):
    global sDiff
    result = []
    cur_reg = None
    cmp_res = "\n".join(sDiff.compare(tree_code1, tree_code2))
    for line in cmp_res.splitlines():
        if len(line) == 0:
            continue
        if cur_reg != line[0]:
            cur_reg = line[0]
            result.append([])
        result[-1].append(line)
    return result

