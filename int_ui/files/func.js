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

    init: function() {
        this.mFDict = {
            "inheritance-z": sFunc_InheritanceZ
        };
    },
    
    notSupported: function(unit_stat) {
        if (unit_stat["kind"] != "func")
            return false;
        return (!this.mFDict[unit_stat["sub-kind"]]);
    },
    
    getCurParams: function() {
        return this.mCurFuncH.getCurParams();
    },
    
    setup: function(func_unit_stat) {
        this.mUnitStat = func_unit_stat;
        this.mCurFuncH = this.mFDict[func_unit_stat["sub-kind"]];
        this.mCurFuncH.setup(func_unit_stat);
        this.mRuntimeErr = null;
        this.renderParams();
        this.reloadStat();
    },
    
    updateCondition: function(cond_data) {
        needs_reload = false;
        if (cond_data != null) {
            needs_reload = this.mCurFuncH.updateCondition(cond_data);
        }
        this.renderParams();
        if (needs_reload)
            this.reloadStat(cond_data);
    },
    
    reloadStat: function() {
        sOpEnumH.waitForUpdate();
        if (this.mTimeH == null) {
            this.mTimeH = setInterval(function(){sOpFuncH._reloadStat();}, 2);
        }
    },

    stop: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
    },
    
    _reloadStat: function(cond_data) {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        ajaxCall("statfunc", sUnitsH.getRqArgs() + "&unit=" + this.mUnitStat["name"] + 
            "&param=" + encodeURIComponent(JSON.stringify(this.mCurFuncH.getCurParams())),
            function(info){sOpFuncH._setupStat(info, cond_data);})
    },
    
    _setupStat: function(info, cond_data) {
        if (this.mUnitStat == null)
            return;
        this.mRuntimeErr = info["err"];
        if (cond_data == null)
            sel_variants = sOpEnumH.getSelected();
        if (this.mCurFuncH.expectedStat(info, cond_data)) {
            sOpEnumH._setupVariants(info["variants"]);
            if ( cond_data != undefined) 
                sOpEnumH._updateState(cond_data[2], cond_data[3]);
            else
                sOpEnumH._updateState(null, sel_variants);
            sOpEnumH.checkControls();
        }
    },
    
    careControls: function(in_check) {
        if (this.mCurFuncH.checkControls(in_check))
            this.reloadStat();
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
    mPGroup: undefined,
    
    setup: function(func_unit_stat) {
        this.mAffectedGroup = func_unit_stat["affected"];
        this.mFamily = func_unit_stat["family"];
        this.mPGroup = undefined;
    },
    
    updateCondition: function(cond_data) {
        if (cond_data != null) {
            p_group = cond_data[4]["problem_group"];
            this.mPGroup = (p_group)? p_group : undefined;
            return true;
        }
        return false;
    },
    
    expectedStat: function(info, cond_data) {
        var p_group = info["problem_group"];
        if (!p_group)
            p_group = undefined;
        if (p_group && JSON.stringify(p_group) == JSON.stringify(this.mAffectedGroup))
            p_group = undefined;
        return (JSON.stringify(p_group) == JSON.stringify(this.mPGroup));
    },
    
    checkControls: function(in_check) {
        var p_group = [];
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            if (document.getElementById("inheritance-z-fam-m__" + idx).checked)
                p_group.push(this.mFamily[idx]);
        }
        if (p_group.join('|') == this.mAffectedGroup.join('|'))
            p_group = undefined;
        document.getElementById("inheritance-z-fam-reset").disabled = (!p_group);
        if (JSON.stringify(p_group) == JSON.stringify(this.mPGroup))
            return false;
        this.mPGroup = p_group;
        return true;
    },
 
    getCurParams: function() {
        if (this.mPGroup)
            return {"problem_group": this.mPGroup};
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
        var p_group = (this.mPGroup == null)? this.mAffectedGroup : this.mPGroup;
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
        list_stat_rep.push('<button id="inheritance-z-fam-reset" ' +
            ' title="Reset affected group" ' +
            'onclick="sFunc_InheritanceZ.resetGrp()">Reset</button>&emsp;');
        return list_stat_rep.join('\n');
    },   

    resetGrp: function() {
        this.mPGroup = undefined;
        sOpFuncH.renderParams();
        sOpFuncH.reloadStat();
    }
}
    
/**************************************/
