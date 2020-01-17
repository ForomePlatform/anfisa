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
/* Filtering base support: units, stats, etc.
 * Used in all main regimes: 
 * WS/XL-Filter/XL-Tree
/**************************************/
var sOpNumH = {
    mInfo: null,
    mInputMin: null,
    mInputMax: null,
    mSpanSigns: null,
    mUpdateCondStr: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
        this.mSpanSigns = [document.getElementById("cond-min-sign"),
            document.getElementById("cond-max-sign")];
    },
    
    getCondType: function() {
        return "numeric";
    },

    suspend: function() {
        this.mInfo = null;
        this.careControls();
    },
    
    updateUnit: function(unit_stat) {
        this.mUpdateCondStr = null;
        this.mInfo = {
            cur_bounds: [null, true, null, true],
            unit_type:  unit_stat["sub-kind"],
            val_min:    unit_stat["min"],
            val_max:    unit_stat["max"],
            count:      unit_stat["count"]}
            
        if (this.mInfo.val_min != null) {
            document.getElementById("cond-min").innerHTML = 
                normFloatLongTail(this.mInfo.val_min);
            document.getElementById("cond-max").innerHTML = 
                normFloatLongTail(this.mInfo.val_max, true);
            sign_val = (this.mInfo.val_min == this.mInfo.val_max)? "=": "&le";
        } else {
            document.getElementById("cond-min").innerHTML = "?";
            document.getElementById("cond-max").innerHTML = "?";
            sign_val = "?"
        }
        this.mInputMin.value = "";
        this.mInputMax.value = "";
        this.mSpanSigns[0].innerHTML = sign_val;
        this.mSpanSigns[0].className = "num-sign-disabled";
        this.mSpanSigns[1].innerHTML =sign_val;
        this.mSpanSigns[1].className = "num-sign-disabled";
    },

    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        this.mInfo.cur_bounds   = cond[2].slice();
        this.mInputMin.value = (this.mInfo.cur_bounds[0] != null)?
            this.mInfo.cur_bounds[0] : "";
        this.mInputMax.value = (this.mInfo.cur_bounds[2] != null)?
            this.mInfo.cur_bounds[2] : "";
    },

    switchSign: function(idx) {
        if (this.mSpanSigns[idx].className == "num-sign-disabled")
            return;
        this.mInfo.cur_bounds[1 + 2 * idx] = 
            !this.mInfo.cur_bounds[1 + 2 * idx];
        this.mSpanSigns[idx].innerHTML = 
            this.mInfo.cur_bounds[1 + 2 * idx]? "&le;" : "&lt;";
        this.checkControls();
    },
    
    careControls: function() {
        document.getElementById("cur-cond-numeric").style.display = 
            (this.mInfo == null)? "none":"block";
    },

    checkControls: function(opt) {
        if (this.mInfo == null) 
            return;
        var err_msg = null;
        if (this.mInputMin.value.trim() == "") {
            this.mInfo.cur_bounds[0] = null;
            this.mInputMin.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMin.value)
            this.mInputMin.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                err_msg = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[0] = val;
            }
        }
        if (this.mInputMax.value.trim() == "") {
            this.mInfo.cur_bounds[2] = null;
            this.mInputMax.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value)
            this.mInputMax.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                err_msg = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[2] = val;
            }
        }
        
        if (this.mInfo.cur_bounds[0] != null && err_msg == null &&
                this.mInfo.cur_bounds[0] == this.mInfo.cur_bounds[2] &&
                (this.mInfo.cur_bounds[1] | this.mInfo.cur_bounds[3])) {
            err_msg = "Out of choice: strict bounds";
        }

        this.mSpanSigns[0].innerHTML = this.mInfo.cur_bounds[1]? "&le;" : "&lt;";
        this.mSpanSigns[1].innerHTML = this.mInfo.cur_bounds[3]? "&le;" : "&lt;";
        this.mSpanSigns[0].className = (this.mInfo.cur_bounds[0] == null)?
            "num-sign-disabled" : "num-sign";
        this.mSpanSigns[1].className = (this.mInfo.cur_bounds[2] == null)?
            "num-sign-disabled" : "num-sign";        
        
        condition_data = null;
        if (err_msg == null) {
            condition_data = [this.mInfo.cur_bounds];
            if (this.mInfo.cur_bounds[0] == null && 
                    this.mInfo.cur_bounds[2] == null)
                err_msg = "";
            if (this.mInfo.val_min != null) {
                if (this.mInfo.cur_bounds[0] != null) {
                    if (this.mInfo.cur_bounds[0] > this.mInfo.val_max)
                        err_msg = "Lower bound is above maximum value";
                    if (this.mInfo.cur_bounds[0] < this.mInfo.val_min) 
                        err_msg = "Lower bound is below minimal value";
                }
                if (this.mInfo.cur_bounds[2] != null) {
                    if (this.mInfo.cur_bounds[2] < this.mInfo.val_min) 
                        err_msg = "Upper bound is below minimum value";
                    if (this.mInfo.cur_bounds[2] > this.mInfo.val_max)
                        err_msg = "Upper bound is above maximal value";
                }
            } else {
                err_msg = "Out of choice"
            }
            if (err_msg && this.mUpdateCondStr == null)
                condition_data = null;
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[2] != null && 
                    this.mInfo.cur_bounds[0] > this.mInfo.cur_bounds[2]) {
                err_msg = "Bounds are mixed up";
                condition_data = null;
            }
        }
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }
        sOpCondH.formCondition(condition_data, err_msg, false);
        this.careControls();
    }
};

