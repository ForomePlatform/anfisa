# -*- coding: utf-8 -*-

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
from xml.sax.saxutils import escape
from bitarray import bitarray

from app.view.attr import AttrH
#===============================================
# Transcript details support
#===============================================
def markupTranscriptTab(info_handle, view_context, aspect):
    if "details" not in view_context or len(info_handle["colhead"]) == 0:
        return
    it_map = bitarray(view_context["details"])
    assert aspect.getColGroups().getAttr(0) == "transcripts", (
        "For aspect " + aspect.getName() + " does not support trancripts")
    for grp_info in info_handle["colhead"][1:]:
        grp_info[2] = " no-hit"
    tr_group_info = info_handle["colhead"][0]
    cnt_total = tr_group_info[1]
    hit_col_idxs = set()
    for idx in range(cnt_total):
        if it_map[idx]:
            hit_col_idxs.add(idx)
    if len(hit_col_idxs) < cnt_total:
        title, _, _ = tr_group_info[0].partition('[')
        title += f"[{len(hit_col_idxs)}/{cnt_total}]"
    else:
        title = tr_group_info[0]
    tr_group_info[0] = title + '&nbsp;<span id="tr-hit-span"></span>'
    for row in info_handle["rows"]:
        for idx, td_info in enumerate(row["cells"]):
            if idx in hit_col_idxs:
                td_info[1] += ' hit'
            else:
                td_info[1] += ' no-tr-hit'

#===============================================
def reprGenTranscripts(val, v_context):
    if not val or len(val) == 0:
        return (None, None)
    if "details" in v_context:
        details = bitarray(v_context["details"])
    else:
        details = None

    ret_handle = ['<table id="gen-transcripts">',
        '<tr class="tr-head">'
        '<td>canonical?</td><td>id</td><td>gene</td><td>annotations</td>'
        '</tr>']
    for idx, it in enumerate(val):
        is_canonical = it.get("is_canonical")
        is_hit = (details is not None and details[idx])
        v_id = it.get("id", "?")
        v_gene = it.get("gene", "?")
        if v_gene is None:
            v_gene = "?"
        v_annotation = " ".join(it.get("transcript_annotations", []))

        v_tr = ' class="tr-canonical"' if is_canonical else ""
        v_td = ' checked' if is_canonical else ""

        ret_handle.append(
            f'<tr{v_tr}><td class="tr-canonical">'
            f'<input type="checkbox" disabled{v_td}></input></td>')
        id_class = "hit tr-id" if is_hit else "tr-id"
        ret_handle.append(
            f'<td class="{id_class}">{escape(v_id)}</td>'
            f'<td class="tr-gene">{escape(v_gene)}</td>'
            f'<td class="tr-annot">{escape(v_annotation)}</td></tr>')
    ret_handle.append("</table>")
    return ('\n'.join(ret_handle), "norm")

