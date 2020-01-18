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
            "comp-hets": sFunc_CompoundHet
        };
    },
    
    notSupported: function(unit_stat) {
        if (unit_stat["kind"] != "func")
            return false;
        return (!this.mFDict[unit_stat["sub-kind"]]);
    },
    
    stop: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
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
        this.renderParams();
        this.reloadStat();
    },
    
    getCurParams: function() {
        return this.mCurFuncH.getCurParams();
    },
    
    updateCondition: function(cond_data) {
        this.mOpMode = cond_data[2];
        this.mOpVariants = cond_data[3];
        this.mCurFuncH.updateCondition(cond_data);
    },
    
    reloadStat: function(scan_variants) {
        if (scan_variants)
            this.mOpVariants = sOpEnumH.getSelected();
        sOpEnumH.waitForUpdate();
        if (this.mTimeH == null) {
            this.mTimeH = setInterval(function(){sOpFuncH._reloadStat();}, 2);
        }
    },

    _reloadStat: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
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
 
    checkError: function(condition_data, err_msg) {
        if (this.mRuntimeErr)
            return this.mRuntimeErr;
        if (err_msg) 
            return err_msg;
        return this.mCurFuncH.checkError(condition_data);
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
    
    setup: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mCurPGroup = null;
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
    
    checkError: function(condition_data) {
        var p_group = condition_data[4]["problem-group"];
        if (!p_group)
            p_group = this.mAffectedGroup;
        if (p_group.length == 0) 
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
        sOpFuncH.reloadStat(true);
    },
 
    resetGrp: function() {
        this.mCurPGroup = null;
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat(true);
    }
}
    
/**************************************/
var sFunc_CompoundHet = {
    mLabels: null,
    mApproxModes: null,
    mApproxTitles: null,
    mCurApprox: null,
    mCurState: undefined,
    
    setup: function(func_unit_stat) {
        this.mLabels = func_unit_stat["labels"];
        this.mApproxModes = [];
        this.mApproxTitles = [];
        for (idx = 0; idx< func_unit_stat["approx-modes"].length; idx++) {
            this.mApproxModes.push(func_unit_stat["approx-modes"][idx][0]);
            this.mApproxTitles.push(func_unit_stat["approx-modes"][idx][1]);
        }
        this.mCurApprox = null;
        this.mCurState = null;
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
    
    checkError: function(cond_data) {        
        v_approx = cond_data[4]["approx"];
        v_state = cond_data[4]["state"];
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
            sOpFuncH.reloadStat(true);
        }
    }        
}
    
/**************************************/