/**************************************/
var sOpEnumH = {
    mVariants: null,
    mOperationMode: null,
    mDivVarList: null,
    mFuncCtrl: null,
    mStatusMode: null,
    mUpdateCondStr: null,
    mDivFuncParam: null,

    init: function() {
        this.mDivVarList = document.getElementById("op-enum-list");
        this.mDivFuncParam = document.getElementById("cur-cond-func-param");
    },
    
    getCondType: function() {
        return (this.mFuncCtrl != null)? "func" : "enum";
    },
    
    renderFuncDiv: function(content) {
        this.mDivFuncParam.innerHTML = content;
    },
    
    suspend: function() {
        if (this.mFuncCtrl)
            this.mFuncCtrl.suspend()
        this.mVariants = null;
        this.mOperationMode = null;
        this.mFuncCtrl = null;
        this.careControls();
    },
    
    reprVariant: function(var_name, var_count, var_idx, is_checked) {
        var check_id = 'elcheck--' + var_idx; 
        return '<div class="enum-val' + 
            ((var_count==0)? " zero":"") +'">' +
            '<input id="' + check_id + '" type="checkbox" ' + 
            ((is_checked)? 'checked ':'') + 
            'onchange="sOpEnumH.checkControls();"/><label for="' +
            check_id + '">&emsp;' + var_name + 
            '<span class="count">(' + var_count + ')</span></div>';
    },
    
    updateUnit: function(unit_stat) {
        if (this.mFuncCtrl)
            this.mFuncCtrl.suspend()
        this.mUpdateCondStr = null;
        this.mOperationMode = 0;
        this.mStatusMode = (unit_stat["sub-kind"] == "status");
        if (unit_stat["kind"] == "func") {
            this.mFuncCtrl = selectFuncCtrl(unit_stat);
            this.mFuncCtrl.setup(unit_stat);
        } else {
            this.mFuncCtrl = null;
            this._setupVariants(unit_stat["variants"]);
        }
        this.mDivFuncParam.style.display = 
            (this.mFuncCtrl == null)? "none":"";
    },

    _setupVariants: function(variants) {
        this.mVariants = variants;
        if (this.mVariants == null)
            this.mVariants = [];
        var list_val_rep = [];
        has_zero = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            var_count = this.mVariants[j][1];
            if (unit_stat["detailed"] && var_count > 0)
                var_count = var_count + "/" + this.mVariants[j][2];
            has_zero |= (var_count == 0);
            list_val_rep.push(this.reprVariant(var_name, var_count, j));
        }
        this.mDivVarList.innerHTML = list_val_rep.join('\n');
        this.mDivVarList.className = "";
        
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero)? "block":"none";            
        this.careEnumZeros(false);
    },
    
    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        if (this.mFuncCtrl != null) {
            this.mFuncCtrl.updateCondition(cond);
        } else {
            this._updateState(cond[2], cond[3]);
        }
    },
    
    _updateState: function(op_mode, var_list) {
        if (this.mOperationMode != null)
            this.mOperationMode = ["OR", "AND", "NOT"].indexOf(op_mode);
        needs_zeros = false;
        if (var_list) {
            present_vars = {};
            for (j = 0; j < this.mVariants.length; j++) {
                var_name = this.mVariants[j][0];
                if (var_list.indexOf(var_name) < 0)
                    continue
                present_vars[var_name] = true;
                needs_zeros |= (this.mVariants[j][1] == 0);
                document.getElementById("elcheck--" + j).checked = true;
            }
            lost_vars = [];
            for (j=0; j < var_list.length; j++)  {
                var_name = var_list[j];
                if (!present_vars[var_name])
                    lost_vars.push(var_name);
            }
            if(lost_vars.length > 0) {
                list_val_rep = [];
                lost_vars.sort();
                for (j=0; j < lost_vars.length; j++)  {
                    var_name = lost_vars[j];
                    this.mDivVarList.innerHTML += this.reprVariant(
                        var_name, 0, this.mVariants.length, true);
                    this.mVariants.push([var_name, 0, 0]);
                }
                needs_zeros = true;
            }
        }
        this.careEnumZeros(needs_zeros);
        this.checkControls();
    },
    
    careControls: function(in_check) {
        if (this.mFuncCtrl != null)
            this.mFuncCtrl.careControls(in_check);
        document.getElementById("cur-cond-enum").style.display = 
            (this.mVariants == null)? "none":"block";
        for (idx = 1; idx < 3; idx++) {
            vmode = ["or", "and", "not"][idx];
            document.getElementById("cond-mode-" + vmode + "-span").
                style.visibility = (this.mOperationMode == null ||
                    (this.mStatusMode && idx != 2))? "hidden":"visible";
            document.getElementById("cond-mode-" + vmode).checked =
                (idx == this.mOperationMode);
        }
    },

    careEnumZeros: function(opt) {
        var check_enum_z = document.getElementById("cur-enum-zeros");
        if (opt == undefined) {
            show_zeros = check_enum_z.checked;
        } else {
            show_zeros = opt;
            check_enum_z.checked = show_zeros;
        }
        this.mDivVarList.className = (show_zeros)? "":"no-zeros";
    },
    
    getSelected: function() {
        var sel_names = [];
        if (this.mVariants != null) {
            for (j=0; j < this.mVariants.length; j++) {
                if (document.getElementById("elcheck--" + j).checked)
                    sel_names.push(this.mVariants[j][0]);
            }
        }
        return sel_names;
    },
    
    checkControls: function(opt) {
        if (this.mVariants == null) 
            return;
        this.careControls(true);
        var err_msg = null;
        if (opt != undefined && this.mOperationMode != null) {
            if (this.mOperationMode == opt)
                this.mOperationMode = 0;
            else
                this.mOperationMode = opt;
        }
        sel_names = this.getSelected();
        op_mode = "";
        if (this.mOperationMode != null)
            op_mode = ["", "AND", "NOT"][this.mOperationMode];
        if (!op_mode)
            op_mode = "";
        
        condition_data = null;
        if (sel_names.length > 0) {
            condition_data = [op_mode, sel_names];
            if (sel_names.length == 1)
                err_msg = "1 variant selected";
            else
                err_msg = sel_names.length + " variants selected";
        } else
            err_msg = " Out of choice"
        if (this.mFuncCtrl != null) {
            if (condition_data)
                condition_data.push(this.mFuncCtrl.getCurParams());
            err_msg = this.mFuncCtrl.checkError(condition_data, err_msg);
        }
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }

        sOpCondH.formCondition(condition_data, err_msg, true);
        this.careControls();
    },
    
    waitForUpdate: function(unit_name) {
        this.mDivVarList.className = "wait";
    }
};

