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
    mDivHistogram: null,
    mUpdateCondStr: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
        this.mSpanSigns = [document.getElementById("cond-min-sign"),
            document.getElementById("cond-max-sign")];
        this.mDivHistogram = document.getElementById("cur-cond-num-histogram");
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
            histogram:  unit_stat["histogram"]
        }
            
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
        this.mSpanSigns[1].innerHTML = sign_val;
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
        if (this.mInfo != null)
            this.drawHistogram();
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
                (!this.mInfo.cur_bounds[1] || !this.mInfo.cur_bounds[3])) {
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
                if (this.mUpdateCondStr == null)
                    condition_data = null;
            }
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
    },
    
    drawHistogram: function() {
        h_info = this.mInfo["histogram"];
        h_content = [];
        if (h_info) {
            if(h_info[0] == "LOG") {
                if (h_info[1] < -15 || this.mInfo.val_min == 0) {
                    val = "0";
                } else {
                    if (h_info[1] == 0)
                        val = "1";
                    else
                        val = "10<sup>" + h_info[1] + "</sup>";
                }
            } else {
                val = "" + h_info[1];
            }
            h_content.push('<span class="hist-diap">' + val + '</span>'); 
            var factor = 30. / Math.max(...h_info[3]);
            var cell_class = (h_info[0] == "LOG")? "hist-cell-log": "hist-cell";
            for (var j = 0; j < h_info[3].length; j++) {
                hh = h_info[3][j] * factor;
                h_content.push(
                    '<span class="' + cell_class + '" style="height:' + 
                        hh + 'px;"> </span>');
            }
            if(h_info[0] == "LOG") {
                if (h_info[2] == 0)
                    val = "1";
                else
                    val = "10<sup>" + h_info[2] + "</sup>";
            } else {
                val = "" + h_info[2];
            }
            h_content.push('<span class="hist-diap">' + val + '</span>'); 
        }
        this.mDivHistogram.innerHTML = h_content.join("");
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
    mArrangeBase: null,
    mArrangeDelta: null,

    init: function(arrange_base, arrange_delta) {
        this.mArrangeBase = arrange_base;
        this.mArrangeDelta = arrange_delta;
        this.mDivVarList = document.getElementById("op-enum-list");
        this.mDivFuncParam = document.getElementById("cur-cond-func-param");
        sOpFuncH.init();
    },
    
    getCondType: function() {
        return (this.mFuncCtrl != null)? "func" : "enum";
    },
    
    renderFuncDiv: function(content) {
        this.mDivFuncParam.innerHTML = content;
    },
    
    suspend: function() {
        if (this.mFuncCtrl)
            this.mFuncCtrl.stop()
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
            this.mFuncCtrl.stop()
        this.mUpdateCondStr = null;
        this.mOperationMode = 0;
        this.mStatusMode = (unit_stat["sub-kind"] == "status");
        if (unit_stat["kind"] == "func") {
            this.mFuncCtrl = sOpFuncH;
            this.mFuncCtrl.setup(unit_stat);
        } else {
            this.mFuncCtrl = null;
            this._setupVariants(unit_stat["variants"]);
        }
    },
    
    _setupVariants: function(variants, func_mode) {
        this.mVariants = variants;
        if (this.mVariants == null)
            this.mVariants = [];
        var list_val_rep = [];
        has_zero = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            var_count = this.mVariants[j][1];
            if (unit_stat["detailed"] && var_count > 0)
                var_count = var_count + '&thinsp;&#x00D7;&thinsp;' + 
                    this.mVariants[j][3] + '&thinsp;&#x21C9;&thinsp;' +
                    this.mVariants[j][2];
            has_zero |= (var_count == 0);
            list_val_rep.push(this.reprVariant(var_name, var_count, j));
        }
        this.mDivVarList.innerHTML = list_val_rep.join('\n');
        this.mDivVarList.className = "";
        
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero && !func_mode)? "block":"none";            
        this.careEnumZeros(false);
        if (func_mode && variants.length == 1)
            document.getElementById("elcheck--" + 0).disabled = true;
    },
    
    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        if (this.mFuncCtrl != null) {
            this.mFuncCtrl.updateCondition(cond);
        } else {
            this._updateState(cond[2], cond[3]);
        }
    },
    
    _updateState: function(op_mode, var_list, func_mode) {
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
                    this.mDivVarList.insertAdjacentHTML('beforeend', 
                        this.reprVariant(var_name, 0, this.mVariants.length, true));
                    this.mVariants.push([var_name, 0, 0]);
                }
                needs_zeros = true;
            }
        }
        this.careEnumZeros(needs_zeros, func_mode);
        this.checkControls();
    },
    
    careControls: function() {
        document.getElementById("cur-cond-enum").style.display = 
            (this.mVariants == null)? "none":"grid";
        for (idx = 1; idx < 3; idx++) {
            vmode = ["or", "and", "not"][idx];
            document.getElementById("cond-mode-" + vmode + "-span").
                style.visibility = (this.mOperationMode == null ||
                    (this.mStatusMode && idx != 2))? "hidden":"visible";
            document.getElementById("cond-mode-" + vmode).checked =
                (idx == this.mOperationMode);
        }
        this.arrangeControls();
    },

    arrangeControls: function() {
        if (!this.mArrangeBase)
            return;
        if (document.getElementById("cur-cond-enum").style.display == "none")
            return;
        block_h = document.getElementById(this.mArrangeBase).
            getBoundingClientRect().height;
        if (this.mFuncCtrl != null) {
            this.mDivFuncParam.style.display = "flex";
            block_h -= this.mDivFuncParam.getBoundingClientRect().height;
        } else { 
            this.mDivFuncParam.style.display = "none";
        }
        if ( block_h < this.mArrangeDelta)
            return;
        document.getElementById("cur-cond-enum-list").style.height = 
            block_h - this.mArrangeDelta;
    },

    careEnumZeros: function(opt, func_mode) {
        var check_enum_z = document.getElementById("cur-enum-zeros");
        if (func_mode) {
            show_zeros = true;
            check_enum_z.checked = show_zeros;
        } else {
            if (opt === undefined) {
                show_zeros = check_enum_z.checked;
            } else {
                show_zeros = opt;
                check_enum_z.checked = show_zeros;
            }
        }
        this.mDivVarList.className = (show_zeros)? "":"no-zeros";
    },
    
    getSelected: function() {
        var sel_names = [];
        if (this.mVariants != null) {
            for (j=0; j < this.mVariants.length; j++) {
                if (document.getElementById("elcheck--" + j).checked) {
                    sel_names.push(this.mVariants[j][0]);
                }
            }
        }
        return sel_names;
    },
    
    checkControls: function(opt) {
        if (this.mVariants == null) 
            return;
        this.careControls();
        var err_msg = null;
        if (opt !== undefined && this.mOperationMode != null) {
            if (this.mOperationMode == opt)
                this.mOperationMode = 0;
            else
                this.mOperationMode = opt;
        }
        sel_names = this.getSelected();
        
        if (this.mOperationMode == null)
            op_mode = "OR";
        else
            op_mode = ["OR", "AND", "NOT"][this.mOperationMode];
        
        condition_data = null;
        if (sel_names.length > 0) {
            condition_data = [op_mode, sel_names];
            if (sel_names.length == 1)
                err_msg = "1 item selected";
            else
                err_msg = sel_names.length + " items selected";
        } else
            err_msg = " Out of choice"
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }
        if (this.mFuncCtrl != null && condition_data) {
            var func_err = this.mFuncCtrl.checkCurError();
            if (func_err) {
                err_msg = func_err;
                if (func_err.startsWith(' '))
                    func_err = null;
            }
            if (func_err) {
                condition_data = null;
            } else {
                var func_params = this.mFuncCtrl.makeFuncParams();
                condition_data.push(func_params);
            }
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
function renderEnumStat(unit_name, expand_mode) {
    sUnitClassesH.renderEnumStat(unit_name, expand_mode);
}

/*************************************/
function fillStatRepNum(unit_stat, list_stat_rep) {
    val_min   = unit_stat["min"];
    val_max   = unit_stat["max"];
    counts    = unit_stat["counts"];
    if (counts[0] == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
    } else {
        if (val_min == val_max) {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                '</span>');
        } else {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                ' &le;&nbsp;...&nbsp;&le; ' + normFloatLongTail(val_max, true) + ' </span>');
        }
        list_stat_rep.push(': ' + reportStatCount(counts, unit_stat, 0));
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
        list_stat_rep.push('<div onclick="renderEnumStat(\'' + 
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
            reportStatCount(var_list[j], unit_stat, 1) + '</li>');
    }
    list_stat_rep.push('</ul>');
    if (list_count > 0) {
        list_stat_rep.push('<p class="stat-comment">...and ' + 
            list_count + ' variants more...</p>');
    }
}

