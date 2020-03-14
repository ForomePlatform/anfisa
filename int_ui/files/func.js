/*
 * Copyright (c) 2019. Partners HealthCare and other members of
 * Forome Association
 *
 * Developed by Sergey Trifonov based on contributions by Joel Krier,
 * Michael Bouzinier, Shamil Sunyaev and other members of Division of
 * Genetics, Brigham and Women's Hospital
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */


/**************************************/
/* Support for different functions
/**************************************/
var sOpFuncH = {
    mUnitStat: null,
    mFamily: null,
    mCurFuncH: null,
    mRuntimeErr: null,
    mTimeH: null,
    mOpVariants: null,
    mOpMode: null,

    init: function() {
        this.mFDict = {
            "inheritance-z": sFunc_InheritanceZ,
            "custom-inheritance-z": sFunc_CustomInheritanceZ,
            "comp-hets": sFunc_CompoundHet,
            "comp-request": sFunc_CompoundRequest,
            "region": sFunc_Region
        };
    },
    
    notSupported: function(unit_stat) {
        if (unit_stat["kind"] != "func")
            return false;
        return (!this.mFDict[unit_stat["sub-kind"]]);
    },

    dropDelay: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
    },
    
    stop: function() {
        this.dropDelay();
        this.mUnitStat = null;
        this.mCurFuncH = null;
        this.mRuntimeErr = null;
        this.mOpVariants = null;
        this.mOpMode = null;
    },
    
    setup: function(func_unit_stat) {
        this.stop();
        this.mUnitStat = func_unit_stat;
        this.mCurFuncH = this.mFDict[func_unit_stat["sub-kind"]];
        this.mCurFuncH.setup(func_unit_stat);
    },
    
    getCurParams: function() {
        return this.mCurFuncH.getCurParams();
    },
    
    updateCondition: function(cond_data) {
        this.mOpMode = cond_data[2];
        this.mOpVariants = cond_data[3];
        this.mCurFuncH.updateCondition(cond_data);
    },
    
    keepSelection: function() {
        this.mOpVariants = sOpEnumH.getSelected();
    },

    reloadStat: function() {
        zero_variants = this.mCurFuncH.checkBad();
        if (zero_variants != null) {
            sOpEnumH._setupVariants(zero_variants);
            sOpEnumH._updateState(this.mOpMode, this.mOpVariants);
            sOpEnumH.waitForUpdate();
            sOpEnumH.checkControls();
            return;
        }
        sOpEnumH.waitForUpdate();
        if (this.mTimeH == null) {
            this.mTimeH = setInterval(function(){sOpFuncH._reloadStat();}, 2);
        }
    },

    _reloadStat: function() {
        this.dropDelay();
        ajaxCall("statfunc", sUnitsH.getRqArgs() + "&unit=" + this.mUnitStat["name"] + 
            "&param=" + encodeURIComponent(JSON.stringify(this.mCurFuncH.getCurParams())),
            function(info){sOpFuncH._setupStat(info);})
    },
    
    _setupStat: function(info) {
        if (this.mUnitStat == null)
            return;
        this.mRuntimeErr = info["err"];
        if (this.mCurFuncH.acceptStat(info, this.mOpCondData) || this.mOpCondData) {
            sOpEnumH._setupVariants(info["variants"]);
            sOpEnumH._updateState(this.mOpMode, this.mOpVariants);
            this.mOpMode = null;
            sOpEnumH.checkControls();
        }
    },
    
    careControls: function(in_check) {
        this.mCurFuncH.checkControls(in_check);
    },
 
    checkError: function(pre_cond_data, err_msg) {
        if (this.mRuntimeErr)
            return this.mRuntimeErr;
        f_err_msg = this.mCurFuncH.checkError(pre_cond_data);
        if (f_err_msg)
            return f_err_msg;
        return err_msg;
    },
     
    renderParams: function() {
        sOpEnumH.renderFuncDiv(this.mCurFuncH.renderIt());
        this.careControls();
    }
}
    
