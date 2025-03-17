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

import ast, tokenize, re
from io import StringIO

from app.config.variables import anfisaVariables
#===============================================
def parseCodeByPortions(code_lines, comment_lines_reg):
    for diap, error_info in _iterCodePortions(code_lines, comment_lines_reg):
        parsed_block, meta_annotations = None, None
        if error_info is None:
            meta_annotations, error_info = _parseMetaAnnotations(
                code_lines, comment_lines_reg, diap)
        if error_info is None:
            parsed_block, error_info = _validatePortion(diap[0], diap[1],
                code_lines, error_info, comment_lines_reg)
        yield (parsed_block, error_info, diap, meta_annotations)

#===============================================
def _iterCodePortions(code_lines, comment_lines_reg):
    start_line_no = 1
    base_indent = None
    multiline_comment_mode = False
    multiline_line_idx = None

    for line_idx, line in enumerate(code_lines):
        stripped = line.strip()
        if stripped == '"""':
            if base_indent is not None:
                yield (start_line_no, line_idx + 1), None
                start_line_no = line_idx
                base_indent = None
            comment_lines_reg.add(line_idx + 1)
            multiline_comment_mode = not multiline_comment_mode
            multiline_line_idx = line_idx + 1
            continue

        if (multiline_comment_mode or not stripped
                or stripped.startswith('#')):
            comment_lines_reg.add(line_idx + 1)
            if base_indent is not None:
                yield (start_line_no, line_idx + 1), None
                start_line_no = line_idx + 1
                base_indent = None
            continue

        if base_indent is not None:
            if line[:base_indent + 1].isspace():
                continue
            yield (start_line_no, line_idx + 1), None
            start_line_no = line_idx + 1

        base_indent = 0
        while line[base_indent] == ' ':
            base_indent += 1
        if base_indent > 0:
            yield (start_line_no, line_idx + 1), (
                "Improper indent on top level", line_idx + 1, base_indent)
            return

    if multiline_comment_mode:
        yield (start_line_no, len(code_lines) + 1), (
            "Unterminated multiline comment", multiline_line_idx, 0)
        return

    if base_indent is not None:
        yield (start_line_no, len(code_lines) + 1), None

#===============================================
def _validatePortion(start_line_no, end_line_no,
        lines, error_info, comment_lines_reg):
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
                if line_no + start_line_no - 1 not in comment_lines_reg:
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

#===============================================
sMetaPattern = re.compile(
    r'^\s*@(\w+)\s*\(\s*((\w+)|(["]([\w ]+)["]))\s*\)\s*$')

def _parseMetaAnnotations(code_lines, comment_lines_reg, diap):
    ret = None
    for idx in range(*diap):
        if idx not in comment_lines_reg:
            continue
        line = code_lines[idx - 1]
        stripped = line.strip()
        if not stripped.startswith('@'):
            continue
        match = sMetaPattern.match(line)
        m_pos = line.index('@')
        if match is None:
            return None, ("Improper meta annotation", idx, m_pos)
        if ret is None:
            ret = []
        meta_idxs, err_msg = anfisaVariables.checkMetaAnnotation(
            match.group(1), match.group(5) or match.group(2))
        if err_msg is not None:
            return None, (err_msg, idx, m_pos)
        ret.append([meta_idxs, (idx, m_pos), stripped])
    return ret, None