#===============================================
# Samples support
#===============================================
class SamplesColumnsMarkup:
    def __init__(self, ds_h):
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mCohortMap = self.mFamilyInfo.getCohortMap()

    def __call__(self, info_handle, view_context, aspect):
        if self.mCohortMap is None and "active-samples" not in view_context:
            return
        par_ctrl = ["", ""]
        par_modes = []
        cohort_row = None
        hit_columns = []
        col_seq = [""] * len(info_handle["rows"][0]["cells"])
        if self.mCohortMap:
            cohort_row = {
                "name": "_cohort",
                "title": "Cohorts",
                "cells": []}
            for idx, td_info in enumerate(info_handle["rows"][0]["cells"]):
                if idx == 0:
                    cohort_row["cells"].append(["-", "null"])
                    continue
                sample_name = td_info[0].split()[-1]
                cohort = self.mCohortMap[sample_name]
                cohort_row["cells"].append([cohort, "string"])
                col_seq[idx] = 'cohort-' + cohort
            par_ctrl[1] = '<span id="cohorts-ctrl"></span>'
            par_modes.append(["cohorts"])
        act_samples = view_context.get("active-samples")
        if act_samples:
            cnt_total = 0
            for idx, td_info in enumerate(info_handle["rows"][0]["cells"]):
                if idx == 0:
                    continue
                sample_name = td_info[0].split()[-1]
                smp_idx = self.mFamilyInfo.sampleIdx(sample_name)
                cnt_total += 1
                if col_seq[idx]:
                    col_seq[idx] += ' '
                if smp_idx in act_samples:
                    hit_columns.append(idx)
                else:
                    col_seq[idx] += "no-smp-hit"
            if len(hit_columns) > 0 and cnt_total > 3:
                par_ctrl[0] = ('<span id="act-samples-ctrl">'
                    f'[{len(hit_columns)}/{cnt_total}]</span>')
                par_modes.append(["hit", hit_columns, cnt_total])
        info_handle["colgroup"] = [""] + col_seq
        info_handle["parcontrol"] = '<div>' + ' '.join(par_ctrl) + '</div>'
        info_handle["parmodes"] = par_modes
        if cohort_row:
            info_handle["rows"].insert(0, cohort_row)
        if len(hit_columns) > 0:
            for idx in hit_columns:
                for row in info_handle["rows"]:
                    row["cells"][idx][1] += " hit"

#===============================================
def normSampleId(sample_name):
    if '[' in sample_name:
        _, _, nm = sample_name.partition('[')
        return nm.rpartition(']')[0].strip()
    return sample_name.strip()

#===============================================
class SamplesConditionVisitor:
    def __init__(self, ds_h):
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mSelectedSamples = set()

    def getName(self):
        return "active-samples"

    def lookAt(self, condition):
        if not condition.isPositive():
            return False
        if condition.getCondType().startswith("enum"):
            unit_name, variants = condition.getData()[:2]
            if unit_name == "Has_Variant":
                for var in variants:
                    self.mSelectedSamples.add(var)
        return True

    def makeResult(self):
        ret = []
        for sample_name in self.mSelectedSamples:
            smp_idx = self.mFamilyInfo.sampleIdx(normSampleId(sample_name))
            if smp_idx is not None:
                ret.append(smp_idx)
        return ','.join(map(str, sorted(ret)))

#===============================================
class OpHasVariant_AttrH(AttrH):
    def __init__(self, view, ds_h):
        AttrH.__init__(self, "OP_has_variant",
            title = "Has variant",
            tooltip = "Samples having variant")
        self.mDS = ds_h
        self.mFamilyInfo = self.mDS.getFamilyInfo()
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        active_samples = v_context.get("active-samples")

        list_hit, list_norm = [], []
        for sample_name in v_context["data"]["_filters"]["has_variant"]:
            if ' [' in sample_name:
                sample_name = sample_name.replace(' [', '[')
            if active_samples:
                smp_idx = self.mFamilyInfo.sampleIdx(normSampleId(sample_name))
                if smp_idx in active_samples:
                    list_hit.append(sample_name)
                    continue
            list_norm.append(sample_name)
        rep_hit = ""
        if len(list_hit) > 0:
            rep_hit = ('<span class="hit">'
                + escape(' '.join(list_hit)) + '</span> ')
        return (rep_hit + escape(' '.join(list_norm)), "norm")

#===============================================
# Operative filtrations support
#===============================================
class OpFilters_AttrH(AttrH):
    def __init__(self, view, ds_h):
        AttrH.__init__(self, "OP_filters",
            title = "Presence in filters",
            tooltip = "Filters positive on variant")
        self.mDS = ds_h
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        return (' '.join(self.mDS.getRecFilters(v_context["rec_no"])), "norm")

#===============================================
class OpDTrees_AttrH(AttrH):
    def __init__(self, view, ds_h):
        AttrH.__init__(self, "OP_dtrees",
            title = "Presence in decision trees",
            tooltip = "Decision trees positive on variant")
        self.mDS = ds_h
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        return (' '.join(self.mDS.getRecDTrees(v_context["rec_no"])), "norm")