/**************************************/
var sFunc_InheritanceZ = {
    mAffectedGroup: null,
    mFamily: null,
    mCurPGroup: null,
    mZeroVariants: null,
    
    setup: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mCurPGroup = null;
        this.mZeroVariants = [];
        for(idx = 0; idx < func_unit_stat["variants"].length; idx++)
            this.mZeroVariants.push([func_unit_stat["variants"][idx], 0]);
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            p_group = cond_data[4]["problem_group"];
            this.mCurPGroup = (p_group)? p_group : null;
            sOpFuncH.renderParams();
            sOpFuncH.reloadStat();
        } else {
            sOpEnumH.renderParams();
        }
    },
    
    checkBad: function() {
        if (this.mCurPGroup == null)
            return (this.mAffectedGroup.length == 0)? this.mZeroVariants: null;
        else
            return (this.mCurPGroup.length == 0)? this.mZeroVariants: null;
    },
    
    acceptStat: function(info, cond_data) {
        var p_group = info["problem_group"];
        if (!p_group)
            p_group = null;
        if (p_group && sameData(p_group, this.mAffectedGroup))
            p_group = null;
        return sameData(p_group, this.mCurPGroup);
    },
    
    getCurParams: function() {
        if (this.mCurPGroup)
            return {"problem_group": this.mCurPGroup};
        return {};
    },
    
    checkError: function(pre_cond_data) {
        if (this.checkBad() != null)
            return "Empty problem group";
        return null;
    },
     
    renderIt: function() {
        var list_stat_rep = ['<div class="func-parameters">',
            '<div class="comment">Problem group:</div>'];
        var p_group = (this.mCurPGroup == null)? this.mAffectedGroup : this.mCurPGroup;
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            sample_id = this.mFamily[idx];
            q_checked = (p_group.indexOf(sample_id) >= 0)? " checked":"";
            check_id = "inheritance-z-fam-m__" + idx;
            list_stat_rep.push('<div class="inheritance-z-fam-member">' + 
                '<input type="checkbox" id="' + check_id + '" ' + q_checked + 
                ' onchange="sFunc_InheritanceZ.checkControls();" /><label for="' +
                check_id + '">&nbsp;' + this.mFamily[idx] + '</div>');
        }
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div class="wrapped"><button id="inheritance-z-fam-reset" ' +
            ' title="Reset affected group" ' +
            'onclick="sFunc_InheritanceZ.resetGrp()">Reset</button></div>');
        list_stat_rep.push('</div>');        
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        var p_group = [];
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            if (document.getElementById("inheritance-z-fam-m__" + idx).checked)
                p_group.push(this.mFamily[idx]);
        }
        if (p_group.join('|') == this.mAffectedGroup.join('|'))
            p_group = null;
        document.getElementById("inheritance-z-fam-reset").disabled = (!p_group);
        if (sameData(p_group, this.mCurPGroup))
            return;
        this.mCurPGroup = p_group;
        sOpFuncH.keepSelection();
        sOpFuncH.reloadStat();
    },
 
    resetGrp: function() {
        sOpFuncH.keepSelection();
        this.mCurPGroup = null;
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    }
}
    
