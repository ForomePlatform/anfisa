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
    mCurFState: null,

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
        this.mCurFState = null;
    },
    
    setup: function(func_unit_stat) {
        this.stop();
        this.mUnitStat = func_unit_stat;
        this.mCurFuncH = this.mFDict[func_unit_stat["sub-kind"]];
        this.mCurFState = this.mCurFuncH.setupFState(func_unit_stat);
        sOpEnumH.renderFuncDiv(this.mCurFuncH.renderIt(this.mCurFState));
        var avail_variants = this.mCurFuncH.getVariants();
        if (avail_variants.length == 1)
            this.mOpVariants = avail_variants;
        else
            this.mOpVariants = [];
        this.mOpMode = "OR";
        this.renderVariants();
        this.reloadStat();
    },
    
    makeFuncParams: function() {
        if (this.mCurFuncH.checkBad(this.mCurFState))
            return null;
        return this.mCurFuncH.makeFParams(this.mCurFState);
    },
    
    getCurFState: function() {
        return this.mCurFState;
    },
    
    updateCondition: function(cond_data) {
        this.mOpMode = cond_data[2];
        this.mOpVariants = cond_data[3];
        this.resetFState(this.mCurFuncH.updateFState(cond_data), false);
        this.renderVariants();
        this.reloadStat();
    },
    
    resetFState: function(state, keep_selection) {
        if (keep_selection)
            this.mOpVariants = sOpEnumH.getSelected();
        this.mCurFState = state;
        if (this.mCurFuncH.onReset(this.mCurFState)) {
            sOpEnumH.renderFuncDiv(this.mCurFuncH.renderIt(this.mCurFState));
        }
        this.reloadStat();
    },
    
    renderVariants: function(variants_stat) {
        if (!variants_stat) {
            var_value = this.mCurFuncH.checkBad(this.mCurFState)? '-':'?';
            if (this.mRuntimeErr)
                var_value = '-';
            variants_stat = [];
            for(idx = 0; idx < this.mCurFuncH.getVariants().length; idx++)
                variants_stat.push(
                    [this.mCurFuncH.getVariants()[idx], var_value]);
        }
        sOpEnumH._setupVariants(variants_stat, true);
        sOpEnumH._updateState(this.mOpMode, this.mOpVariants);
    },
    
    reloadStat: function() {
        if (this.mCurFuncH.checkBad(this.mCurFState)) {
            this.renderVariants()
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
        if (this.mCurFuncH.checkBad(this.mCurFState))
            return;
        ajaxCall("statfunc", sUnitsH.getRqArgs(true) + 
            "&unit=" + this.mUnitStat["name"] + "&param=" +
            encodeURIComponent(JSON.stringify(this.makeFuncParams())),
            function(info){sOpFuncH._setupStat(info);})
    },
    
    _setupStat: function(info) {
        if (this.mUnitStat == null)
            return;
        if (!sUnitsH.checkRqId(info))
            return;
        var ret_state = this.mCurFuncH.parseFState(info);
        this.mRuntimeErr = info["err"];
        if (sameData(ret_state, this.mCurFState))
            this.renderVariants(info["variants"]);
        sOpEnumH.checkControls();
    },
    
    careControls: function() {
        var state = this.mCurFuncH.checkFControls();
        if (!sameData(state, this.mCurFState)) {
            this.resetFState(state, true);
        }
    },
 
    checkCurError: function() {
        if (this.mRuntimeErr)
            return this.mRuntimeErr;
        if (this.mCurFState == null)
            return null;
        return this.mCurFuncH.checkError(this.mCurFState);
    }
}
    
