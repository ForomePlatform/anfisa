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

var sFuncInheritanceZ = {
    mUnitStat: null,
    mUnitName: null,
    mFamily: null,
    mAffectedGroup: null,
    mPrevData: null,
    mPGroup: null,
    mRuntimeErr: null,
    mTimeH: null,
    
    setup: function(func_unit_stat) {
        this.mUnitStat = func_unit_stat;
        this.mUnitName = func_unit_stat["name"];
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mPrevData = null;
        this.mPGroup = null;
        this.mRuntimeErr = null;
        this.renderParams();
        this.reloadStat();
    },
    
    suspend: function(){
        this.mUnitStat = null;
        this.mUnitName = null;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
    },
    
    updateCondition: function(cond_data) {
        this.mPrevData = cond_data;
        needs_reload = false;
        if (cond_data != null) {
            p_group = cond_data[4]["problem_group"];
            this.mPGroup = (p_group == undefined)? null: p_group;
            needs_reload = true;
        }
        this.renderParams();
        if (needs_reload)
            this.reloadStat(cond_data);
    },
    
    reloadStat: function() {
        sOpEnumH.waitForUpdate();
        if (this.mTimeH == null) {
            this.mTimeH = setInterval(function(){sFuncInheritanceZ._reloadStat();}, 2);
        }
    },
    
    _reloadStat: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        ajaxCall("statfunc", sUnitsH.getRqArgs() + "&unit=" + this.mUnitName + 
            "&param=" + encodeURIComponent(JSON.stringify(this.getCurParams())),
            function(info){sFuncInheritanceZ._setupStat(info, this.mUnitStat);})
    },
    
    _setupStat: function(info, cond_data) {
        if (this.mUnitStat == null)
            return;
        this.mRuntimeErr = info["err"];
        var p_group = info["problem_group"];
        if (p_group == undefined || 
                JSON.stringify(p_group) == JSON.stringify(this.mAffectedGroup))
            p_group = null;
        if ( cond_data == undefined)
            sel_variants = sOpEnumH.getSelected();
        if (JSON.stringify(p_group) == JSON.stringify(this.mPGroup)) {
            sOpEnumH._setupVariants(info["variants"]);
            if ( cond_data != undefined) 
                sOpEnumH._updateState(cond_data[2], cond_data[3]);
            else
                sOpEnumH._updateState(null, sel_variants);
            sOpEnumH.checkControls();
        }
    },
    
    careControls: function(in_check) {
        var p_group = [];
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            if (document.getElementById("inheritance-z-fam-m__" + idx).checked)
                p_group.push(this.mFamily[idx]);
        }
        if (p_group.join('|') == this.mAffectedGroup.join('|'))
            p_group = null;
        document.getElementById("inheritance-z-fam-reset").disabled = (p_group == null);
        if (JSON.stringify(p_group) != JSON.stringify(this.mPGroup)) {
            this.mPGroup = p_group;
            this.reloadStat();
        }
    },
 
    getCurParams: function() {
        return (this.mPGroup == null)? {}: {"problem_group": this.mPGroup};
    },
    
    checkError: function(condition_data, err_msg) {
        if (this.mRuntimeErr)
            return this.mRuntimeErr;
        if (err_msg) 
            return err_msg;
        var p_group = condition_data[4]["problem-group"];
        if (p_group == undefined)
            p_group = this.mAffectedGroup;
        if (p_group.length == 0) 
            return "Empty problem group";
        return null;
    },
     
    renderParams: function() {
        var list_stat_rep = [];
        var p_group = (this.mPGroup == null)? this.mAffectedGroup : this.mPGroup;
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            sample_id = this.mFamily[idx];
            q_checked = (p_group.indexOf(sample_id) >= 0)? " checked":"";
            check_id = "inheritance-z-fam-m__" + idx;
            list_stat_rep.push('<div class="inheritance-z-fam-member">' + 
                '<input type="checkbox" id="' + check_id + '" ' + q_checked + 
                ' onchange="sFuncInheritanceZ.careControls();" /><label for="' +
                check_id + '">&nbsp;' + this.mFamily[idx] + '</div>');
        }
        list_stat_rep.push('</div>');
        list_stat_rep.push('<button id="inheritance-z-fam-reset" ' +
            ' title="Reset affected group" ' +
            'onclick="sFuncInheritanceZ.resetGrp()">Reset</button>&emsp;');
        sOpEnumH.renderFuncDiv(list_stat_rep.join('\n'));
    },   

    resetGrp: function() {
        this.mPGroup = null;
        this.renderParams();
        this.reloadStat();
    }
}
    
/**************************************/
sFuncCtrlDict = {
    "inheritance-z": sFuncInheritanceZ
};

function selectFuncCtrl(func_unit_stat) {
    ctrl = sFuncCtrlDict[func_unit_stat["sub-kind"]];
    return (ctrl)? ctrl : null;
}
