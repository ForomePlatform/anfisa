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

import sys, ast, json
from hashlib import md5

from forome_tools.log_err import logException
from .condition import ConditionMaker
from .code_works import normalizeCode
from .code_parse import parseCodeByPortions
#===============================================
class TreeFragment:
    def __init__(self, level, tp, line_diap,
            base_instr = None, err_info = None, decision = None,
            cond_data = None, cond_atoms = None, label = None):
        self.mLevel = level
        self.mType = tp
        self.mLineDiap = line_diap
        self.mBaseInstr = base_instr
        self.mErrInfo = err_info
        self.mCondData = cond_data
        self.mDecision = decision
        self.mCondAtoms = cond_atoms if cond_atoms is not None else []
        self.mLabel = label

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

    def getLabel(self):
        return self.mLabel

    def getCondAtoms(self):
        return self.mCondAtoms

    def _getAtom(self, cond_data, is_optional = False):
        for atom_info in self.mCondAtoms:
            if cond_data is atom_info.getCondData():
                return atom_info
        assert is_optional, ("Condition atom not found: "
            + json.dumps(cond_data))
        return None

    def _setAtomError(self, cond_data, err_msg):
        self._getAtom(cond_data).setError(err_msg)

#===============================================
class CondAtomInfo:
    def __init__(self, cond_data, location, warn_msg = None):
        self.mCondData = cond_data
        self.mLoc = location
        self.mErrorMsg = warn_msg

    def setError(self, error_msg):
        self.mErrorMsg = error_msg

    def getLoc(self):
        return self.mLoc

    def getCondData(self):
        return self.mCondData

    def resetCondData(self, values):
        self.mCondData[:] = values

    def getErrorMsg(self):
        return self.mErrorMsg

