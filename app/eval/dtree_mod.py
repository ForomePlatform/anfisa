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

from .condition import reduceCondData
from .code_repr import formatIfCode
#===============================================
def modifyDTreeCode(parsed, instr):
    target, mode, loc = instr[:3]
    if target == "ATOM":
        frag_no, atom_no = loc
    elif target == "POINT":
        frag_no, atom_no = loc, None
    else:
        assert False, "Bad dtree instruction target: " + target
    frag_h = parsed.getFragments()[frag_no]
    line_from, line_to = frag_h.getLineDiap()
    use_comments = True

    if mode == "EDIT":
        assert atom_no is not None
        new_point_cond = instr[3]
        frag_h.getCondAtoms()[atom_no].resetCondData(new_point_cond)
        new_cond_data = frag_h.getCondData()
    elif mode == "DELETE":
        if atom_no is not None:
            frag_h.getCondAtoms()[atom_no].resetCondData([False])
            new_cond_data = reduceCondData(frag_h.getCondData())
            assert new_cond_data, "Use delete point instead of atom!"
        else:
            use_comments = False
            new_cond_data = None
            _, line_to = parsed.getFragments()[frag_no + 1].getLineDiap()
    else:
        assert False, "Bad dtree edit mode: " + mode

    code_lines = parsed.getTreeCode().splitlines()
    replace_lines = []
    if use_comments:
        for line_no in range(line_from, line_to):
            if parsed.isLineIsDummy(line_no):
                replace_lines.append(code_lines[line_no - 1])
    if new_cond_data:
        replace_lines += formatIfCode(new_cond_data).splitlines()
    code_lines[line_from - 1: line_to - 1] = replace_lines
    return "\n".join(code_lines)