/*************************************/
/*************************************/
function fillStatList(items, unit_map, list_stat_rep, 
        unit_names_to_load, expand_mode) {
    var group_title = false;
    for (idx = 0; idx < items.length; idx++) {
        unit_stat = items[idx];
        unit_name   = unit_stat["name"];
        unit_map[unit_name] = idx;
        if (group_title != unit_stat["vgroup"] || unit_stat["vgroup"] == null) {
            if (group_title != false) {
                list_stat_rep.push('</div>');
            }
            group_title = unit_stat["vgroup"];
            list_stat_rep.push('<div class="stat-group">');
            if (group_title != null) {
                list_stat_rep.push('<div class="stat-group-title">' + 
                    group_title);
                if (unit_name == "Rules") {
                    list_stat_rep.push(
                        '<span id="flt-go-dtree" ' +
                            'title="Configure decision trees as rules..." ' +
                        'onclick="goToPage(\'DTREE\');"">&#x2699;</span>')
                }
                list_stat_rep.push('</div>');
            }
        }
        func_decor = (unit_stat["kind"] == "func" || 
            unit_stat["sub-kind"] == "func")? "(...)":"";
        list_stat_rep.push('<div id="stat--' + unit_name + '" class="stat-unit" ');
        if (unit_stat["tooltip"]) 
            list_stat_rep.push('title="' + escapeText(unit_stat["tooltip"]) + '" ');

        list_stat_rep.push('onclick="sUnitsH.selectUnit(\'' + unit_name + '\');">');
        list_stat_rep.push('<div class="wide"><span class="stat-unit-name">' +
            unit_name + func_decor + '</span>');
        if (unit_stat["title"]) 
            list_stat_rep.push('<span class="stat-unit-title">' + 
                unit_stat["title"] + '</span>');
        list_stat_rep.push('</div>')
        list_stat_rep.push('<div id="stat-data--' + unit_name + '" class="stat-unit-data">');
        if (unit_stat["incomplete"]) {
            unit_names_to_load.push(unit_name);
            list_stat_rep.push('<div class="comment">Loading data...</div>');
        } else {
            switch (unit_stat["kind"]) {
                case "numeric":
                    fillStatRepNum(unit_stat, list_stat_rep);
                    break;
                case "enum":
                    fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
                    break;
                case "func":
                    break;
            }
        }
        list_stat_rep.push('</div></div>')
    }
    if (group_title != false) {
        list_stat_rep.push('</div>')
    }
}

