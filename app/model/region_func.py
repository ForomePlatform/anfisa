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

from app.eval.var_unit import FunctionUnit
#===============================================
class RegionFuncUnit(FunctionUnit):
    @staticmethod
    def makeIt(ds_h, descr, map_units, before = None, after = None):
        unit_h = RegionFuncUnit(ds_h, descr, map_units)
        ds_h.getEvalSpace()._insertUnit(unit_h, before = before, after = after)
        ds_h.getEvalSpace()._addFunction(unit_h)

    def __init__(self, ds_h, descr, map_units):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "region", parameters = ["locus"])
        self.mMapUnits = map_units

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        if variants is None or "True" in variants:
            yield ("True", context["loc-condition"])

    def makeInfoStat(self, eval_h, stat_ctx, point_no):
        return self.prepareStat(stat_ctx)

    def makeParamStat(self, condition, parameters, eval_h, stat_ctx, point_no):
        ret_handle = self.prepareStat(stat_ctx)
        ret_handle.update(parameters)
        loc_condition, error_msg = self.parse(parameters.get("locus"))
        if loc_condition is None:
            ret_handle["variants"] = None
            ret_handle["err"] = error_msg
        else:
            self.collectComplexStat(ret_handle, condition,
                {"loc-condition": loc_condition})
        return ret_handle

    def locateContext(self, cond_data, eval_h):
        if len(cond_data[3]) == 0:
            eval_h.operationError(cond_data,
                "%s: empty set of variants" % self.getName())
            return None
        loc_condition, error_msg = self.parse(cond_data[4].get("locus"))
        if loc_condition is None:
            eval_h.operationError(cond_data, error_msg)
            return None
        return {"loc-condition": loc_condition}

    def validateArgs(self, func_args):
        if func_args.get("locus"):
            _, error_msg = self.parse(func_args["locus"])
            return error_msg
        return None

    def parse(self, locus):
        if not locus:
            return None, "Empty locus"
        loc_parts = [part.strip() for part in locus.split(':')]
        if len(loc_parts) > 3:
            return None, "Bad locus: many fields"
        if len(loc_parts) < 2:
            return None, "Bad locus: too short"

        seq_cond = []

        if loc_parts[0]:
            chrom_val = loc_parts[0].upper()
            if chrom_val.startswith("CHR"):
                chrom_val = chrom_val[3:]
            if (chrom_val.isdigit()):
                if not (1 <= int(chrom_val) <= 23):
                    chrom_val = None
            elif chrom_val not in {"M", "X", "Y"}:
                chrom_val = None
            if chrom_val is None:
                return None, "Bad chromosome"
            seq_cond.append(self.getEvalSpace().makeEnumCond(
                self.getEvalSpace().getUnit(self.mMapUnits["chrom"]),
                ["chr" + chrom_val]))

        if loc_parts[1]:
            if len(seq_cond) == 0:
                return None, "No chromosome defined"
            start_val, sep, end_val = loc_parts[1].partition('-')
            start_val = start_val.strip()
            if not start_val.isdigit() or len(start_val) > 10:
                return None, "Bad start position"
            start_val = int(start_val)
            seq_cond.append(self.getEvalSpace().makeNumericCond(
                self.getEvalSpace().getUnit(self.mMapUnits["start"]),
                min_val = start_val, min_eq = True))
            if not sep:
                end_val = start_val
            else:
                end_val = end_val.strip()
                if not end_val.isdigit() or len(end_val) > 10:
                    return None, "Bad end position"
                end_val = int(end_val.strip())
            seq_cond.append(self.getEvalSpace().makeNumericCond(
                self.getEvalSpace().getUnit(self.mMapUnits["end"]),
                max_val = end_val, max_eq = True))

        if len(loc_parts) > 2:
            gene_values = [val.strip() for val in loc_parts[2].split(',')]
            if len(gene_values) < 1 or not all(gene_values) or max(
                    len(val) for val in gene_values) > 30:
                return None, "Bad gene values"
            seq_cond.append(self.getEvalSpace().makeEnumCond(
                self.getEvalSpace().getUnit(self.mMapUnits["symbol"]),
                gene_values))

        if len(seq_cond) == 0:
            return None, "Empty locus"

        return self.getEvalSpace().joinAnd(seq_cond), None