/**************************************/
sZygSuportH = {
    Z_MODES: ["0", "0-1", "1", "1-2", "2"],

    emptyScenario: function(scenario) {
        if (scenario.length == 0)
            return true;
        for (j=0; j < this.Z_MODES.length; j++)
            if (scenario[this.Z_MODES[j]])
                return false;
        return true;
    },

    emptyRequest: function(request) {
        for (idx=0; idx < request.length; idx++) {
            if (request[idx][0] >= 1 && !this.emptyScenario(request[idx][1]))
                return false;
        }
        return true;
    },
    
    renderScenario: function(
        scenario, family, ctrl_name, scope_option, out_rep) {
        var tab_fam = {};
        for (j=0; j < this.Z_MODES.length; j++) {
            if (scenario[this.Z_MODES[j]]) {
                for (idx=0; idx < scenario[this.Z_MODES[j]].length; idx++)
                    tab_fam[scenario[this.Z_MODES[j]][idx]] = j + 1;
            }
        }
        for (var idx = 0; idx < family.length; idx++) {
            sample_id = family[idx];
            q_val = (tab_fam[sample_id])? tab_fam[sample_id]:0;
            check_id = "c-inheritance-z-fam-m__" + idx + scope_option;
            out_rep.push('<div class="wrapped">' + sample_id + 
                '&nbsp;<select id="' + check_id + 
                '" onchange="' + ctrl_name + '.checkControls();">');
            out_rep.push('<option value="0" ' + ((q_val == 0)? "selected " : "") +
                '>--</option>');
            for (j=0; j < this.Z_MODES.length; j++) {
                out_rep.push('<option value="' + (j+1) + '" ' + 
                    ((q_val == j + 1)? "selected " : "") + '>' + this.Z_MODES[j] + '</option>');
            }
            out_rep.push('</select></div>')
        }
    },

    scanScenario: function(family, scope_option) {
        var scenario = {};
        for (j=0; j < this.Z_MODES.length; j++) {
            if (scenario[this.Z_MODES[j]]) {
                for (idx=0; idx < scenario[this.Z_MODES[j]].length; idx++)
                    tab_fam[this.Z_MODES[j][idx]] = j + 1;
            }
        }
        for (var idx = 0; idx < family.length; idx++) {
            sample_id = family[idx];
            check_id = "c-inheritance-z-fam-m__" + idx + scope_option;
            zyg_el = document.getElementById(check_id);
            zyg_val = parseInt(zyg_el.value);
            zyg_el.parentElement.className = (zyg_val > 0)? "":"blocked";
            if (zyg_val > 0) {
                if (scenario[this.Z_MODES[zyg_val - 1]])
                    scenario[this.Z_MODES[zyg_val - 1]].push(sample_id);
                else
                    scenario[this.Z_MODES[zyg_val - 1]] = [sample_id];
            }
        }
        return scenario;
    },

    buildScenario: function(family, affected_group, zyg_a, zyg_n) {
        group0 = [];
        group1 = [];
        for (var idx = 0; idx < family.length; idx++) {
            sample_id = family[idx];
            if (affected_group.indexOf(sample_id) >= 0)
                group0.push(sample_id);
            else
                group1.push(sample_id);
        }
        var scenario = {};
        if (group0.length > 0)
            scenario[zyg_a] = group0;
        if (group1.length > 0)
            scenario[zyg_n] = group1;
        return scenario;
    },
    
    evalResetVariants: function(family, affected_group) {
        return [{}, 
            this.buildScenario(family, affected_group, "2", "0-1"),
            this.buildScenario(family, affected_group, "1-2", "0"),
            this.buildScenario(family, affected_group, "0", "1-2")];
    },
    
    renderResetGroup: function(ctrl_name, out_rep) {
        out_rep.push('<div class="wrapped"><span class="comment">Reset</span>&nbsp;' +
            '<select id="inheritance-z-fam-reset-select" onchange="' +
            ctrl_name + '.resetScenario()" ><option value=""></option>');
        out_rep.push(
            '<option value="0">-empty-</option>' +
            '<option value="2|0-1">Homozygous Recessive/X-linked</option>' +
            '<option value="1-2|0">Autosomal Dominant</option>' +
            '<option value="0|1-2">Compensational</option>' +
            '</select></div>');
    },
    
    updateResetGroup: function(scenario, reset_variants) {
        var cur_idx = 0;
        for (idx=0; idx < 4; idx++) {
            if (sameData(scenario, reset_variants[idx])) {
                cur_idx = idx + 1;
                break;
            }
        }
        document.getElementById
            ("inheritance-z-fam-reset-select").selectedIndex = cur_idx;
    }
}