/**************************************/
var sFunc_InheritanceZ = {
    mAffectedGroup: null,
    mFamily: null,
    mAvailVariants: null,
    mTP: "inheritance",
    
    setupFState: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mAvailVariants = func_unit_stat["available"];
        return [null];
    },
    
    normPGroup: function(p_group) {
        if (!p_group  || sameData(p_group, this.mAffectedGroup))
            return null;
        return p_group;
    },
    
    updateFState: function(cond_data) {
        return [this.normPGroup(cond_data[4]["problem_group"])];
    },

    parseFState: function(info) {
        return [this.normPGroup(info["problem_group"])];
    },    
    
    getVariants: function() {
        return this.mAvailVariants;
    },
    
    makeFParams: function(state) {
        return {"problem_group": state[0]};
    },
    
    checkBad: function(state) {
        return (!state[0] && this.mAffectedGroup.length == 0);
    },
    
    checkError: function(state) {
        var p_group = state[0];
        if (p_group || (p_group == null && this.mAffectedGroup.length > 0))
            return null;
        return "Empty problem group";
    },
    
    onReset: function(state) {
        var p_group = state[0];
        if (p_group == null)
            p_group = this.mAffectedGroup;
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            sample_id = this.mFamily[idx];
            document.getElementById("inheritance-z-fam-m__" + idx).checked =
                (p_group.indexOf(sample_id) >= 0);
        }
        return false;
    },
     
    renderIt: function(state) {        
        var list_stat_rep = ['<div class="func-parameters">',
            '<div class="comment">Problem group:</div>'];
        var p_group = state[0];
        if (p_group == null)
            p_group = this.mAffectedGroup;
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            sample_id = this.mFamily[idx];
            q_checked = (p_group.indexOf(sample_id) >= 0)? " checked":"";
            check_id = "inheritance-z-fam-m__" + idx;
            list_stat_rep.push('<div class="inheritance-z-fam-member">' + 
                '<input type="checkbox" id="' + check_id + '" ' + q_checked + 
                ' onchange="sOpFuncH.careControls();" /><label for="' +
                check_id + '">&nbsp;' + this.mFamily[idx] + '</div>');
        }
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div class="wrapped"><button id="inheritance-z-fam-reset" ' +
            ' title="Reset affected group" ' +
            'onclick="sFunc_InheritanceZ.resetGrp()">Reset</button></div>');
        list_stat_rep.push('</div>');        
        return list_stat_rep.join('\n');
    },   

    checkFControls: function() {
        var p_group = [];
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            if (document.getElementById("inheritance-z-fam-m__" + idx).checked)
                p_group.push(this.mFamily[idx]);
        }
        p_group = this.normPGroup(p_group);
        document.getElementById("inheritance-z-fam-reset").disabled = (!p_group);
        return [p_group];
    },
 
    resetGrp: function() {
        sOpFuncH.resetFState([null], true);
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
    
    simplifyRequest: function(request) {
        var is_full = true;
        for (idx=0; idx < request.length; idx++) {
            if (request[idx][0] < 1 || this.emptyScenario(request[idx][1])) { 
                is_full = false;
                break;
            }
        }
        if (is_full) 
            return request;
        var request_norm = [];
        for (idx=0; idx < request.length; idx++) {
            if (request[idx][0] < 1 || this.emptyScenario(request[idx][1]))
                continue;
            request_norm.push(request[idx]);
        }        
        return request_norm;
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
                '" onchange="sOpFuncH.careControls();">');
            out_rep.push('<option value="0" ' + ((q_val == 0)? 'selected ' : '') +
                '>--</option>');
            for (j=0; j < this.Z_MODES.length; j++) {
                out_rep.push('<option value="' + (j+1) + '" ' + 
                    ((q_val == j + 1)? 'selected ' : '') + '>' + this.Z_MODES[j] + '</option>');
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
    
    setupFState: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mResetVariants = sZygSuportH.evalResetVariants(
            this.mFamily, this.mAffectedGroup);
        return [this.mResetVariants[1]];
    },

    normScenario: function(p_scenario) {
        if (!p_scenario)
            return {};
        return p_scenario;
    },
    
    updateFState: function(cond_data) {
        return [this.normScenario(cond_data[4]["scenario"])];
    },

    parseFState: function(info) {
        return [this.normScenario(info["scenario"])];
    },

    getVariants: function() {
        return ["True"];
    },
    
    makeFParams: function(state) {
        return {"scenario": state[0]};
    },
    
    checkBad: function(state) {
        return sZygSuportH.emptyScenario(state[0]);
    },
    
    checkError: function(state) {
        var p_scenario = state[0];
        if (!sZygSuportH.emptyScenario(p_scenario))
            return " ";
        return "Empty scenario";
    },
     
    onReset: function(state) {
        return true;
    },

    renderIt: function(state) {
        var list_stat_rep = ['<div class="func-parameters">',
            '<div class="comment">Scenario:</div>'];
        sZygSuportH.renderScenario(state[0], 
            this.mFamily, "sFunc_CustomInheritanceZ", "", list_stat_rep);
        sZygSuportH.renderResetGroup("sFunc_CustomInheritanceZ", list_stat_rep);
        list_stat_rep.push('</div>');
        return list_stat_rep.join('\n');
    },   

    checkFControls: function() {
        var p_scenario = sZygSuportH.scanScenario(this.mFamily, "");
        sZygSuportH.updateResetGroup(p_scenario, this.mResetVariants);
        return [p_scenario];
    },

    resetScenario: function() {
        cur_idx = document.getElementById
            ("inheritance-z-fam-reset-select").selectedIndex;
        if (cur_idx > 0) {
            sOpFuncH.resetFState([this.mResetVariants[cur_idx - 1]], true);
        }
    }
}
    