function refillUnitStat(unit_stat, expand_mode) {
    div_el = document.getElementById("stat-data--" + unit_stat["name"]);
    list_stat_rep = [];
    if (unit_stat["kind"] == "func") 
        sOpFuncH.setup(unit_stat, list_stat_rep);
    else {
        if (unit_stat["kind"] == "numeric") 
            fillStatRepNum(unit_stat, list_stat_rep);
        else
            fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
    }
    div_el.innerHTML = list_stat_rep.join('\n');
    div_el.className = "";
}

function renderEnumUnitStat(unit_stat, expand_mode) {
    list_stat_rep = [];
    fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
    div_el = document.getElementById("stat-data--" + unit_stat["name"]);
    div_el.innerHTML = list_stat_rep.join('\n');
}

function topUnitStat(unit_name) {
    return document.getElementById(
        "stat--" + unit_name).getBoundingClientRect().top;
}

/*************************************/
function fillStatRepNum(unit_stat, list_stat_rep) {
    val_min   = unit_stat["min"];
    val_max   = unit_stat["max"];
    count     = unit_stat["count"];
    if (count == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
    } else {
        if (val_min == val_max) {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                '</span>');
        } else {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                ' &le;&nbsp;...&nbsp;&le; ' + normFloatLongTail(val_max, true) + ' </span>');
        }
        list_stat_rep.push(': ' + reportStatCount([null, count], unit_stat));
    }
}

/*************************************/
function fillStatRepEnum(unit_stat, list_stat_rep, expand_mode) {
    var_list = unit_stat["variants"];
    list_count = 0;
    if (var_list) {
        for (j = 0; j < var_list.length; j++) {
            if (var_list[j][1] > 0)
                list_count++;
        }
    }
    if (list_count == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
        return;
    }
    needs_expand = list_count > 6 && expand_mode;
    if (expand_mode == 2) 
        view_count = list_count
    else
        view_count = (list_count > 6)? 3: list_count; 
        
    if (list_count > 6 && expand_mode) {
        list_stat_rep.push('<div onclick="renderEnum(\'' + 
            unit_stat["name"] +  '\',' + (3 - expand_mode) + 
            ');" class="enum-exp">' + 
            ((expand_mode==1)?'+':'-') + '</div>');
    }
    list_stat_rep.push('<ul>');
    for (j = 0; j < var_list.length && view_count > 0; j++) {
        var_name = var_list[j][0];
        var_count = var_list[j][1];
        if (var_count == 0)
            continue;
        view_count -= 1;
        list_count--;
        list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
            reportStatCount(var_list[j], unit_stat) + '</li>');
    }
    list_stat_rep.push('</ul>');
    if (list_count > 0) {
        list_stat_rep.push('<p class="stat-comment">...and ' + 
            list_count + ' variants more...</p>');
    }
}

function reportStatCount(count_info, unit_stat) {
    if (unit_stat["detailed"]) {
        cnt_rep = count_info[1] + '(' + count_info[2] + ')';
        nm = "transcript";
    } else {
        cnt_rep = count_info[1];
        nm = "variant";
    }
    return '<span class="stat-count">' + cnt_rep + ' ' + nm +  
        ((count_info[1]>1)? 's':'') + '</span>';
}