/**************************************/
var sFunc_CustomInheritanceZ = {
    mAffectedGroup: null,
    mFamily: null,
    mResetVariants: null,
    mCurScenario: null,
    
    setup: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mResetVariants = sZygSuportH.evalResetVariants(
            this.mFamily, this.mAffectedGroup);
        this.mCurScenario = this.mResetVariants[1];
        sOpFuncH.mOpVariants = ["True"];
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            p_scenario = cond_data[4]["scenario"];
            this.mCurScenario = (p_scenario)? p_scenario : {};
            sOpFuncH.renderParams();
            sOpFuncH.reloadStat();
        } else {
            sOpEnumH.renderParams();
        }
    },
    
    checkBad: function() {
        if (sZygSuportH.emptyScenario(this.mCurScenario)) {
            return [["True", 0]];
        }
        return null;
    },
    
    acceptStat: function(info, cond_data) {
        return sameData(info["scenario"], this.mCurScenario);
    },
    
    getCurParams: function() {
        return {"scenario": this.mCurScenario};
    },
    
    checkError: function(pre_cond_data) {
        if (sZygSuportH.emptyScenario(this.mCurScenario))
            return "Empty scenario";
        return null;
    },
     
    renderIt: function() {
        var list_stat_rep = ['<div class="func-parameters">',
            '<div class="comment">Scenario:</div>'];
        sZygSuportH.renderScenario(this.mCurScenario, 
            this.mFamily, "sFunc_CustomInheritanceZ", "", list_stat_rep);
        sZygSuportH.renderResetGroup("sFunc_CustomInheritanceZ", list_stat_rep);
        list_stat_rep.push('</div>');
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        var p_scenario = sZygSuportH.scanScenario(this.mFamily, "");
        sZygSuportH.updateResetGroup(p_scenario, this.mResetVariants);
        if (sameData(p_scenario, this.mCurScenario))
            return;
        sOpFuncH.keepSelection();
        this.mCurScenario = p_scenario;
        sOpFuncH.reloadStat();
    },

    resetScenario: function() {
        cur_idx = document.getElementById
            ("inheritance-z-fam-reset-select").selectedIndex;
        if (cur_idx > 0) {
            sOpFuncH.keepSelection();
            this.mCurScenario = this.mResetVariants[cur_idx - 1];
            sOpFuncH.renderParams();
            sOpFuncH.reloadStat();
        }
    }
}
    