#===============================================
class ParsedDTree:
    def __init__(self, eval_space, dtree_code):
        self.mEvalSpace = eval_space
        self.mFragments = []
        self.mCode = normalizeCode(dtree_code)
        self.mDummyLinesReg = set()
        self.mLabels = dict()
        self.mFirstError = None
        hash_h = md5()
        code_lines = self.mCode.splitlines()

        for parsed_d, err_info, line_diap in parseCodeByPortions(
                code_lines, self.mDummyLinesReg):
            fragments = []
            if parsed_d is None or len(parsed_d.body) != 1:
                err_info = ("Improper instruction", line_diap[0], 0)
            if err_info is None:
                self.mError = None
                self.mCurLineDiap = line_diap
                try:
                    instr_d = parsed_d.body[0]
                    if isinstance(instr_d, ast.Return):
                        fragments.append(TreeFragment(0, "Return", line_diap,
                            decision = self.getReturnValue(instr_d)))
                    elif (isinstance(instr_d, ast.Expr)
                            and isinstance(instr_d.value, ast.Call)):
                        fragments.append(self.processCall(instr_d.value,
                            len(self.mFragments)))
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
                if self.mFirstError is None:
                    self.mFirstError = err_info
            self.mFragments += fragments
        self.mHashCode = hash_h.hexdigest()
        self.mCurLineDiap = None
        self.mError = None
        self.mCondAtoms = None
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
        if self.mFirstError is None:
            self.mFirstError = self.mError

    def getError(self):
        return self.mFirstError

    def getTreeCode(self):
        return self.mCode

    def getEvalSpace(self):
        return self.mEvalSpace

    def getFragments(self):
        return self.mFragments

    def getHashCode(self):
        return self.mHashCode

    def isLineIsDummy(self, line_no):
        return line_no in self.mDummyLinesReg

    def errorIt(self, it, msg_text):
        self.mError = (msg_text,
            it.lineno + self.mCurLineDiap[0] - 1, it.col_offset)
        if self.mFirstError is None:
            self.mFirstError = self.mError
        raise RuntimeError()

    def errorMsg(self, line_no, col_offset, msg_text):
        self.mError = (msg_text,
            line_no + self.mCurLineDiap[0] - 1, col_offset)
        if self.mFirstError is None:
            self.mFirstError = self.mError
        raise RuntimeError()

    def _regCondAtom(self, cond_data, it, it_name, warn_msg = None):
        self.mCondAtoms.append(
            CondAtomInfo(cond_data,
                [it.lineno + self.mCurLineDiap[0] - 1,
                it.col_offset,
                it.col_offset + len(it_name)], warn_msg))

    #===============================================
    def processIf(self, instr_d):
        self.mCondAtoms = []
        cond_data = self._processCondition(instr_d.test)
        if len(instr_d.orelse) > 0:
            self.errorIt(instr_d.orelse[0],
                "Else instruction is not supported")
        line_from, line_to = self.mCurLineDiap
        decision = self.getSingleReturnValue(instr_d.body)
        line_decision = instr_d.body[0].lineno + line_from - 1
        ret = [
            TreeFragment(0, "If", (line_from, line_decision),
                cond_atoms = self.mCondAtoms, cond_data = cond_data),
            TreeFragment(1, "Return",
                (line_decision, line_to), decision = decision)]
        self.mCondAtoms = None
        return ret

    #===============================================
    def processCall(self, instr, point_no):
        assert isinstance(instr, ast.Call)
        if instr.func.id != "label":
            self.errorIt(instr, "Only label() function supported on top level")
        if len(instr.args) != 1 or len(instr.keywords) != 0:
            self.errorIt(instr, "Only one argument expected for label()")
        if isinstance(instr.args[0], ast.Str):
            label = instr.args[0].s
        elif isinstance(instr.args[0], ast.Name):
            label = instr.args[0].id
        else:
            self.errorIt(instr.args[0],
                "String is expected as argument of label()")
        if label in self.mLabels:
            self.errorIt(instr, "Duplicate label %s" % label)
        self.mLabels[label] = point_no
        frag_h = TreeFragment(0, "Label", self.mCurLineDiap, label = label)
        return frag_h

    #===============================================
    def getReturnValue(self, instr):
        if isinstance(instr.value, ast.NameConstant):
            if instr.value.value in (True, False):
                return instr.value.value
        self.errorIt(instr,
            "Only boolean return (True/False) is expected here")
        return None

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
    def _processCondition(self, it):
        if isinstance(it, ast.BoolOp):
            if isinstance(it.op, ast.And):
                seq = ["and"]
            elif isinstance(it.op, ast.Or):
                seq = ["or"]
            else:
                self.errorIt(it, "Logic operation not supported")
            for val in it.values:
                rep_el = self._processCondition(val)
                if len(rep_el) == 0:
                    continue
                if rep_el[0] == seq[0]:
                    seq += rep_el[1:]
                else:
                    seq.append(rep_el)
            if len(seq) == 0:
                return []
            return seq
        if isinstance(it, ast.UnaryOp):
            if not isinstance(it.op, ast.Not):
                self.errorIt(it, "Unary operation not supported")
            return ["not", self._processCondition(it.operand)]
        if not isinstance(it, ast.Compare):
            self.errorIt(it, "Comparison or logic operation expected")
        if len(it.ops) == 1 and (isinstance(it.ops[0], ast.In)
                or isinstance(it.ops[0], ast.NotIn)):
            return self._processEnumInstr(it)
        return self._processNumInstr(it)

    #===============================================
    def _processEnumInstr(self, it):
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

        variants = self.processIdSet(it_set)
        #if len(variants) == 0:
        #    self.errorIt(it_set, "Empty set")

        if isinstance(it.left, ast.Name):
            field_name = it.left.id
            warn_msg = None
            cond_data = ["enum", field_name, op_mode, variants]
            if self.mEvalSpace is not None:
                unit_h = self.mEvalSpace.getUnit(field_name)
                if unit_h is None:
                    warn_msg = "Inactive enum field"
                    cond_data = ConditionMaker.coverError(
                        cond_data, op_mode == "NOT")
                else:
                    if not unit_h.isInDTrees():
                        self.errorIt(it.left,
                            "No support for field %s in decision trees"
                                % field_name)
                    elif unit_h.getUnitKind() == "func":
                        self.errorIt(it.left,
                            "Field %s should be used as function" % field_name)
                    if unit_h.getUnitKind() != "enum":
                        self.errorIt(it.left, "Improper enum field name: "
                            + field_name)
            self._regCondAtom(cond_data, it.left, it.left.id, warn_msg)
            return cond_data

        if isinstance(it.left, ast.Call):
            field_name = it.left.func.id
            func_args, warn_msg = dict(), None
            cond_data = ["func", field_name, op_mode, variants, func_args]
            if self.mEvalSpace is None:
                # No parameters w/o eval space, parse only
                del cond_data[2:]
            else:
                unit_h = self.mEvalSpace.getUnit(field_name)
                if unit_h is None:
                    warn_msg = "Inactive function"
                    cond_data = ConditionMaker.coverError(
                        cond_data, op_mode == "NOT")
                elif unit_h.getUnitKind() != "func":
                    self.errorIt(it.left, "Improper functional field name: "
                        + field_name)
                else:
                    parameters = unit_h.getParameters()[:]
                    for it_arg in it.left.args:
                        if len(parameters) == 0:
                            self.errorIt(it_arg, "Extra argument of function")
                        func_args[parameters.pop(0)] = self.processJSonData(
                            it_arg)
                    for argval_it in it.left.keywords:
                        if argval_it.arg in func_args:
                            self.errorIt(argval_it.value,
                                "Argument %s duplicated" % argval_it.arg)
                        if argval_it.arg not in parameters:
                            self.errorIt(argval_it.value,
                                "Argument %s not expected" % argval_it.arg)
                        func_args[argval_it.arg] = self.processJSonData(
                            argval_it.value)
                        parameters.remove(argval_it.arg)
                    err_msg = unit_h.validateArgs(func_args)
                    if err_msg:
                        self.errorIt(it.left, err_msg)
            self._regCondAtom(cond_data, it.left, it.left.func.id, warn_msg)
            return cond_data
        self.errorIt(it.left, "Name of field is expected")
        return None

    #===============================================
    sNumOpTab = [
        (ast.Lt,  1, False),
        (ast.LtE, 1, True),
        (ast.Eq,  0, True),
        (ast.GtE, -1, True),
        (ast.Gt, -1, False)]

    @classmethod
    def determineNumOp(cls, op):
        for op_class, ord_mode, eq_mode in cls.sNumOpTab:
            if isinstance(op, op_class):
                return (ord_mode, eq_mode)
        return None, None

    def _processNumInstr(self, it):
        op_modes = []
        for op in it.ops:
            if len(op_modes) > 1:
                op_modes = None
                break
            if len(op_modes) > 0 and op_modes[0][0] == 0:
                break
            op_modes.append(self.determineNumOp(op))
            if op_modes[-1][0] is None:
                self.errorIt(it, "Operation not supported")
        if op_modes is not None:
            if ((len(op_modes) == 2 and op_modes[0][0] != op_modes[1][0])
                    or len(op_modes) > 2):
                op_modes = None
        if not op_modes:
            self.errorIt(it, "Unexpected complexity of numeric comparison")

        operands = [it.left] + it.comparators[:]
        values = []
        idx_fld = None
        for idx, op in enumerate(operands):
            if isinstance(op, ast.Name):
                if idx_fld is None:
                    idx_fld = idx
                else:
                    self.errorIt(op,
                        "Comparison of two fields not supported")
            else:
                values.append(self.processFloat(op))
        if idx_fld is None:
            self.errorIt(it, "Where is a field fo compare?")
        field_node = operands[idx_fld]
        field_name = field_node.id
        bounds = [None, True, None, True]
        cond_data = ["numeric", field_name, bounds]
        warn_msg = None
        if self.mEvalSpace is not None:
            unit_h = self.mEvalSpace.getUnit(field_name)
            if unit_h is None:
                warn_msg = "Inactive numeric field"
                cond_data = ConditionMaker.coverError(cond_data)
            elif unit_h.getUnitKind() != "numeric":
                self.errorIt(operands[idx_fld],
                    "Improper numeric field name: " + field_name)
        if len(operands) == 3 and idx_fld != 1:
            self.errorIt(it, "Too complex comparison")
        assert len(values) == len(op_modes)
        if op_modes[0][0] == 0:
            assert len(op_modes) == 1 and len(values) == 1
            bounds[0] = values[0]
            bounds[2] = values[0]
        else:
            if op_modes[0][0] < 0:
                values = values[::-1]
                op_modes = op_modes[::-1]
                idx_fld = 0 if idx_fld > 0 else 1
            if idx_fld == 0:
                assert len(values) == 1
                bounds[2] = values[0]
                bounds[3] = op_modes[0][1]
            else:
                bounds[0] = values[0]
                bounds[1] = op_modes[0][1]
                if len(values) > 1:
                    bounds[2] = values[1]
                    bounds[3] = op_modes[1][1]
        if bounds[0] is not None and bounds[2] is not None:
            if ((bounds[0] == bounds[2] and not (bounds[1] and bounds[3]))
                    or bounds[0] > bounds[2]):
                self.errorIt(it, "Condition never success")
        self._regCondAtom(cond_data, field_node, field_name, warn_msg)
        return cond_data

    #===============================================
    def processInt(self, it):
        if not isinstance(it, ast.Num) or not isinstance(it.n, int):
            self.errorIt(it, "Integer is expected")
        return it.n

    #===============================================
    def processFloat(self, it):
        if not isinstance(it, ast.Num):
            self.errorIt(it, "Numeric is expected: %r" % it)
        if (not isinstance(it.n, int) and not isinstance(it.n, float)):
            self.errorIt(it, "Int or float is expected: %r" % it.n)
        return it.n

    #===============================================
    def processIdSet(self, it_set):
        if isinstance(it_set, ast.Dict) and len(it_set.keys) == 0:
            return []
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
        return variants

    #===============================================
    def processJSonData(self, it):
        if isinstance(it, ast.Num):
            return it.n
        if isinstance(it, ast.Str):
            return it.s
        if isinstance(it, ast.Name):
            return it.id
        if isinstance(it, ast.NameConstant):
            if it.value in (True, False, None):
                return it.value
            self.errorIt(it,
                "Constant %s not expected" % str(it.value))
        if (isinstance(it, ast.List)
                or isinstance(it, ast.Set)):
            return [self.processJSonData(el) for el in it.elts]
        if isinstance(it, ast.Dict):
            ret = dict()
            for idx, it_key in enumerate(it.keys):
                key = self.processJSonData(it_key)
                if isinstance(key, ast.List) or isinstance(key, ast.Dict):
                    self.errorIt(it_key,
                        "Combined keys for dict are not supported")
                ret[key] = self.processJSonData(it.values[idx])
            return ret
        self.errorIt(it, "Incorrect data format")
        return None


#===============================================
if __name__ == '__main__':
    source = sys.stdin.read()
    parser = ParsedDTree(None, source)

    if parser.getError() is not None:
        print("Error:", parser.getError())
    if parser.getFragments() is not None:
        print("Done:", len(parser.getFragments()))