/*************************************/
/* Create WS                         */
/*************************************/
var sCreateWsH = {
    mStage: null,
    mDSNames: null,
    mSpanModTitle: null,
    mInputModName: null,
    mDivModProblems: null,
    mDivModStatus: null,
    mButtonModStart: null,
    mButtonModCancel: null,
    mTaskId: null,
    mTimeH: null,
    
    init: function() {
        this.mSpanModTitle = document.getElementById("create-ws-title");
        this.mInputModName = document.getElementById("create-ws-name");
        this.mDivModProblems = document.getElementById("create-ws-problems");
        this.mDivModStatus = document.getElementById("create-ws-status");
        this.mButtonModStart = document.getElementById("create-ws-start");
        this.mButtonModCancel = document.getElementById("create-ws-cancel");
    },
    
    show: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDSNames = null;
        this.mTaskId = null;
        
        var info = sUnitsH.prepareWsCreate();
        if (info == null) 
            return;
        
        this.mSpanModTitle.innerHTML = 'Create workspace for ' +
            info[0] + ' of ' + info[1];
        var err_msg = "";
        if (info[0] >= 9000)
            err_msg = "Too many variants, try to reduce";
        if (info[0] < 1)
            err_msg = "Empty set";
        this.mDivModProblems.innerHTML = err_msg;
        if (err_msg) {
            this.mStage = "BAD";
            this.checkControls();
            sViewH.modalOn(document.getElementById("create-ws-back"));
            return;
        }
        this.mStage = "NAMES";
        ajaxCall("dirinfo", "", function(info) {
            sCreateWsH._setupName(info);})
    },
    
    _nameReserved: function(dsname) {
        return this.mDSNames.indexOf(dsname) >= 0;
    },
    
    _setupName: function(dirinfo) {
        this.mDSNames = dirinfo["reserved"];
        var no = 1;
        var own_name = sDSName.match(/\_(.*)$/)[1];
        var ws_name;
        while (true) {
            ws_name = "ws" + no + '_' + own_name;
            if (!this._nameReserved(ws_name))
                break;
            no += 1;
        }
        this.mInputModName.value = ws_name;
        this.mStage = "READY";
        this.checkControls();
        sViewH.modalOn(document.getElementById("create-ws-back"));
    },
    
    checkControls: function() {
        if (this.mStage == "BAD")
            this.mInputModName.value = "";
        this.mInputModName.disabled = (this.mStage != "READY");
        err_msg = "";
        if (this.mStage == "READY") {
            if (this._nameReserved(this.mInputModName.value)) 
                err_msg = "Name is reserved, try another one";
            this.mDivModProblems.innerHTML = err_msg;
        }
        this.mButtonModStart.disabled = (this.mStage != "READY" || err_msg);
        if (this.mStage == "BAD" || this.mStage == "READY") {
            this.mDivModProblems.style.display = "block";
            this.mDivModStatus.style.display = "none";
            this.mDivModStatus.innerHTML = "";
        } else {
            this.mDivModProblems.style.display = "none";
            this.mDivModStatus.style.display = "block";
        }
        this.mButtonModCancel.disabled = (this.mStage == "WAIT");
    },
    
    startIt: function() {
        if (this.mStage != "READY")
            return;
         this.checkControls();
        if (this.mButtonModStart.disabled)
            return;
        sViewH.blockModal(true);
        this.mStage = "WAIT";
        ajaxCall("ds2ws", sUnitsH.getWsCreateArgs() +
            "&ws=" + encodeURIComponent(this.mInputModName.value),
            function(info) {sCreateWsH._setupTask(info);})
    },
    
    _setupTask: function(info) {
        this.mTaskId = info["task_id"];
        this.checkTask();
    },
    
    checkTask: function() {
        if (this.mTaskId == null)
            return;
        ajaxCall("job_status", "task=" + this.mTaskId,
            function(info) {
                sCreateWsH._checkTask(info);})
    },
    
    _checkTask: function(info) {
        if (info != null && info[0] == false) {
            this.mDivModStatus.innerHTML = info[1];
            if (this.mTimeH == null)
                this.mTimeH = setInterval(function() {sCreateWsH.checkTask()}, 3000);
            this.checkControls();
            return;
        }
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mStage = "DONE";
        sViewH.blockModal(false);
        this.checkControls();
        if (info == null) {
            this.mDivModStatus.innerHTML = "Task information lost";
        } else {
            if (info[0] == null) {
                this.mDivModStatus.innerHTML = info[1];
            } else {
                target_ref = (sWsPubURL != "ws")? '': (' target="' + 
                    sCommonTitle + ':' + info[0]["ws"] + '"'); 
                this.mDivModStatus.innerHTML = 'Done: <a href="' + sWsPubURL + 
                    '?ds=' +  info[0]["ws"] + '"' + target_ref + '>Open it</a>';
            }
        }
    }
};

function wsCreate() {
    sCreateWsH.show();
}

function startWsCreate() {
    sCreateWsH.startIt();
}

