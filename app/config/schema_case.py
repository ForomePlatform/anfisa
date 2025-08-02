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

#===============================================
import os
from app.eval.var_reg import VarRegistry
from app.view.view_model import ViewModel
from app.view.colgrp import ColGroupsH
from .flt_schema import defineFilterMaster_Case
from .flt_tune import tuneUnits_Case
from .view_tune import tuneAspects_Case

class DS_Schema_Case:

    #===============================================
    @staticmethod
    def defineViewModel(metadata_record = None, schema_modes = None):
        data_schema = (metadata_record.get("data_schema")
            if metadata_record else None)
        if schema_modes is None:
            schema_modes = set()
        assert data_schema in (None, "CASE"), (
            "Bad data schema: " + data_schema)

        cohorts = metadata_record.get("cohorts") if metadata_record else None

        if cohorts and "COHORTS" not in schema_modes:
            schema_modes.add("COHORTS")

        viewModel = ViewModel.loadY(
            os.path.dirname(__file__) + "/view_schema.yaml", schema_modes)

        if cohorts:
            cohort_columns = [["ALL",  "ALL"]] + [
                [ch["name"],  ch.get("title",  ch["name"])] for ch in cohorts]
            viewModel["view_cohorts"].setColGroups(ColGroupsH(
                attr_title_pairs = cohort_columns, single_group_col = True))

        return viewModel

    @staticmethod
    def defineVariables(sol_broker=None, metadata_record=None, ds_kind=None):
        var_registry = VarRegistry(
            os.path.dirname(__file__) + "/var_config.yaml",
            os.path.dirname(__file__) + "/variables.yaml")
        if metadata_record is not None:
            cohorts = metadata_record.get("cohorts")
            if cohorts:
                ch_names = [cohort_info["name"] for cohort_info in cohorts]
                var_registry.makeTemplatedVarSeq("Cohort_{}_AF", ch_names)
                var_registry.makeTemplatedVarSeq("Cohort_{}_AF2", ch_names)

        if sol_broker is not None:
            submitters = sol_broker.getStdItemData(
                "item-dict", "Clinvar_Trusted_Submitters").values()
            var_registry.makeTemplatedVarSeq(
                "ClinVar_Significance_{}", submitters)
        return var_registry

    @staticmethod
    def defineFilterMaster(metadata_record, ds_kind, druid_adm = None):
        return defineFilterMaster_Case(metadata_record, ds_kind, druid_adm)

    @staticmethod
    def tuneUnits(ds_h):
        return tuneUnits_Case(ds_h)

    @staticmethod
    def tuneAspects(ds_h, aspects):
        return tuneAspects_Case(ds_h, aspects)
