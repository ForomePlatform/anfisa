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
            "comp-hets": sFunc_CompoundHet
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
        if (p_group && JSON.stringify(p_group) == JSON.stringify(this.mAffectedGroup))
            p_group = null;
        return (JSON.stringify(p_group) == JSON.stringify(this.mCurPGroup));
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
        var list_stat_rep = ['<div class="comment">Problem group:</div>'];
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
        list_stat_rep.push('<button id="inheritance-z-fam-reset" ' +
            ' title="Reset affected group" ' +
            'onclick="sFunc_InheritanceZ.resetGrp()">Reset</button>&emsp;');
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
        if (JSON.stringify(p_group) == JSON.stringify(this.mCurPGroup))
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
            out_rep.push('<div class="c-inheritance-z-fam-member">' + sample_id + 
                '&nbsp<select id="' + check_id + 
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

    checkScenario: function(family, ctrl_name, scope_option) {
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
    
    sameScenario: function(sc1, sc2) {
        return (JSON.stringify(sc1) == JSON.stringify(sc2));
    },
    
    evalResetVariants: function(family, affected_group) {
        return [{}, 
            this.buildScenario(family, affected_group, "2", "0-1"),
            this.buildScenario(family, affected_group, "1-2", "0"),
            this.buildScenario(family, affected_group, "0", "1-2")];
    },
    
    renderResetGroup: function(ctrl_name, out_rep) {
        out_rep.push('<div><span class="comment">Reset</span>&nbsp;' +
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
            if (this.sameScenario(scenario, reset_variants[idx])) {
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
        return sZygSuportH.sameScenario(info["scenario"], this.mCurScenario);
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
        var list_stat_rep = ['<div class="comment">Scenario:</div>'];
        sZygSuportH.renderScenario(this.mCurScenario, 
            this.mFamily, "sFunc_CustomInheritanceZ", "", list_stat_rep);
        list_stat_rep.push('</div>');
        sZygSuportH.renderResetGroup("sFunc_CustomInheritanceZ", list_stat_rep);
        return list_stat_rep.join('\n');
    },   

    checkControls: function(in_check) {
        var p_scenario = sZygSuportH.checkScenario(
            this.mFamily, "sFunc_CustomInheritanceZ", "");
        sZygSuportH.updateResetGroup(p_scenario, this.mResetVariants);
        if (sZygSuportH.sameScenario(p_scenario, this.mCurScenario))
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
        var list_stat_rep = [
            '<div><span class="comment">Approx:</span>&nbsp<select ' + 
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
            '<div><span class="comment">State:</span>&nbsp<select ' + 
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
        list_stat_rep.push('<div></div>');
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