/**************************************/
var sFunc_CompoundHet = {
    mLabels: null,
    mApproxModes: null,
    mApproxTitles: null,
    mCurApprox: null,
    mTrioVariants: null,
    mCurState: undefined,
    
    setup: function(func_unit_stat) {
        this.mLabels = func_unit_stat["labels"];
        this.mTrioVariants = func_unit_stat["trio-variants"];
        this.mApproxModes = [];
        this.mApproxTitles = [];
        for (idx = 0; idx< func_unit_stat["approx-modes"].length; idx++) {
            this.mApproxModes.push(func_unit_stat["approx-modes"][idx][0]);
            this.mApproxTitles.push(func_unit_stat["approx-modes"][idx][1]);
        }
        this.mCurApprox = null;
        this.mCurState = null;
        sOpFuncH.mOpVariants = [this.mTrioVariants[0]];
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            v_approx = cond_data[4]["approx"];
            v_state = cond_data[4]["state"];
            if (this.mApproxModes.indexOf(v_approx) < 1)
                v_approx = null;
            if (this.mLabels.indexOf(v_state) < 0)
                v_state = null;
            if (v_approx != this.mCurApprox || v_state != this.mCurState) {
                this.mCurApprox = v_approx;
                this.mCurState = v_state;
                sOpFuncH.renderParams();
            }
            sOpFuncH.reloadStat();
        }
    },
    
    acceptStat: function(info, cond_data) {
        v_approx = info["approx"];
        v_state = info["state"];
        if (this.mApproxModes.indexOf(v_approx) < 1)
            v_approx = null;
        if (this.mLabels.indexOf(v_state) < 0)
            v_state = null;
        return (v_approx == this.mCurApprox && v_state == this.mCurState);
    },
    
    getCurParams: function() {
        var ret = {};
        if (this.mCurApprox)
            ret["approx"] = this.mCurApprox;
        if (this.mCurState)
            ret["state"] = this.mCurState;
        return ret;
    },
    
    checkBad: function() {
        return null;
    },
    
    checkError: function(pre_cond_data) {
        if (pre_cond_data == null)
            return null;
        v_approx = pre_cond_data[2]["approx"];
        v_state = pre_cond_data[2]["state"];
        if (v_approx && this.mApproxModes.indexOf(v_approx) < 0)
            return "Bad approx mode: " + v_approx;
        if (v_state && this.mLabels.indexOf(v_state) < 0)
            return "Label " + v_state + " not found";
        return null;
    },
     
    renderIt: function() {
        var list_stat_rep = ['<div class="func-parameters">',
            '<div><span class="comment">Approx:</span>&nbsp;<select ' + 
            'id="compound-het-approx" onchange="sFunc_CompoundHet.checkControls();"' + 
            ((this.mApproxModes.length == 1)? " disabled":"") + '>'];
        for (idx = 0; idx < this.mApproxModes.length; idx++) {
            list_stat_rep.push('<option value="' + this.mApproxModes[idx] + '" ' +
                ((this.mApproxModes[idx] == this.mCurApprox || (idx == 0 && !this.mCurApprox))?
                    " selected ": "") +
                '>' + this.mApproxTitles[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push(
            '<div><span class="comment">State:</span>&nbsp;<select ' + 
            'id="compound-het-state" onchange="sFunc_CompoundHet.checkControls();"' + 
            ((this.mLabels.length == 0)? " disabled":"") + '>');
        list_stat_rep.push(
            '<option value=""' + ((this.mLabels.length == 0)? " selected":"") + '>' +
            '-current-</option>');
        for (idx = 0; idx < this.mLabels.length; idx++) {
            list_stat_rep.push('<option value="' + this.mLabels[idx] + '" ' +
                ((this.mLabels[idx] == this.mCurState)? " selected ": "") +
                '>' + this.mLabels[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push('<div></div></div>');
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        v_approx = document.getElementById('compound-het-approx').value;
        v_state = document.getElementById('compound-het-state').value;
        if (this.mApproxModes.indexOf(v_approx) < 1)
            v_approx = null;
        if (this.mLabels.indexOf(v_state) < 0)
            v_state = null;
        if (v_approx != this.mCurApprox || v_state != this.mCurState) {
            this.mCurApprox = v_approx;
            this.mCurState = v_state;
            sOpFuncH.keepSelection();
            sOpFuncH.reloadStat();
        }
    }        
}
    
/**************************************/
var sFunc_CompoundRequest = {
    mLabels: null,
    mApproxModes: null,
    mApproxTitles: null,
    mAffectedGroup: null,
    mFamily: null,
    mCurApprox: null,
    mCurRequest: undefined,
    mCurState: undefined,
    mCurRequest: null,
    mCurLine: null,
    mPrevCurLine: null,
    
    setup: function(func_unit_stat) {
        this.mLabels = func_unit_stat["labels"];
        this.mApproxModes = [];
        this.mApproxTitles = [];
        for (idx = 0; idx< func_unit_stat["approx-modes"].length; idx++) {
            this.mApproxModes.push(func_unit_stat["approx-modes"][idx][0]);
            this.mApproxTitles.push(func_unit_stat["approx-modes"][idx][1]);
        }
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mResetVariants = sZygSuportH.evalResetVariants(
            this.mFamily, this.mAffectedGroup);
        this.mCurApprox = null;
        this.mCurState = null;
        this.mCurLine = 0;
        this.mPrevCurLine = null;
        this.mCurRequest = [[1, {}]];
        sOpFuncH.mOpVariants = ["True"];
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            v_approx = cond_data[4]["approx"];
            v_state = cond_data[4]["state"];
            v_request = cond_data[4]["request"];
            if (this.mApproxModes.indexOf(v_approx) < 1)
                v_approx = null;
            if (this.mLabels.indexOf(v_state) < 0)
                v_state = null;
            if (v_request.length == 0)
                v_request = [[1, {}]];
            if (v_approx != this.mCurApprox || v_state != this.mCurState ||
                    !sameData(v_request, this.mCurRequest)) {
                this.mCurApprox = v_approx;
                this.mCurState = v_state;
                this.mCurRequest = v_request;
                sOpFuncH.renderParams();
            }
            sOpFuncH.reloadStat();
        }
    },
    
    acceptStat: function(info, cond_data) {
        v_approx = info["approx"];
        v_state = info["state"];
        v_request = info["request"];
        if (this.mApproxModes.indexOf(v_approx) < 1)
            v_approx = null;
        if (this.mLabels.indexOf(v_state) < 0)
            v_state = null;
        return (v_approx == this.mCurApprox && v_state == this.mCurState &&
            sameData(v_request, this.mCurRequest));
    },
    
    getCurParams: function() {
        var ret = {"request": this.mCurRequest};
        if (this.mCurApprox)
            ret["approx"] = this.mCurApprox;
        if (this.mCurState)
            ret["state"] = this.mCurState;
        return ret;
    },
    
    checkBad: function() {
        if (sZygSuportH.emptyRequest(this.mCurRequest)) {
            return [["True", 0]];
        }
        return null;
    },
    
    checkError: function(pre_cond_data) {
        if (pre_cond_data == null)
            return null;
        v_approx = pre_cond_data[2]["approx"];
        v_state = pre_cond_data[2]["state"];
        v_request = pre_cond_data[2]["request"];
        if (sZygSuportH.emptyRequest(v_request))
            return "Empty request";
        if (v_approx && this.mApproxModes.indexOf(v_approx) < 0)
            return "Bad approx mode: " + v_approx;
        if (v_state && this.mLabels.indexOf(v_state) < 0)
            return "Label " + v_state + " not found";
        return null;
    },
     
    renderIt: function() {
        this.mPrevCurLine = null;
        var list_stat_rep = [
            '<div class="func-parameters">' +
            '<div><span class="comment">Approx:</span>&nbsp;<select ' + 
            'id="compound-het-approx" onchange="sFunc_CompoundRequest.checkControls();"' + 
            ((this.mApproxModes.length == 1)? " disabled":"") + '>'];
        for (idx = 0; idx < this.mApproxModes.length; idx++) {
            list_stat_rep.push('<option value="' + this.mApproxModes[idx] + '" ' +
                ((this.mApproxModes[idx] == this.mCurApprox || (idx == 0 && !this.mCurApprox))?
                    " selected ": "") +
                '>' + this.mApproxTitles[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push(
            '<div><span class="comment">State:</span>&nbsp;<select ' + 
            'id="compound-het-state" onchange="sFunc_CompoundRequest.checkControls();"' + 
            ((this.mLabels.length == 0)? " disabled":"") + '>');
        list_stat_rep.push(
            '<option value=""' + ((this.mLabels.length == 0)? " selected":"") + '>' +
            '-current-</option>');
        for (idx = 0; idx < this.mLabels.length; idx++) {
            list_stat_rep.push('<option value="' + this.mLabels[idx] + '" ' +
                ((this.mLabels[idx] == this.mCurState)? " selected ": "") +
                '>' + this.mLabels[idx] + '</option>');
        }
        list_stat_rep.push('</select></div></div>');
        list_stat_rep.push('<div id="comp-rq-request">');
        for (idx = 0; idx < this.mCurRequest.length; idx++) {
            list_stat_rep.push('<div class="comp-rq-item-block"' +
                ' id="comp-rq-line' + idx + '"' +
                ' onclick="sFunc_CompoundRequest.setCur(' + idx + ')">');
            list_stat_rep.push('<div class="wrapped">' +
                '<input type="number" min="0"' +
                ' title = "minimal count of events" class="w50"' +
                ' id="comp-rq-item--' + idx + '"' +
                ' onchange="sFunc_CompoundRequest.checkControls()"' + 
                ' value="' + this.mCurRequest[idx][0] + '"/></div>');
            sZygSuportH.renderScenario(this.mCurRequest[idx][1], 
                this.mFamily, "sFunc_CompoundRequest", "__" + idx, list_stat_rep);
            list_stat_rep.push('</div>');
        }
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div class="func-parameters">');
        list_stat_rep.push('<div class="wrapped"><button ' + 
            ((this.mCurRequest.length < 5)? "": "disabled ") + 
            'onclick="sFunc_CompoundRequest.addLine()">Add</button></div>');
        list_stat_rep.push('<div class="wrapped"><button ' + 
            ((this.mCurRequest.length > 1)? "": "disabled ") + 
            'onclick="sFunc_CompoundRequest.delLine()">Remove</button></div>');
        sZygSuportH.renderResetGroup("sFunc_CompoundRequest", list_stat_rep);
        list_stat_rep.push('</div>');
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        v_approx = document.getElementById('compound-het-approx').value;
        v_state = document.getElementById('compound-het-state').value;
        v_request = [];
        for (idx = 0; idx < this.mCurRequest.length; idx++) {
            v_request.push([parseInt(document.getElementById("comp-rq-item--" + idx).value),
                sZygSuportH.scanScenario(this.mFamily, "__" + idx)]);
        }
        if (this.mApproxModes.indexOf(v_approx) < 1)
            v_approx = null;
        if (this.mLabels.indexOf(v_state) < 0)
            v_state = null;
        if (v_approx != this.mCurApprox || v_state != this.mCurState || 
            !sameData(v_request, this.mCurRequest)) {
            this.mCurApprox = v_approx;
            this.mCurState = v_state;
            this.mCurRequest = v_request;
            sOpFuncH.keepSelection();
            sOpFuncH.reloadStat();
        }
        if (this.mPrevCurLine != null) {
            line_el = document.getElementById("comp-rq-line" + this.mPrevCurLine);
            if (line_el) {
                line_el.className = line_el.className.split(' ')[0];
            }
        }
        this.mCurLine = Math.min(this.mCurLine, this.mCurRequest.length - 1);
        this.mPrevCurLine = this.mCurLine;
        line_el = document.getElementById("comp-rq-line" + this.mPrevCurLine);
        line_el.className = line_el.className.split(' ')[0] + ' cur';
        sZygSuportH.updateResetGroup(
            this.mCurRequest[this.mCurLine][1], this.mResetVariants);
    },
    
    setCur: function(line_no) {
        this.mCurLine = line_no;
        this.checkControls();
    },
    
    addLine: function() {
        this.mCurLine = this.mCurRequest.length;
        this.mCurRequest.push([1, {}]);
        sOpFuncH.keepSelection();
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    delLine: function() {
        this.mCurRequest.splice(this.mCurLine, 1);
        sOpFuncH.keepSelection();
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    resetScenario: function() {
        cur_idx = document.getElementById
            ("inheritance-z-fam-reset-select").selectedIndex;
        if (cur_idx > 0) {
            sOpFuncH.keepSelection();
            this.mCurRequest[this.mCurLine][1] = this.mResetVariants[cur_idx - 1];
            sOpFuncH.renderParams();
            sOpFuncH.reloadStat();
        }
    }
}

/**************************************/
var sFunc_Region = {
    mCurLocus: undefined,
    
    setup: function(func_unit_stat) {
        this.mCurLocus = func_unit_stat["locus"];
        if (!this.mCurLocus)
            this.mCurLocus = null;
        sOpFuncH.mOpVariants = ["True"];
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            v_locus = cond_data[4]["locus"];
            if (v_locus != this.mCurLocus) {
                this.mCurLocus = v_locus;
            }
            sOpFuncH.renderParams();
            sOpFuncH.reloadStat();
        } else {
            sOpEnumH.renderParams();
        }
    },
    
    acceptStat: function(info, cond_data) {
        v_locus = info["locus"];
        return (v_locus == this.mCurLocus);
    },
    
    getCurParams: function() {
        var ret = {};
        if (this.mCurLocus)
            ret["locus"] = this.mCurLocus;
        return ret;
    },
    
    checkBad: function() {
        if (!this.mCurLocus) {
            return [["True", 0]];
        }
        return null;
    },
    
    checkError: function(pre_cond_data) {
        if (pre_cond_data == null)
            return null;
        v_locus = pre_cond_data[2]["locus"];
        if (!v_locus)
            return "Locus is empty";
        return null;
    },
     
    renderIt: function() {
        var list_stat_rep = ['<div class="func-parameters">',
            '<div><span class="comment">Locus:</span>&nbsp;<input ' + 
            'id="region-locus" onchange="sFunc_Region.checkControls();" ' +
            ((this.mCurLocus)? 'value="' + escapeText(this.mCurLocus) + '"' : '') + 
            '>'];
        list_stat_rep.push('</div></div>');
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        v_locus = document.getElementById('region-locus').value.trim();
        if (v_locus != this.mCurLocus) {
            this.mCurLocus = v_locus;
            sOpFuncH.keepSelection();
            sOpFuncH.reloadStat();
        }
    }        
}
    
