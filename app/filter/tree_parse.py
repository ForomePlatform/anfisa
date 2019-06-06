import sys, ast, traceback, logging
from StringIO import StringIO
from collections import defaultdict

from app.config.solutions import Solutions
from .code_works import reprConditionCode, findComment
#===============================================
class TreeFragment:
    def __init__(self, level, type, base_instr):
        self.mLevel = level
        self.mType = type
        self.mBaseInstr = base_instr
        self.mBaseLineDiap = None
        self.mFullLineDiap = None
        self.mCondData = None
        self.mDecision = None
        self.mImportEntries = None
        self.mMarkers = []

    def setLineDiap(self, base_diap, full_diap):
        self.mBaseLineDiap = base_diap
        self.mFullLineDiap = full_diap

    def getLevel(self):
        return self.mLevel

    def getInstrType(self):
        return self.mType

    def getBaseInstr(self):
        return self.mBaseInstr

    def getBaseLineDiap(self):
        return self.mBaseLineDiap

    def getFullLineDiap(self):
        return self.mFullLineDiap

    def getCondData(self):
        return self.mCondData

    def getDecision(self):
        return self.mDecision

    def getImportEntries(self):
        return self.mImportEntries

    def addMarker(self, point_cond, name_instr):
        self.mMarkers.append([point_cond, name_instr])

    def getMarkers(self):
        return self.mMarkers

    def getMarkerInstr(self, idx):
        return self.mMarkers[idx][1]

    def getMarkerIdx(self, point_cond):
        for idx, point_info in enumerate(self.mMarkers):
            if point_info[0] is point_cond:
                return idx
        assert False

    def _removeMarker(self, idx):
        del self.mMarkers[idx]

    def setCondData(self, cond_data):
        assert self.mCondData is None
        self.mCondData = cond_data

    def setDecision(self, decision):
        assert self.mDecision is None
        self.mDecision = decision

    def setImportEntries(self, import_entries):
        self.mImportEntries = import_entries


