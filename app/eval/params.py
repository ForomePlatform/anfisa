import ast

#===============================================
def parseParams(text, param_list):
    bad_line_no = None
    bad_line = None
    error = None
    ret = []
    for idx, line in enumerate(text.split('\n')):
        if not line.strip():
            continue
        bad_line, bad_line_no = line, idx + 1
        try:
            mod = ast.parse(line)
        except Exception:
            error = "Syntax error"
            break
        if len(mod.body) != 1:
            error = "Syntax problem"
            break
        if len(ret) >= len(param_list):
            error = "Extra parameter assignment"
            break
        instr = mod.body[0]
        if (isinstance(instr, ast.Assign) and
                len(instr.targets) == 1 and
                isinstance(instr.targets[0], ast.Name) and
                isinstance(instr.value, ast.Num)):
            if instr.targets[0].id != param_list[len(ret)]:
                error = "Parameter %s assignment expected" % param_list[idx]
                break;
            ret.append((instr.targets[0].id, instr.value.n))
        else:
            error = "Parameter assignment expected"
            break
    if error is None and len(ret) < len(param_list):
        error = "More paremeters expected: %s" % param_list[len(ret)]
        bad_line, bad_line_no = None, -1

    if error is None:
        return ret, None
    if bad_line_no is None:
        return None, "Empty list?"
    if bad_line_no < 0:
        return None, '<b>At end</b><br/>' + error
    return None, ('<b>At line %d: %s</b><br/>' %
        (bad_line_no, bad_line)) + error