function reportStatCount(count_info, unit_stat, shift) {
    if (unit_stat["detailed"] && count_info[1 + shift] > 0) {
        cnt = count_info[1 + shift];
        s_mult = (cnt > 1)? "s":"";
        return '<span class="stat-count">' + cnt + 
            ' transcript variant' + s_mult +  
            '(' + count_info[2 + shift] + 
            '&thinsp;&#x00D7;&thinsp;' + count_info[shift] + ')';
    } 
    cnt = count_info[shift];
    s_mult = (cnt > 1)? "s":"";
    return '<span class="stat-count">' + cnt + ' variant' + s_mult + '</span>';
}

/*************************************/
/* Create WS                         */
/*************************************/
var sCreateWsH = {
    mStage: null,
    mDSDir: null,
    mSpanModTitle: null,
    mInputModName: null,
    mDivModProblems: null,
    mDivModStatus: null,
    mButtonModStart: null,
    mButtonModCancel: null,
    mTaskId: null,
    mTimeH: null,
    
    init: function() {
        this.mSpanModTitle = document.getElementById("derive-ws-title");
        this.mInputModName = document.getElementById("derive-ws-name");
        this.mDivModProblems = document.getElementById("derive-ws-problems");
        this.mDivModStatus = document.getElementById("derive-ws-status");
        this.mButtonModStart = document.getElementById("derive-ws-start");
        this.mButtonModCancel = document.getElementById("derive-ws-cancel");
    },
    
    show: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDSDir = null;
        this.mTaskId = null;
        
        var info = sUnitsH.prepareWsCreate();
        if (info == null) 
            return;
        
        this.mSpanModTitle.innerHTML = 'Derive dataset for ' +
            info[0] + ' of ' + info[1];
        var err_msg = "";
        if (info[0] == info[1])
            err_msg = "Select subset of variants, operation is trivial";
        if (info[0] >= 9000)
            err_msg = "Too many variants, try to reduce";
        if (info[0] < 1)
            err_msg = "Empty set";
        this.mDivModProblems.innerHTML = err_msg;
        if (err_msg) {
            this.mStage = "BAD";
            this.checkControls();
            sViewH.modalOn(document.getElementById("derive-ws-back"));
            return;
        }
        this.mStage = "NAMES";
        ajaxCall("dirinfo", "", function(info) {
            sCreateWsH._setupName(info);})
    },
    
    _nameReserved: function(ds_name) {
        return this.mDSDir[ds_name] !=  undefined;
    },
    
    _setupName: function(dirinfo) {
        this.mDSDir = dirinfo["ds-dict"];
        ds_name_parts = sDSName.split('_');
        if (ds_name_parts[0].toLowerCase() == "xl") {
            name_idx = 0;
            name_prefix = "ws";
        } else {
            name_idx = ds_name_parts.length;
            ds_name_parts.push("");
            name_prefix = "";
        }        
        var no = 1;
        while (true) {
            ds_name_parts[name_idx] = name_prefix + no;
            ws_name = ds_name_parts.join('_');
            if (!this._nameReserved(ws_name))
                break;
            no += 1;
        }
        this.mInputModName.value = ws_name;
        this.mStage = "READY";
        this.checkControls();
        sViewH.modalOn(document.getElementById("derive-ws-back"));
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

/**********************************************/
/* Visual control for units and visual groups */
/**********************************************/
var sUnitClassesH = {
    mUnitClasses: null,
    mUnitItems: null,
    mVGroupsSeq: null,
    mDivTopBack: null,
    mDivMain: null,
    mSpanState: null,
    mSpanIntState: null,
    mBtnReset: null,
    mBtnDone: null,
    mCurCriterium: null,
    mCurTotalCounts: null,
    mCurEntropyRep: null,
    
    init: function() {
        this.mDivTopBack = document.getElementById("unit-classes-back");
        this.mDivMain = document.getElementById("unit-classes-main");
        this.mSpanState = document.getElementById("unit-classes-state");
        this.mSpanIntState = document.getElementById("unit-classes-int-state");
        this.mBtnReset = document.getElementById("unit-classes-reset");
        this.mBtnDone = document.getElementById("unit-classes-done");
    },
    
    setup: function(unit_classes) {
        this.mUnitClasses = unit_classes;
        var list_rep = [];
        var j, k;
        for (j = 0; j < this.mUnitClasses.length; j++) {
            unit_cls = this.mUnitClasses[j];
            list_rep.push('<div class="unit-classes-class">\n' +
                '  <div class="unit-class-title">' + 
                '<input id="ucl--' + j + '-all" type="checkbox" checked ' +
                'onclick="sUnitClassesH.update();">&nbsp;' + 
                unit_cls["title"] + '</div>');
            list_rep.push('<div class="unit-class-group" id="ucl-group--' + j + '">');
            for(k=0; k < unit_cls["values"].length; k++) {
                it_code = '--' + j + '-' + k;
                list_rep.push(
                    '    <div class="unit-class-val" id="div-ucl' + it_code + '">' +
                    '<input id="ucl' + it_code + '" type="checkbox" checked ' +
                    'onclick="sUnitClassesH.update();">&nbsp;' + 
                    unit_cls["values"][k] + '</div>');
            }
            list_rep.push('</div></div>');
        }
        this.mDivMain.innerHTML = list_rep.join("\n");
        this.showStatus();
        if (this.mUnitItems != null) {
            this.updateItems(this.mUnitItems);
        }
    },

    itInWork: function(it_classes, except_cls) {
        var j, k, in_w;
        if (this.mCurCriterium != null) {
            for (var j=0; j < this.mCurCriterium.length; j++) {
                if ((this.mCurCriterium[j] != null) 
                        && (j != except_cls)) {
                    in_w = false;
                    for (var k=0; k < it_classes[j].length; k++) {
                        if(this.mCurCriterium[j].
                            indexOf(it_classes[j][k]) >= 0) {
                            in_w = true;
                            break;
                        }
                    }
                    if (!in_w) {
                        return false;
                    }
                }
            }
        }
        return true;        
    },
    
    updateItems: function(unit_items, no_reset) {
        this.mUnitItems = unit_items;
        if (this.mUnitClasses == null) {
            return;
        }
        var cls_counts = [];
        var j, idx, k;
        for (j = 0; j < this.mUnitClasses.length; j++) {
            cls_counts.push(Array(this.mUnitClasses[j]["values"].length).fill(0));
        }
        for (idx=0; idx < this.mUnitItems.length; idx++) {
            it_classes = this.mUnitItems[idx]["classes"];
            for (j=0; j < this.mUnitClasses.length; j++) {
                if (!this.itInWork(it_classes, j))
                    continue;
                facet_idxs = it_classes[j];
                for (k=0; k < facet_idxs.length; k++) {
                    cls_counts[j][facet_idxs[k]]++;
                }
            }
        }
        for (j = 0; j < this.mUnitClasses.length; j++) {
            cls_total = cls_counts[j].reduce(function(acc, val) { return acc + val; }, 0)
            for (k=0; k < this.mUnitClasses[j]["values"].length; k++) {
                it_code = '--' + j + '-' + k;
                it_div = document.getElementById('div-ucl' + it_code);
                it_check = document.getElementById('ucl' + it_code);
                if (cls_counts[j][k] > 0) {
                    it_div.class = "unit-class-val";
                    it_check.disabled = (cls_total == cls_counts[j][k]);
                } else {
                    it_div.class = "unit-class-val blocked";
                    it_check.disabled = true;
                    it_check.checked = false;
                }
            }
        }
        this.update(no_reset);
    },
    
    update: function(no_reset) {
        this.mCurCriterium = [];
        var j, k, idx;
        for (j = 0; j < this.mUnitClasses.length; j++) {
            cls_div = document.getElementById("ucl-group--" + j);
            cls_check = document.getElementById("ucl--" + j + "-all");
            cls_div.style.display = (cls_check.checked)? "none":"block";
            var j_cr = null;
            if (!cls_check.checked) {
                j_cr = [];
                for(k=0; k < this.mUnitClasses[j]["values"].length; k++) {
                    it_code = '--' + j + '-' + k;
                    if (document.getElementById("ucl" + it_code).checked)
                        j_cr.push(k);
                }
            }
            this.mCurCriterium.push(j_cr);
        }
        var cnt_shown = 0;
        var groups_shown = [];
        var group_e_val = -1;
        for (idx = 0; idx < this.mUnitItems.length; idx++) {
            it = this.mUnitItems[idx];
            var in_w = this.itInWork(it["classes"]);
            if (groups_shown.length < this.mVGroupsSeq.length &&
                    idx == this.mVGroupsSeq[groups_shown.length]) {
                if (groups_shown.length > 0)
                    this.renderVGroupEntropy(groups_shown.length - 1, group_e_val);
                groups_shown.push(false);
                group_e_val = -1;
            }
            if (in_w) {
                cnt_shown++;
                groups_shown[groups_shown.length - 1] = true;
            }
            document.getElementById("stat--" + it["name"]).style.display = 
                (in_w)? "block": "none";
            e_val = this.renderEntopyReport(idx);
            if (in_w && e_val > group_e_val)
                group_e_val = e_val;
        }
        if (groups_shown.length > 0)
            this.renderVGroupEntropy(groups_shown.length - 1, group_e_val);
        for(idx=0; idx < groups_shown.length; idx++) {
            grp_el = document.getElementById("stat-vgroup--" + idx);
            if (grp_el)
                grp_el.style.display = (groups_shown[idx])? "block": "none";
        }
        if (cnt_shown == 0 && this.mUnitItems.length > 0 && !no_reset) {
            this.reset(true);
            return;
        }
        this.showStatus(cnt_shown, this.mUnitItems.length);
    },
    
    showStatus: function(cnt_shown, cnt_all) {
        if (cnt_shown == cnt_all) {
            state_msg = "all properties";
        } else {
            state_msg = "properties: <b>" + cnt_shown + "</b>/" + cnt_all;
        }
        this.mSpanState.innerHTML = state_msg;
        this.mSpanIntState.innerHTML = state_msg;
    },
    
    show: function() {
        this.mDivTopBack.style.display = "block";
    },

    hide: function() {
        this.mDivTopBack.style.display = "none";
    },
    
    reset: function(heavy_mode) {
        var j;
        for (j = 0; j < this.mUnitClasses.length; j++) {
            document.getElementById("ucl--" + j + "-all").checked = true;
            if (heavy_mode) {
                for(k=0; k < this.mUnitClasses[j]["values"].length; k++) {
                    it_code = '--' + j + '-' + k;
                    document.getElementById("ucl" + it_code).checked = true;
                }
            }
        }
        this.update();
        if (heavy_mode) {
            this.updateItems(this.mUnitItems, true);
        } else {
            this.hide();
        }
    },
    
    topUnitStat: function(unit_name) {
        if (!unit_name)
            return null;
        return document.getElementById(
            "stat--" + unit_name).getBoundingClientRect().top;
    },

    setupItems: function(items, total_counts, unit_map,  
            unit_names_to_load, div_el, expand_mode, click_func) {
        var list_stat_rep = [];
        var group_title = false;
        this.mCurTotalCounts = total_counts;
        this.mCurEntropyRep = [];
        this.mVGroupsSeq = [];
        for (idx = 0; idx < items.length; idx++) {
            unit_stat = items[idx];
            unit_name   = unit_stat["name"];
            unit_map[unit_name] = idx;
            if (group_title != unit_stat["vgroup"] || unit_stat["vgroup"] == null) {
                if (group_title != false) {
                    list_stat_rep.push('</div>');
                }
                group_title = unit_stat["vgroup"];
                list_stat_rep.push('<div class="stat-group" id="stat-vgroup--' + 
                        this.mVGroupsSeq.length + '">');
                list_stat_rep.push('<div class="stat-group-title">' + 
                    ((group_title != null)? group_title:"") + 
                    '<span class="entropy-info" id="vgroup-entropy--' + 
                    this.mVGroupsSeq.length + '"></span>');
                this.mVGroupsSeq.push(idx);
                if (unit_name == "Rules") {
                    list_stat_rep.push(
                        '<span id="flt-go-dtree" ' +
                            'title="Configure decision trees as rules..." ' +
                        'onclick="goToPage(\'DTREE\');"">&#x2699;</span>')
                }
                list_stat_rep.push('</div>');
            }
            name_decor = (unit_stat["kind"] == "func" || 
                unit_stat["sub-kind"] == "func")? "(...)":"";
            click_support = '';
            if (click_func)
                click_support = '<span class="unit-click" onclick="' +
                    click_func + '(\'' + unit_name + '\')">&#x25c0;</span>&nbsp;';
            list_stat_rep.push('<div id="stat--' + 
                unit_name + '" class="stat-unit" ');
            if (unit_stat["tooltip"]) 
                list_stat_rep.push('title="' + 
                    escapeText(unit_stat["tooltip"]) + '" ');

            list_stat_rep.push(
                'onclick="sUnitsH.selectUnit(\'' + unit_name + '\');">');
            list_stat_rep.push('<div class="wide">' +
                '<span class="stat-unit-name">' +
                click_support + unit_name + name_decor + '</span>' +
                '<span class="entropy-info" id="unit-entropy--' + idx + '"></span>');
            if (unit_stat["title"]) 
                list_stat_rep.push('<span class="stat-unit-title">' + 
                    unit_stat["title"] + '</span>');
            list_stat_rep.push('</div>')
            list_stat_rep.push('<div id="stat-data--' + 
                unit_name + '" class="stat-unit-data">');
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
            this.mCurEntropyRep.push(this.unitEntropyReport(unit_stat));
            list_stat_rep.push('</div></div>')
        }
        if (group_title != false) {
            list_stat_rep.push('</div>')
        }
        div_el.innerHTML = list_stat_rep.join('\n');
        this.updateItems(items);
    },
    
    renderEnumStat: function(unit_name, expand_mode) {
        unit_stat = sUnitsH.getUnitStat(unit_name);
        list_stat_rep = [];
        fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
        div_el = document.getElementById("stat-data--" + unit_stat["name"]);
        div_el.innerHTML = list_stat_rep.join('\n');
    },
    
    refillUnitStat: function(unit_stat, unit_idx, expand_mode) {
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
        e_rep = this.unitEntropyReport(unit_stat);
        if (e_rep[0] >= 0)
            this.mCurEntropyRep[unit_idx] = e_rep;
    },
    
    renderEntopyReport: function(unit_idx) {
        e_el = document.getElementById("unit-entropy--" + unit_idx);
        e_rep = this.mCurEntropyRep[unit_idx];
        e_el.innerHTML = '['+ e_rep[0].toFixed(3) + ']';
        e_el.title = e_rep[1];
        return e_rep[0];
    },
    
    renderVGroupEntropy: function(group_idx, e_val) {
        e_el = document.getElementById("vgroup-entropy--" + group_idx);
        e_el.innerHTML = '['+ e_val.toFixed(3) + ']';
    },
    
    unitEntropyReport: function(unit_stat) {
        if (unit_stat == null || unit_stat["incomplete"])
            return [-1, "loading"];
        var total = this.mCurTotalCounts[(unit_stat["detailed"])?1:0];
        var var_counts = [];
        if (unit_stat["kind"] == "numeric") {
            if (unit_stat["histogram"]) {
                hist_seq = unit_stat["histogram"][3];
                for (var j = 0; j < hist_seq.length; j++) {
                    var_counts.push(hist_seq[j]);
                    total -= hist_seq[j];
                }
                if (total > 0)
                    var_counts.push(total);
            }
        } else if (unit_stat["kind"] == "enum") {
            var c_idx = (unit_stat["detailed"]? 2:1);
            for (var j = 0; j < unit_stat["variants"].length; j++) {
                cnt = unit_stat["variants"][j][c_idx];
                var_counts.push(cnt);
                total -= cnt;
            }
            // No special work for multiset
            if (total > 0)
                var_counts.push(total);
        }
        
        return entropyReport(var_counts);
    }
    
};

/*************************************/

/*************************************/
function entropyReport(counts) {
    var total = 0.;
    for (j = 0; j < counts.length; j++) {
        total += counts[j];
    }
    if (total < 3) 
        return [-1, "E=0! T=" + total];
    var sum_e = 0.;
    var cnt = 0;
    for (j = 0; j < counts.length; j++) {
        if (counts[j] == 0)
            continue;
        cnt++;
        quote = counts[j] / total;
        sum_e -= quote * Math.log2(quote);
    }
    l_tot = Math.log2(total);
    norm_e = sum_e / l_tot;
    return [norm_e, "E=" + norm_e.toFixed(3) + " S=" + l_tot.toFixed(3) + 
        " T=" + total + " N=" + cnt];
}