#===============================================
class ParsedDecisionTree:
    @staticmethod
    def parse(cond_env, code, instr):
        parser = ParsedDecisionTree(cond_env, code)
        if parser.getError() is not None:
            return parser
        if instr is not None:
            code = parser.modifyCode(instr)
            parser = ParsedDecisionTree(cond_env, code)
        return parser

    #===============================================
    def __init__(self, cond_env, code):
        self.mCondEnv = cond_env
        self.mFragments = []
        self.mCode = code
        self.mError = None
        self.mImportFragments = {}

        try:
            top_d = ast.parse(self.mCode)
        except SyntaxError as err:
            txt_len = len(err.text.rstrip())
            self.mError = ("Syntax error", max(0, err.lineno),
                max(0, min(err.offset, txt_len - 1)))
            self.mFragments = None
            return

        try:
            last_instr = len(top_d.body) - 1
            for idx, instr_d in enumerate(top_d.body):
                self.processInstr(instr_d, idx == last_instr)
            if self.mError is None:
                self.arrangeDiapasons()
        except Exception as err:
            if self.mError is None:
                rep = StringIO()
                traceback.print_exc(file = rep, limit = 10)
                logging.error("Exception on parse code. Stack:\n" +
                    rep.getvalue())
                raise err
            self.mFragments = None

    def getError(self):
        return self.mError

    def getTreeCode(self):
        return self.mCode

    def getCondEnv(self):
        return self.mCondEnv

    def getFragments(self):
        return self.mFragments

    def getCurFrag(self):
        return self.mFragments[-1]

    def errorIt(self, it, msg_text):
        self.mError = (msg_text, it.lineno, it.col_offset)
        raise RuntimeError()

    def errorMsg(self, line_no, col_offset, msg_text):
        self.mError = (msg_text, line_no, col_offset)
        raise RuntimeError()

    #===============================================
    def processInstr(self, instr, q_last_instr):
        if q_last_instr:
            if isinstance(instr, ast.Return):
                self.mFragments.append(
                    TreeFragment(0, "Return", instr))
                self.getCurFrag().setDecision(
                    self.getReturnValue(instr))
            else:
                self.errorIt(instr,
                    "Last instructon must return True/False")
        else:
            if isinstance(instr, ast.If):
                self.mFragments.append(
                    TreeFragment(0, "If", instr))
                self._processIf(instr)
            elif isinstance(instr, ast.Import):
                self.mFragments.append(
                    TreeFragment(0, "Import", instr))
                self._processImport(instr)
            else:
                self.errorIt(instr,
                    "Instructon must be of if-type")

    #===============================================
    def _processIf(self, instr):
        self.getCurFrag().setCondData(
            self._processCondition(instr.test))
        self.mFragments.append(TreeFragment(1, "Return",
            instr.body[0]))
        self.getCurFrag().setDecision(
            self.getSingleReturnValue(instr.body))
        if len(instr.orelse) > 0:
            self.errorIt(instr.orelse[0],
                "Else instruction is not supported")

    #===============================================
    def _processImport(self, instr):
        import_entries = []
        for entry in instr.names:
            if entry.asname is not None:
                self.errorIt(instr, "entry with path not supported")
            if (entry.name in self.mImportFragments or
                    entry.name in import_entries):
                self.errorIt(instr, "duplicate import: " + entry.name)
            unit_kind, _ = self.mCondEnv.detectUnit(entry.name)
            if unit_kind in (None, "reserved"):
                self.errorIt(instr, "Case does not provide: " + entry.name)
            if unit_kind != "operational":
                self.errorIt(instr, "improper name for import: " + entry.name)
            import_entries.append(entry.name)
        self.mFragments[-1].setImportEntries(import_entries)
        for nm in import_entries:
            self.mImportFragments[nm] = self.mFragments[-1]

    #===============================================
    def arrangeDiapasons(self):
        if len(self.mFragments) == 0:
            return
        lines = self.mCode.splitlines()
        empty_lines_no = set()
        comment_lines_no = set()
        max_line_no = None
        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                empty_lines_no.add(line_idx + 1)
            else:
                max_line_no = line_idx + 1
                if stripped.startswith('#'):
                    comment_lines_no.add(line_idx + 1)
        diap_seq = []
        for frag in self.mFragments:
            base_instr = frag.getBaseInstr()
            line_no, offset = base_instr.lineno, base_instr.col_offset
            if offset > 0 and not lines[line_no - 1][:offset - 1].isspace():
                self.errorIt(base_instr, "Split line before instruction")
            cur_diap = [line_no, line_no]
            if len(diap_seq) == 0:
                cur_diap[0] = 1
            else:
                while (cur_diap[0] - 1 > diap_seq[-1][1] and
                        cur_diap[0] - 1 in comment_lines_no):
                    cur_diap[0] -= 1
                diap_seq[-1][1] = cur_diap[0] - 1
            diap_seq.append(cur_diap)
        diap_seq[-1][1] = max_line_no

        for idx, frag in enumerate(self.mFragments):
            full_diap = diap_seq[idx]
            base_diap = full_diap[:]
            while (base_diap[0] in empty_lines_no or
                    base_diap[0] in comment_lines_no):
                base_diap[0] += 1
                assert base_diap[0] <= base_diap[1]
            while (base_diap[1] in empty_lines_no or
                    base_diap[1] in comment_lines_no):
                base_diap[1] -= 1
                assert base_diap[0] <= base_diap[1]
            loc = findComment("\n".join(
                lines[base_diap[0] - 1: base_diap[1]]))
            if loc is not None:
                line_no, offset = loc
                self.errorMsg(base_diap[0] + line_no - 1, offset,
                    "Sorry, no comments inside instructions")
            frag.setLineDiap(base_diap, full_diap)

    #===============================================
    #===============================================
    def getReturnValue(self, instr):
        if isinstance(instr.value, ast.Name):
            result = instr.value.id
            if result in ("True", "False"):
                return result == "True"
        self.errorIt(instr.value,
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
                if rep_el[0] == seq[0]:
                    seq += rep_el[1:]
                else:
                    seq.append(rep_el)
            if seq[0] == "and":
                return self._clearConjunction(seq)
            return seq
        if isinstance(it, ast.UnaryOp):
            if not isinstance(it.op, ast.Not):
                self.errorIt(it, "Unary operation not supported")
            return ["not", self._processCondition(it.operand)]
        if not isinstance(it, ast.Compare):
            self.errorIt(it, "Comparison or logic operation expected")
        if len(it.ops) == 1 and (isinstance(it.ops[0], ast.In) or
                isinstance(it.ops[0], ast.NotIn)):
            return self._processEnumInstr(it)
        return self._processNumInstr(it)

    #===============================================
    def _processEnumInstr(self, it):
        assert len(it.comparators) == 1
        it_set = it.comparators[0]
        panel_name = None
        if isinstance(it.ops[0], ast.NotIn):
            op_mode = "NOT"
        else:
            assert isinstance(it.ops[0], ast.In)
            op_mode = "OR"

        if isinstance(it_set, ast.Call):
            if (len(it_set.args) != 1 or len(it_set.keywords) > 0 or
                    it_set.kwargs or it_set.starargs or
                    not it_set.func or
                    not isinstance(it_set.func, ast.Name)):
                self.errorIt(it_set, "Complex call not supported")
            if it_set.func.id == "all":
                if op_mode == "NOT":
                    self.errorIt(it_set, "Complex call not supported")
                op_mode = "AND"
                it_set = it_set.args[0]
            elif  it_set.func.id == "panel":
                if self.mCondEnv is None:
                    self.errorIt(it_set, "No panel support")
                it_set = it_set.args[0]
                if isinstance(it_set, ast.Str):
                    panel_name = it_set.s
                elif isinstance(it_set, ast.Name):
                    panel_name = it_set.id
                else:
                    self.errorIt(it_set, "Panel id expected")
            else:
                self.errorIt(it_set,
                    "Only pseudo-functions all/panel supported")

        if panel_name is None:
            if not (isinstance(it_set, ast.List) or
                    isinstance(it_set, ast.Set)):
                self.errorIt(it_set, "Set (or list) expected")
            variants = []
            for el in it_set.elts:
                if isinstance(el, ast.Str):
                    val = el.s
                elif isinstance(el, ast.Name):
                    val = el.id
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
                unit_kind, unit_h = self.mCondEnv.detectUnit(field_name, "enum")
                if unit_kind == "operational":
                    if field_name not in self.mImportFragments:
                        self.errorIt(it.left,
                            "Field %s not imported" % field_name)
                    return ["operational", field_name, op_mode, variants]
                if unit_kind != "enum":
                    self.errorIt(it.left, "Improper enum field name")
            if panel_name is not None:
                variants = Solutions.getPanel(field_name, panel_name)
                if variants is None:
                    self.errorIt(it_set, "Panel not found")
                ret = ["panel", field_name, op_mode, panel_name]
            else:
                ret = ["enum", field_name, op_mode, variants]
                self.getCurFrag().addMarker(ret, it.left)
            return ret

        if panel_name is not None:
            self.errorIt(it_set, "Panel supported only for enumerated fields")

        if isinstance(it.left, ast.Call):
            if (len(it.left.keywords) > 0 or
                    it.left.kwargs or it.left.starargs or
                    not isinstance(it.left.func, ast.Name)):
                self.errorIt(it.left, "Complex call not supported")
            field_name = it.left.func.id
            assert self.mCondEnv is not None
            unit_kind, unit_h = self.mCondEnv.detectUnit(
                field_name, "special")
            if unit_kind != "special":
                self.errorIt(it.left, "Improper special field name")
            ret = unit_h.processInstr(self,it.left.args, op_mode, variants)
            if ret is None:
                self.errorIt(it.left,
                    "Improper arguments for special field")
            self.getCurFrag().addMarker(ret, it.left)
            return ret
        self.errorIt(it.left, "Name of field is expected")

    #===============================================
    def _processNumInstr(self, it):
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
            if unit_kind != "numeric":
                self.errorIt(operands[idx_fld],
                    "Improper numeric field name")
        if len(operands) == 3 and idx_fld != 1:
            self.errorIt(it, "Too complex comparison")
        ret = ["numeric", field_name, [None, None], None]
        for idx, op in enumerate(operands):
            if idx < idx_fld:
                ret[2][0] = self.processFloat(op)
            elif idx > idx_fld:
                ret[2][1] = self.processFloat(op)
        self.getCurFrag().addMarker(ret, operands[idx_fld])
        return ret

    #===============================================
    def _clearConjunction(self, ret_seq):
        unit_groups = defaultdict(list)
        for cond in ret_seq:
            if cond[0] == "numeric":
                unit_groups[cond[1]].append(cond)
        idxs_to_remove = []
        for cond_seq in unit_groups.values():
            if len(cond_seq) < 2:
                continue
            sheet = []
            for cond in cond_seq:
                sheet.append((self.getCurFrag().getMarkerIdx(cond), cond))
            sheet.sort()
            bounds_base = sheet[0][1][2]
            for cond_info in sheet[-1:0:-1]:
                bounds = cond_info[1][2]
                for j in (0, 1):
                    if bounds[j] is not None:
                        if bounds_base[j] is not None:
                            self.errorIt(self.getCurFrag().
                                getMarkerInstr(cond_info[0]),
                                "Too heavy numeric condition")
                        bounds_base[j] = bounds[j]
                self.getCurFrag()._removeMarker(cond_info[0])
                idxs_to_remove.append(ret_seq.index(cond_info[1]))
        ret = ret_seq[:]
        for idx in sorted(idxs_to_remove)[::-1]:
            del ret[idx]
        return ret

    #===============================================
    def processInt(self, it):
        if not isinstance(it, ast.Num) or not any(
                [isinstance(it.n, tp) for tp in (int, long)]):
            self.errorIt(it, "Integer is expected")
        return it.n

    #===============================================
    def processFloat(self, it):
        if not isinstance(it, ast.Num) or not any(
                [isinstance(it.n, tp) for tp in (int, long, float)]):
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
        frag = self.mFragments[loc[0]]
        frag.getMarkers()[loc[1]][0][:] = new_cond
        code_lines = self.mCode.splitlines()
        line_from, line_to = frag.getBaseLineDiap()
        code_lines[line_from - 1: line_to] = reprConditionCode(
            frag.getCondData()).splitlines()
        return "\n".join(code_lines)

if __name__ == '__main__':
    source = sys.stdin.read()
    parser = ParsedDecisionTree(None, source)

    if parser.getError() is not None:
        print >> sys.stdout, "Error:", parser.getError()
    if parser.getFragments() is not None:
        print >> sys.stdout, "Done:", len(parser.getFragments())
