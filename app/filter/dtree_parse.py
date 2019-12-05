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

import sys, ast
from hashlib import md5

from utils.log_err import logException
from .code_repr import formatIfCode
from .code_works import normalizeCode
from .code_parse import parseCodeByPortions
#===============================================
class TreeFragment:
    def __init__(self, level, tp, line_diap,
            base_instr = None, err_info = None, decision = None,
            import_entries = None, cond_data = None, markers = None,
            hash_code = None):
        self.mLevel = level
        self.mType = tp
        self.mLineDiap = line_diap
        self.mBaseInstr = base_instr
        self.mErrInfo = err_info
        self.mCondData = cond_data
        self.mDecision = decision
        self.mImportEntries = import_entries
        self.mMarkers = markers if markers is not None else []
        self.mHashCode = hash_code

    def setLineDiap(self, base_diap, full_diap):
        self.mBaseLineDiap = base_diap
        self.mFullLineDiap = full_diap

    def getLevel(self):
        return self.mLevel

    def getInstrType(self):
        return self.mType

    def getBaseInstr(self):
        return self.mBaseInstr

    def getLineDiap(self):
        return self.mLineDiap

    def getErrorInfo(self):
        return self.mErrInfo

    def getCondData(self):
        return self.mCondData

    def getDecision(self):
        return self.mDecision

    def getImportEntries(self):
        return self.mImportEntries

    def getHashCode(self):
        return self.mHashCode

    def getMarkers(self):
        return self.mMarkers

    def getMarkerInstr(self, idx):
        return self.mMarkers[idx][1]

