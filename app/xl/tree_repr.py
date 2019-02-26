from StringIO import StringIO
from difflib import Differ

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
        unit_name, ge_mode, the_val, use_undef = cond[1:]
        output.write('(' + ' '.join([unit_name,
            "<=" if ge_mode else ">=", str(the_val)]) + ')')
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
        if point_kind == "term":
            p_decision = "True" if instr[2] else "False"
            print >> output, "return", p_decision
            continue
        assert point_kind == "cond"
        output.write("if ")
        _reprCondition(instr[2], output, point_level)
        print >> output

    return output.getvalue().splitlines()


#===============================================
def cmpTrees(tree_data1, tree_data2):
    global sDiff
    result = []
    cur_reg = None
    cmp_res = "\n".join(sDiff.compare(
        treeToText(tree_data1), treeToText(tree_data2)))
    for line in cmp_res.split('\n'):
        if len(line) == 0:
            continue
        if cur_reg != line[0]:
            cur_reg = line[0]
            result.append([])
        result[-1].append(line)
    return result