/**************************************/
var sFunc_CompoundHet = {
    mLabels: null,
    mApproxModes: null,
    mApproxTitles: null,
    mTrioVariants: null,
    
    setupFState: function(func_unit_stat) {
        this.mLabels = func_unit_stat["labels"];
        this.mTrioVariants = func_unit_stat["trio-variants"];
        this.mApproxModes = [];
        this.mApproxTitles = [];
        for (idx = 0; idx< func_unit_stat["approx-modes"].length; idx++) {
            this.mApproxModes.push(func_unit_stat["approx-modes"][idx][0]);
            this.mApproxTitles.push(func_unit_stat["approx-modes"][idx][1]);
        }
        return [null, null];
    },
    
    normApproxMode: function(v_approx) {
        if (this.mApproxModes.indexOf(v_approx) < 1)
            return null;
        return v_approx;
    },
    
    normVState: function(v_state) {
        if (this.mLabels.indexOf(v_state) < 0)
            return null;
        return v_state;
    },
        
    updateFState: function(cond_data) {
        return [
            this.normApproxMode(cond_data[4]["approx"]),
            this.normVState(cond_data[4]["state"])];
    },

    parseFState: function(info) {
        return [
            this.normApproxMode(info["approx"]),
            this.normVState(info["state"])];
    },
    
    getVariants: function() {
        return this.mTrioVariants;
    },

    makeFParams: function(state) {
        return {"approx": state[0], "state": state[1]};
    },
    
    checkBad: function(state) {
        return false;
    },
    
    checkError: function(state) {
        var v_approx = state[0];
        var v_state = state[1];
        if (v_approx && this.mApproxModes.indexOf(v_approx) < 0)
            return "Bad approx mode: " + v_approx;
        if (v_state && this.mLabels.indexOf(v_state) < 0)
            return "Label " + v_state + " not found";
        if (this.mTrioVariants.length == 1)
            return " ";
        return null;
    },
     
    onReset: function(state) {
        return true;
    },

    renderIt: function(state) {
        v_approx = state[0];
        v_state = state[1];
        var list_stat_rep = ['<div class="func-parameters">',
            '<div><span class="comment">Approx:</span>&nbsp;<select ' + 
            'id="compound-het-approx" onchange="sOpFuncH.careControls();"' + 
            ((this.mApproxModes.length == 1)? " disabled":"") + '>'];
        for (idx = 0; idx < this.mApproxModes.length; idx++) {
            list_stat_rep.push('<option value="' + this.mApproxModes[idx] + '" ' +
                ((this.mApproxModes[idx] == v_approx || (idx == 0 && !v_approx))?
                    " selected ": "") +
                '>' + this.mApproxTitles[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push(
            '<div><span class="comment">State:</span>&nbsp;<select ' + 
            'id="compound-het-state" onchange="sOpFuncH.careControls();"' + 
            ((this.mLabels.length == 0)? " disabled":"") + '>');
        list_stat_rep.push(
            '<option value=""' + ((this.mLabels.length == 0)? " selected":"") + '>' +
            '-current-</option>');
        for (idx = 0; idx < this.mLabels.length; idx++) {
            list_stat_rep.push('<option value="' + this.mLabels[idx] + '" ' +
                ((this.mLabels[idx] == v_state)? " selected ": "") +
                '>' + this.mLabels[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push('<div></div></div>');
        return list_stat_rep.join('\n');
    },   

    checkFControls: function() {
        return [
            this.normApproxMode(
                document.getElementById('compound-het-approx').value),
            this.normVState(
                document.getElementById('compound-het-state').value)];
    }        
}
    
/**************************************/
var sFunc_CompoundRequest = {
    mLabels: null,
    mApproxModes: null,
    mApproxTitles: null,
    mAffectedGroup: null,
    mFamily: null,
    mResetVariants: null,
    mCurLine: null,
    mPrevCurLine: null,
    
    setupFState: function(func_unit_stat) {
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
        this.mCurLine = 0;
        this.mPrevCurLine = null;
        return [null, null, [[1, {}]]];
    },
    
    normApproxMode: function(v_approx) {
        if (this.mApproxModes.indexOf(v_approx) < 1)
            return null;
        return v_approx;
    },
    
    normVState: function(v_state) {
        if (this.mLabels.indexOf(v_state) < 0)
            return null;
        return v_state;
    },

    normRequest: function(v_request) {
        if (v_request.length == 0)
            return [[1, {}]];
        return v_request;
    },
    
    updateFState: function(cond_data) {
        return [
            this.normApproxMode(cond_data[4]["approx"]),
            this.normVState(cond_data[4]["state"]),
            this.normRequest(cond_data[4]["request"])];
    },

    parseFState: function(info) {
        return [
            this.normApproxMode(info["approx"]),
            this.normVState(info["state"]),
            this.normRequest(info["request"])];
    },
    
    getVariants: function() {
        return ["True"];
    },
    
    makeFParams: function(state) {
        var v_request = sZygSuportH.simplifyRequest(state[2]);
        return {"approx": state[0], "state": state[1],
            "request": v_request};
    },
        
    checkBad: function(state) {
        return sZygSuportH.emptyRequest(state[2]);
    },
    
    checkError: function(state) {
        var v_approx = state[0];
        var v_state = state[1];
        var v_request = state[2];
        if (sZygSuportH.emptyRequest(v_request))
            return "Empty request";
        if (v_approx && this.mApproxModes.indexOf(v_approx) < 0)
            return "Bad approx mode: " + v_approx;
        if (v_state && this.mLabels.indexOf(v_state) < 0)
            return "Label " + v_state + " not found";
        return " ";
    },
     
    onReset: function(state) {
        return true;
    },

    renderIt: function(state) {
        v_approx = state[0];
        v_state = state[1];
        v_request = state[2];
        this.mPrevCurLine = null;
        var list_stat_rep = [
            '<div class="func-parameters">' +
            '<div><span class="comment">Approx:</span>&nbsp;<select ' + 
            'id="compound-het-approx" onchange="sOpFuncH.careControls();"' + 
            ((this.mApproxModes.length == 1)? " disabled":"") + '>'];
        for (idx = 0; idx < this.mApproxModes.length; idx++) {
            list_stat_rep.push('<option value="' + this.mApproxModes[idx] + '" ' +
                ((this.mApproxModes[idx] == v_approx || (idx == 0 && !v_approx))?
                    " selected ": "") +
                '>' + this.mApproxTitles[idx] + '</option>');
        }
        list_stat_rep.push('</select></div>');
        list_stat_rep.push(
            '<div><span class="comment">State:</span>&nbsp;<select ' + 
            'id="compound-het-state" onchange="sOpFuncH.careControls();"' + 
            ((this.mLabels.length == 0)? " disabled":"") + '>');
        list_stat_rep.push(
            '<option value=""' + ((this.mLabels.length == 0)? " selected":"") + '>' +
            '-current-</option>');
        for (idx = 0; idx < this.mLabels.length; idx++) {
            list_stat_rep.push('<option value="' + this.mLabels[idx] + '" ' +
                ((this.mLabels[idx] == v_state)? " selected ": "") +
                '>' + this.mLabels[idx] + '</option>');
        }
        list_stat_rep.push('</select></div></div>');
        list_stat_rep.push('<div id="comp-rq-request">');
        for (idx = 0; idx < v_request.length; idx++) {
            list_stat_rep.push('<div class="comp-rq-item-block"' +
                ' id="comp-rq-line' + idx + '"' +
                ' onclick="sFunc_CompoundRequest.setCur(' + idx + ')">');
            list_stat_rep.push('<div class="wrapped">' +
                '<input type="number" min="0"' +
                ' title = "minimal count of events" class="w50"' +
                ' id="comp-rq-item--' + idx + '"' +
                ' onchange="sOpFuncH.careControls()"' + 
                ' value="' + v_request[idx][0] + '"/></div>');
            sZygSuportH.renderScenario(v_request[idx][1], 
                this.mFamily, "sFunc_CompoundRequest", "__" + idx, list_stat_rep);
            list_stat_rep.push('</div>');
        }
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div class="func-parameters">');
        list_stat_rep.push('<div class="wrapped"><button ' + 
            ((v_request.length < 5)? "": "disabled ") + 
            'onclick="sFunc_CompoundRequest.addLine()">Add</button></div>');
        list_stat_rep.push('<div class="wrapped"><button ' + 
            ((v_request.length > 1)? "": "disabled ") + 
            'onclick="sFunc_CompoundRequest.delLine()">Remove</button></div>');
        sZygSuportH.renderResetGroup("sFunc_CompoundRequest", list_stat_rep);
        list_stat_rep.push('</div>');
        return list_stat_rep.join('\n');
    },   

    checkFControls: function() {
        v_request = [];
        for (idx = 0; idx < sOpFuncH.getCurFState()[2].length; idx++) {
            v_request.push([
                parseInt(document.getElementById("comp-rq-item--" + idx).value),
                sZygSuportH.scanScenario(this.mFamily, "__" + idx)]);
        }
        if (this.mPrevCurLine != null) {
            line_el = document.getElementById("comp-rq-line" + this.mPrevCurLine);
            if (line_el) {
                line_el.className = line_el.className.split(' ')[0];
            }
        }
        this.mCurLine = Math.min(this.mCurLine, v_request.length - 1);
        this.mPrevCurLine = this.mCurLine;
        line_el = document.getElementById("comp-rq-line" + this.mPrevCurLine);
        line_el.className = line_el.className.split(' ')[0] + ' cur';
        sZygSuportH.updateResetGroup(
            v_request[this.mCurLine][1], this.mResetVariants);

        return [
            this.normApproxMode(
                document.getElementById('compound-het-approx').value),
            this.normVState(
                document.getElementById('compound-het-state').value),
            v_request];
    },
    
    setCur: function(line_no) {
        this.mCurLine = line_no;
        sOpFuncH.careControls();
    },
    
    addLine: function() {
        var f_state = sOpFuncH.getCurFState();
        var v_request = f_state[2];
        this.mCurLine = v_request.length;
        v_request.push([1, {}]);
        sOpFuncH.resetFState(f_state, true);
    },
    
    delLine: function() {
        var f_state = sOpFuncH.getCurFState();
        var v_request = f_state[2];
        v_request.splice(this.mCurLine, 1);
        if (this.mCurLine >= v_request.length)
            this.mCurLine = v_request.length - 1;
        sOpFuncH.resetFState(f_state, true);
    },
    
    resetScenario: function() {
        cur_idx = document.getElementById
            ("inheritance-z-fam-reset-select").selectedIndex;
        if (cur_idx > 0) {
            var f_state = sOpFuncH.getCurFState();
            var v_request = f_state[2];
            v_request[this.mCurLine][1] = this.mResetVariants[cur_idx - 1];
            sOpFuncH.resetFState(f_state, true);
        }
    }
}

/**************************************/
var sFunc_Region = {
    normLocus: function(locus) {
        if (!locus)
            return null;
        return locus;
    },
    
    setupFState: function(func_unit_stat) {
        return [this.normLocus(func_unit_stat["locus"])];
    },
    
    updateFState: function(cond_data) {
        var locus = this.normLocus(cond_data[4]["locus"]);
        document.getElementById('region-locus').value = (locus)? locus:'';
        return [locus];
    },
    
    parseFState: function(info) {
        return [this.normLocus(info["locus"])];
    },
    
    getVariants: function() {
        return ["True"];
    },
    
    makeFParams: function(state) {
        return {"locus": state[0]};
   },
    
    checkBad: function(state) {
        return !state[0];
    },
    
    checkError: function(state) {
        var locus = state[0];
        if (locus) {
            return " ";
        }
        return "Locus is empty";
    },
     
    onReset: function(state) {
        var locus = state[0];
        if (document.getElementById('region-locus').value.trim() != locus)
            document.getElementById('region-locus').value = locus;
        return false;
    },

    renderIt: function(state) {
        var locus = state[0];
        var list_stat_rep = ['<div class="func-parameters">',
            '<div><span class="comment">Locus:</span>&nbsp;<input ' + 
            'id="region-locus" oninput="sOpFuncH.careControls();" ' +
            ((locus)? 'value="' + escapeText(locus) + '"' : '') + 
            '>'];
        list_stat_rep.push('</div></div>');
        return list_stat_rep.join('\n');
    },   

    checkFControls: function() {
        return [this.normLocus(
            document.getElementById('region-locus').value.trim())];
    }        
}
    