#===============================================
class ParsedDTree:
    def __init__(self, cond_env, code):
        self.mCondEnv = cond_env
        self.mFragments = []
        self.mCode = normalizeCode(code)
        self.mImportFragments = dict()
        self.mDummyLinesReg = set()
        hash_h = md5()
        code_lines = self.mCode.splitlines()

        for parsed_d, err_info, line_diap in parseCodeByPortions(
                code_lines, self.mDummyLinesReg):
            fragments = []
            if err_info is None:
                assert len(parsed_d.body) == 1
                self.mError = None
                self.mCurLineDiap = line_diap
                try:
                    instr_d = parsed_d.body[0]
                    if isinstance(instr_d, ast.Return):
                        fragments.append(TreeFragment(0, "Return", line_diap,
                            decision = self.getReturnValue(instr_d)))
                    elif isinstance(instr_d, ast.Import):
                        fragments.append(self.processImport(instr_d,
                            hash_h.hexdigest()))
                    elif isinstance(instr_d, ast.If):
                        fragments += self.processIf(instr_d)
                    else:
                        self.errorIt(instr_d,
                            "Instructon must be of if-type")
                    for frag_h in fragments:
                        line_from, line_to = frag_h.getLineDiap()
                        for line_no in range(line_from, line_to):
                            if line_no not in self.mDummyLinesReg:
                                hash_h.update(bytes(code_lines[line_no - 1],
                                    "utf-8"))
                                hash_h.update(b'\n')
                except Exception as err:
                    if self.mError is None:
                        logException("Exception on parse tree code")
                        raise err
                    err_info = self.mError
            if err_info is not None:
                fragments = [TreeFragment(0, "Error", line_diap,
                    err_info = err_info)]
            self.mFragments += fragments
        self.mHashCode = hash_h.hexdigest()
        self.mError = None
        self.mCurLineDiap = None
        for frag_h in self.mFragments:
            self.mError = frag_h.getErrorInfo()
            if self.mError is not None:
                break
        if self.mError is None:
            for idx, frag_h in enumerate(self.mFragments[:-1]):
                if frag_h.getLevel() == 0 and frag_h.getDecision() is not None:
                    err_info = ("Final instruction not in final place",
                        frag_h.getLineDiap()[0], 0)
                    self.mFragments[idx] = TreeFragment(0, "Error",
                        frag_h.getLineDiap(), err_info = err_info)
                    self.mError = err_info
                    break
        if self.mError is None:
            last_frag_h = self.mFragments[-1]
            if last_frag_h.getLevel() > 0 or last_frag_h.getDecision() is None:
                err_info = ("Final instruction must return True or False",
                    last_frag_h.getLineDiap()[0], 0)
                self.mFragments[-1] = TreeFragment(0, "Error",
                    frag_h.getLineDiap(), err_info = err_info)
                self.mError = err_info

    def getError(self):
        return self.mError

    def getTreeCode(self):
        return self.mCode

    def getCondEnv(self):
        return self.mCondEnv

    def getFragments(self):
        return self.mFragments

    def getHashCode(self):
        return self.mHashCode

    def errorIt(self, it, msg_text):
        self.mError = (msg_text,
            it.lineno + self.mCurLineDiap[0] - 1, it.col_offset)
        raise RuntimeError()

    def errorMsg(self, line_no, col_offset, msg_text):
        self.mError = (msg_text,
            line_no + self.mCurLineDiap[0] - 1, col_offset)
        raise RuntimeError()

    #===============================================
    def processIf(self, instr_d):
        markers = []
        cond_data = self._processCondition(instr_d.test, markers)
        if len(instr_d.orelse) > 0:
            self.errorIt(instr_d.orelse[0],
                "Else instruction is not supported")
        line_from, line_to = self.mCurLineDiap
        decision = self.getSingleReturnValue(instr_d.body)
        line_decision = instr_d.body[0].lineno + line_from - 1
        return [
            TreeFragment(0, "If", (line_from, line_decision),
                markers = markers, cond_data = cond_data),
            TreeFragment(1, "Return",
                (line_decision, line_to), decision = decision)]

    #===============================================
    def processImport(self, instr, hash_code):
        import_entries = []
        for entry in instr.names:
            if entry.asname is not None:
                self.errorIt(instr, "entry with path not supported")
            if (entry.name in self.mImportFragments
                    or entry.name in import_entries):
                self.errorIt(instr, "duplicate import: " + entry.name)
            unit_kind, _ = self.mCondEnv.detectUnit(entry.name)
            if unit_kind in (None, "reserved"):
                self.errorIt(instr, "Case does not provide: " + entry.name)
            if unit_kind != "operational":
                self.errorIt(instr, "improper name for import: " + entry.name)
            import_entries.append(entry.name)
        frag_h = TreeFragment(0, "Import", self.mCurLineDiap,
            import_entries = import_entries, hash_code = hash_code)
        for nm in import_entries:
            self.mImportFragments[nm] = frag_h
        return frag_h

    #===============================================
    def getReturnValue(self, instr):
        if isinstance(instr.value, ast.NameConstant):
            if instr.value.value in (True, False):
                return instr.value.value
        self.errorIt(instr,
            "Only boolean return (True/False) is expected here")

    #===============================================
    def getSingleReturnValue(self, body):
        assert len(body) >= 1
        if len(body) > 1:
            self.errorIt(body[1],
                "Only one instruction is expected here")
        instr = body[0]
        if not isinstance(instr, ast.Return):
            self.errorIt(instr, "Only return instruction is expected here")
        return self.getReturnValue(instr)

    #===============================================
    def _processCondition(self, it, markers):
        if isinstance(it, ast.BoolOp):
            if isinstance(it.op, ast.And):
                seq = ["and"]
            elif isinstance(it.op, ast.Or):
                seq = ["or"]
            else:
                self.errorIt(it, "Logic operation not supported")
            for val in it.values:
                rep_el = self._processCondition(val, markers)
                if rep_el[0] == seq[0]:
                    seq += rep_el[1:]
                else:
                    seq.append(rep_el)
            return seq
        if isinstance(it, ast.UnaryOp):
            if not isinstance(it.op, ast.Not):
                self.errorIt(it, "Unary operation not supported")
            return ["not", self._processCondition(it.operand, markers)]
        if not isinstance(it, ast.Compare):
            self.errorIt(it, "Comparison or logic operation expected")
        if len(it.ops) == 1 and (isinstance(it.ops[0], ast.In)
                or isinstance(it.ops[0], ast.NotIn)):
            return self._processEnumInstr(it, markers)
        return self._processNumInstr(it, markers)

    #===============================================
    def _processEnumInstr(self, it, markers):
        assert len(it.comparators) == 1
        it_set = it.comparators[0]
        if isinstance(it.ops[0], ast.NotIn):
            op_mode = "NOT"
        else:
            assert isinstance(it.ops[0], ast.In)
            op_mode = "OR"

        if isinstance(it_set, ast.Call):
            if (len(it_set.args) != 1 or len(it_set.keywords) > 0
                    or not it_set.func
                    or not isinstance(it_set.func, ast.Name)):
                self.errorIt(it_set, "Complex call not supported")
            if it_set.func.id == "all":
                if op_mode == "NOT":
                    self.errorIt(it_set, "Complex call not supported")
                op_mode = "AND"
                it_set = it_set.args[0]
            else:
                self.errorIt(it_set,
                    "Only pseudo-function all is supported")

        if not (isinstance(it_set, ast.List)
                or isinstance(it_set, ast.Set)):
            self.errorIt(it_set, "Set (or list) expected")
        variants = []
        for el in it_set.elts:
            if isinstance(el, ast.Str):
                val = el.s
            elif isinstance(el, ast.Name):
                val = el.id
            elif isinstance(el, ast.NameConstant):
                val = str(el.value)
            else:
                self.errorIt(el, "Name or string is expected as variant")
            if val in variants:
                self.errorIt(el, "Duplicated variant")
            variants.append(val)
        if len(variants) == 0:
            self.errorIt(it_set, "Empty set")

        if isinstance(it.left, ast.Name):
            field_name = it.left.id
            if self.mCondEnv is not None:
                unit_kind, unit_h = self.mCondEnv.detectUnit(
                    field_name, "enum")
                if unit_kind == "operational":
                    if field_name not in self.mImportFragments:
                        self.errorIt(it.left,
                            "Field %s not imported" % field_name)
                    return ["operational", field_name, op_mode, variants]
                if unit_kind != "enum" or unit_h is None:
                    self.errorIt(it.left, "Improper enum field name: "
                        + field_name)
            ret = ["enum", field_name, op_mode, variants]
            markers.append([ret, it.left])
            return ret

        if isinstance(it.left, ast.Call):
            if (len(it.left.keywords) > 0
                    or not isinstance(it.left.func, ast.Name)):
                self.errorIt(it.left, "Complex call not supported")
            field_name = it.left.func.id
            assert self.mCondEnv is not None
            unit_kind, unit_h = self.mCondEnv.detectUnit(
                field_name, "special")
            if unit_kind != "special":
                self.errorIt(it.left, "Improper special field name")
            ret = unit_h.processInstr(self, it.left.args, op_mode, variants)
            if ret is None:
                self.errorIt(it.left,
                    "Improper arguments for special field")
            markers.append([ret, it.left])
            return ret
        self.errorIt(it.left, "Name of field is expected")

    #===============================================
    def _processNumInstr(self, it, markers):
        if len(it.ops) > 2 or (
                len(it.ops) == 2 and it.ops[0] != it.ops[1]):
            self.errorIt(it, "Too complex comparison")
        if isinstance(it.ops[0], ast.LtE):
            mode_ord = 0
        elif isinstance(it.ops[0], ast.GtE):
            mode_ord = 1
        else:
            self.errorIt(it, "Operation not supported")
        operands = [it.left] + it.comparators[:]
        if mode_ord:
            operands = operands[::-1]
        idx_fld = None
        for idx, op in enumerate(operands):
            if isinstance(op, ast.Name):
                if idx_fld is None:
                    idx_fld = idx
                else:
                    self.errorIt(op,
                        "Comparison of two fields not supported")
        if idx_fld is None:
            self.errorIt(it, "Where is a field fo compare?")
        field_name = operands[idx_fld].id
        if self.mCondEnv is not None:
            unit_kind, unit_h = self.mCondEnv.detectUnit(
                field_name, "numeric")
            if unit_kind != "numeric" or unit_h is None:
                self.errorIt(operands[idx_fld],
                    "Improper numeric field name: " + field_name)
        if len(operands) == 3 and idx_fld != 1:
            self.errorIt(it, "Too complex comparison")
        ret = ["numeric", field_name, [None, None], None]
        for idx, op in enumerate(operands):
            if idx < idx_fld:
                ret[2][0] = self.processFloat(op)
            elif idx > idx_fld:
                ret[2][1] = self.processFloat(op)
        markers.append([ret, operands[idx_fld]])
        return ret

    #===============================================
    def processInt(self, it):
        if not isinstance(it, ast.Num) or not isinstance(it.n, int):
            self.errorIt(it, "Integer is expected")
        return it.n

    #===============================================
    def processFloat(self, it):
        if not isinstance(it, ast.Num) or (
                not isinstance(it.n, int) and not isinstance(it.n, float)):
            self.errorIt(it, "Int or float is expected: %r" % it.n)
        return it.n

    #===============================================
    def processIntSet(self, it):
        if not isinstance(it, ast.Set):
            self.errorIt(it, "Set of integers is expected")
        ret = set()
        for el in it.elts:
            val = self.processInt(el)
            if el.n in ret:
                self.errorIt(el, "Duplicated int value")
            ret.add(val)
        return ret

    #===============================================
    def modifyCode(self, instr):
        mode, loc, new_cond = instr
        assert mode == "mark"
        frag_h = self.mFragments[loc[0]]
        frag_h.getMarkers()[loc[1]][0][:] = new_cond
        code_lines = self.mCode.splitlines()
        line_from, line_to = frag_h.getLineDiap()
        dummy_lines = []
        for line_no in range(*frag_h.getLineDiap()):
            if line_no in self.mDummyLinesReg:
                dummy_lines.append(code_lines[line_no - 1])
        code_lines[line_from - 1: line_to] = (dummy_lines
            + formatIfCode(frag_h.getCondData()).splitlines())
        return "\n".join(code_lines)


if __name__ == '__main__':
    source = sys.stdin.read()
    parser = ParsedDTree(None, source)

    if parser.getError() is not None:
        print("Error:", parser.getError())
    if parser.getFragments() is not None:
        print("Done:", len(parser.getFragments()))
