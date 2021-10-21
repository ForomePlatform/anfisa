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

from .condition import ConditionMaker, reduceCondData
from .code_repr import formatIfCode

def makeReturnStr(value, level = 1):
    return (level * "    ") + "return " + ("True" if value else "False")

#===============================================
def modifyDTreeCode(parsed, instr):
    target, mode, loc = instr[:3]
    if target == "ATOM":
        frag_no, atom_no = loc
    elif target == "POINT":
        frag_no, atom_no = loc, None
    elif target == "INSTR":
        frag_no, atom_no = loc, None
    else:
        assert False, "Bad dtree instruction target: " + target
    if mode.startswith("UP-"):
        frag_no -= 1
        mode = mode[3:]
    frag_h = parsed.getFragments()[frag_no]
    line_from, line_to = frag_h.getLineDiap()
    c_line_from, c_line_to = line_from, line_to
    use_comments = True
    add_line = None
    more_lines = []

    if mode == "DELETE":
        if atom_no is not None:
            frag_h.getCondAtoms()[atom_no].resetCondData([False])
            new_cond_data = reduceCondData(frag_h.getCondData())
            assert new_cond_data, "Use delete point instead of atom!"
        else:
            use_comments = False
            new_cond_data = None
            _, line_to = parsed.getFragments()[frag_no + 1].getLineDiap()
    elif mode == "EDIT":
        assert atom_no is not None, "No atom no for EDIT mode"
        new_point_cond = instr[3]
        frag_h.getCondAtoms()[atom_no].resetCondData(new_point_cond)
        new_cond_data = frag_h.getCondData()
    elif target == "POINT":
        assert atom_no is None, "Bad tree edit atom mode: " + mode
        new_point_cond = instr[3]
        if mode == "REPLACE":
            new_cond_data = new_point_cond
        elif mode == "INSERT":
            use_comments = False
            line_to = line_from
            new_cond_data = new_point_cond
            add_line = makeReturnStr(True)
        elif mode == "JOIN-AND":
            new_cond_data = ConditionMaker.joinAnd(
                [frag_h.getCondData(), new_point_cond])
        elif mode == "JOIN-OR":
            new_cond_data = ConditionMaker.joinOr(
                [frag_h.getCondData(), new_point_cond])
        else:
            assert False, "Bad dtree POINT edit mode: " + mode
    else:
        assert target == "INSTR", "Improper target: " + str(target)
        if mode == "JOIN-AND":
            prev_frag_h = parsed.getFragments()[frag_no - 2]
            line_from, _ = prev_frag_h.getLineDiap()
            c_line_from = line_from
            new_cond_data = ConditionMaker.joinAnd([
                prev_frag_h.getCondData(), frag_h.getCondData()])
        elif mode == "JOIN-OR":
            prev_frag_h = parsed.getFragments()[frag_no - 2]
            line_from, _ = prev_frag_h.getLineDiap()
            c_line_from = line_from
            new_cond_data = ConditionMaker.joinOr([
                prev_frag_h.getCondData(), frag_h.getCondData()])
        elif mode == "SPLIT":
            sub_frag_h = parsed.getFragments()[frag_no + 1]
            _, line_to = sub_frag_h.getLineDiap()
            c_line_to = line_to
            add_line = makeReturnStr(sub_frag_h.getDecision())
            assert frag_h.getCondData()[0] in ("and", "or"), (
                "Bad SPLIT operation: " + frag_h.getCondData()[0])
            new_cond_data = frag_h.getCondData()[1]
            for more_cond in frag_h.getCondData()[2:]:
                more_lines += formatIfCode(more_cond).splitlines()
                more_lines.append(add_line)
        elif mode == "DUPLICATE":
            new_cond_data = frag_h.getCondData()
            use_comments = False
            sub_frag_h = parsed.getFragments()[frag_no + 1]
            _, line_to = sub_frag_h.getLineDiap()
            line_from = line_to
            add_line = makeReturnStr(sub_frag_h.getDecision())
        elif mode == "NEGATE":
            new_cond_data = ConditionMaker.condNot(frag_h.getCondData())
        elif mode == "BOOL-TRUE":
            new_cond_data = None
            add_line = makeReturnStr(True, frag_h.getLevel())
        elif mode == "BOOL-FALSE":
            new_cond_data = None
            add_line = makeReturnStr(False, frag_h.getLevel())
        elif mode == "LABEL":
            pass
        elif mode == "COMMENTS":
            pass
        else:
            assert False, "Bad dtree INSTR edit mode: " + mode

    code_lines = parsed.getTreeCode().splitlines()
    replace_lines = []
    if use_comments:
        for line_no in range(c_line_from, c_line_to):
            if parsed.isLineIsDummy(line_no):
                replace_lines.append(code_lines[line_no - 1])
    if new_cond_data:
        replace_lines += formatIfCode(new_cond_data).splitlines()
    if add_line:
        replace_lines.append(add_line)
    code_lines[line_from - 1: line_to - 1] = replace_lines + more_lines
    return "\n".join(code_lines)
