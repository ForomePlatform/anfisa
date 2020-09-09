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

import ast, tokenize
from io import StringIO
#===============================================
def parseCodeByPortions(code_lines, dummy_lines_reg):
    start_line_no = 1
    base_pos, error_info = None, None
    for line_idx, line in enumerate(code_lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            dummy_lines_reg.add(line_idx + 1)
            if base_pos is None:
                continue
        elif base_pos is not None and line[:base_pos + 1].isspace():
            continue
        if base_pos is not None:
            parsed_block, error_info = _validatePortion(start_line_no,
                line_idx + 1, code_lines, error_info, dummy_lines_reg)
            yield (parsed_block, error_info, (start_line_no, line_idx + 1))
            start_line_no = line_idx + 1
            base_pos, error_info = None, None
            if stripped.startswith('#') or not stripped:
                continue
        base_pos = 0
        while line[base_pos] == ' ':
            base_pos += 1
        if base_pos > 0 and error_info is None:
            error_info = ("Improper indent on top level",
                line_idx + 1, base_pos)
    if base_pos is not None:
        parsed_block, error_info = _validatePortion(start_line_no,
            len(code_lines) + 1, code_lines, error_info, dummy_lines_reg)
    else:
        parsed_block = None
        error_info = ("Script not finished", start_line_no, 0)
    yield (parsed_block, error_info, (start_line_no, len(code_lines) + 1))

#===============================================
def _validatePortion(start_line_no, end_line_no,
        lines, error_info, dummy_lines_reg):
    text_block = '\n'.join(lines[start_line_no - 1: end_line_no - 1])
    parsed_block = None
    if error_info is None:
        try:
            parsed_block = ast.parse(text_block)
        except SyntaxError as err:
            txt_len = len(err.text.rstrip())
            error_info = ("Syntax error",
                start_line_no - 1 + max(1, err.lineno),
                max(0, min(err.offset, txt_len - 1)))
            parsed_block = None
    if parsed_block is not None:
        text_io = StringIO(text_block)
        for info in tokenize.generate_tokens(text_io.readline):
            if info[0] == tokenize.COMMENT:
                line_no, offset = info[2]
                if line_no + start_line_no - 1 not in dummy_lines_reg:
                    error_info = ("Sorry, no inline comments",
                        start_line_no + line_no - 1, offset)
                    parsed_block = None
                    break
    if parsed_block is not None and error_info is None:
        error_info = _validateInstrSplit(parsed_block,
            lines, start_line_no, True)
        if error_info is not None:
            parsed_block = None
    return (parsed_block, error_info)

#===============================================
def _validateInstrSplit(instr_d, lines, start_line_no, on_top = False):
    if not on_top:
        line_no, offset = instr_d.lineno, instr_d.col_offset
        if offset > 0:
            prefix = lines[start_line_no + line_no - 2][:offset]
            if not prefix.isspace():
                return("Split line before instruction",
                    start_line_no + line_no - 1, offset)
    if "body" in instr_d._fields:
        for sub_instr_d in instr_d.body:
            err = _validateInstrSplit(sub_instr_d, lines, start_line_no)
            if err:
                return err
    return None
