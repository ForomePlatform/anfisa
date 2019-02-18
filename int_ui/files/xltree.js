var sDSName = null;
var sTitlePrefix = null;
var sCommonTitle = null;

/*************************************/
function initXL(ds_name, common_title) {
    sOpNumH.init();
    sOpEnumH.init();
    sViewH.init();
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    sCommonTitle = common_title;
    sDSName = ds_name; 
    window.name = sCommonTitle + "/" + sDSName;
    document.title = sTitlePrefix + "/" + sDSName;
    document.getElementById("xl-name").innerHTML = sDSName;
    sDecisionTree.setup();
}
    
/**************************************/
function ajaxCall(rq_name, args, func_eval) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            func_eval(info);
        }
    };
    xhttp.open("POST", rq_name, true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(args); 
}

/**************************************/
var sDecisionTree = {
    mPoints: null,
    mTree: null,
    mStat: null,
    mCurPointNo: null,
    
    setup: function() {
        args = "ds=" + sDSName;
        if (this.mTree != null) 
            args += "&tree=" + encodeURIComponent(this.mTree);
        ajaxCall("xltree", args, function(info){sDecisionTree._setup(info);})
    },
    
    _setup: function(info) {
        this.mTree = info["tree"];
        this.mStat = this.mTree[0][1];
        this.mPoints = [];
        this.mCurPointNo = null;
        var list_rep = ['<table class="d-tree">'];
        for (var idx = 1; idx < this.mTree.length; idx++) {
            it = this.mTree[idx];
            p_kind = it[0];
            if (p_kind == "comment") {
                list_rep.push('<tr><td class="tree-comment" colspan="3" ># ' +
                    escapeText(it[1]) + '</td></tr>');
                continue;
            }
            this.mPoints.push(it);
            p_no = it[1]; p_lev = it[2]; p_count = it[3];
            if (p_count > 0) {
                list_rep.push('<tr id="p_td__' + p_no + 
                    '" class="active" onclick="sDecisionTree.selectPoint(' + 
                    p_no + ');">');
            } else {
                list_rep.push('<tr>');
            }
            list_rep.push('<td class="point-no" id="p_no__' + p_no + '">' + 
                p_no + '</td>');
            list_rep.push('<td class="point-cond">')
            for (var j=0; j < p_lev; j++)
                list_rep.push('&emsp;');
            p_count_class = "point-count";
            p_count_add = "";
            if (p_kind == "cond") {
                list_rep.push('<span class="point-instr">if</span> ');
                p_cond = it[4];
                if (p_cond[0] == "and") {
                    list_rep.push('<div class="point-block"><div class="point-block1">' + 
                        '<div class="point-op">and</div><div class="point-list">') 
                    for (var j=1; j < p_cond.length; j++) {
                        list_rep.push('<div class="point-cond1" id="p_cond__' +
                            p_no + '_' + j + '">' + getConditionDescr(p_cond[j]) + 
                            '</div>');
                    }
                    list_rep.push('</div></div></div>');
                } else {
                    list_rep.push('<div class="point-cond" id="p_cond__' +
                        p_no + '">' + getConditionDescr(p_cond) + '</div>');
                }
            } else {
                p_decision = it[4]? "True": "False";
                if (p_count > 0)
                    p_count_class = it[4]? "point-count-accept":"point-count-reject";
                    p_count_add = it[4]? "+":"-";
                list_rep.push('<span class="point-instr">return ' + p_decision +
                    '</span> ');
            }
            list_rep.push('</td><td class="' + p_count_class + '">' + p_count_add + 
                p_count + '</td></tr>');
        }
        list_rep.push('</table>'); 
        document.getElementById("decision-tree").innerHTML = list_rep.join('\n');
        //alert("tb:" + list_rep.join('\n'));
        this.selectPoint(0);
        
        document.getElementById("report-accepted").innerHTML = "" + (this.mStat[1]);
        rep_rejected = "" + this.mStat[2];
        if (this.mStat[0] - this.mStat[1] - this.mStat[2] > 0) {
            rep_rejected += '/' + (this.mStat[0] - this.mStat[1] - this.mStat[2]);
        }
        document.getElementById("report-rejected").innerHTML = rep_rejected;
    },
    
    selectPoint: function(point_no) {
        if (this.mCurPointNo == point_no) 
            return;
        if (this.mPoints[point_no][3] == 0)
            return;
        var new_el = document.getElementById("p_td__" + point_no);
        if (new_el == null) 
            return;
        if (this.mCurPointNo != null) {
            var prev_el = document.getElementById("p_td__" + this.mCurPointNo);
            prev_el.className = "active";
        }
        this.mCurPointNo = point_no;
        new_el.className = "cur";
        sUnitsH.setup(this.mTree, this.mCurPointNo);
    }    
}

/**************************************/
var sUnitsH = {
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,    
    
    setup: function(decision_tree, point_no) {
        args = "ds=" + sDSName + "&tree=" +
            encodeURIComponent(JSON.stringify(decision_tree)) + 
            "&no=" + point_no;
        ajaxCall("xlstat", args, function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        count = info["count"];
        total = info["total"]
        document.getElementById("list-report").innerHTML = (count == total)?
            total : count + "/" + total;

            
        this.mItems = info["stat-list"];
        this.mUnitMap = {}
        var list_stat_rep = [];
        var group_title = false;
        for (idx = 0; idx < this.mItems.length; idx++) {
            unit_stat = this.mItems[idx];
            unit_type = unit_stat[0];
            unit_name   = unit_stat[1]["name"];
            unit_title  = unit_stat[1]["title"];
            unit_vgroup = unit_stat[1]["vgroup"];
            this.mUnitMap[unit_name] = idx;
            if (group_title != unit_vgroup || unit_vgroup == null) {
                if (group_title != false) {
                    list_stat_rep.push('</div>');
                }
                group_title = unit_vgroup;
                list_stat_rep.push('<div class="stat-group">');
                if (group_title != null) {
                    list_stat_rep.push('<div class="stat-group-title">' + 
                        group_title + '</div>');
                }
            }
            list_stat_rep.push('<div id="stat--' + unit_name + 
                '" class="stat-unit" onclick="sUnitsH.selectUnit(\'' + 
                unit_name + '\');">');
            list_stat_rep.push('<div class="wide"><span class="stat-unit-name">' +
                unit_name + '</span>');
            if (unit_title)
                list_stat_rep.push('<span class="stat-unit-title">' + 
                    unit_title + '</span>');
            list_stat_rep.push('</div>')
            if (unit_type == "long" || unit_type == "float") {
                this._fillStatRepNum(unit_stat, list_stat_rep);
            } else {
                this._fillStatRepEnum(unit_stat, list_stat_rep);
            }
            list_stat_rep.push('</div>')
        }
        if (group_title != false) {
            list_stat_rep.push('</div>')
        }
        document.getElementById("stat-list").innerHTML = list_stat_rep.join('\n');
        
        this.mCurUnit = null;
        
        if (this.mCurUnit == null)
            this.selectUnit(this.mItems[0][1]["name"]);
    },

    _fillStatRepNum: function(unit_stat, list_stat_rep) {
        val_min   = unit_stat[2];
        val_max   = unit_stat[3];
        count     = unit_stat[4];
        cnt_undef = unit_stat[5];
        if (count == 0) {
            list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
        } else {
            if (val_min == val_max) {
                list_stat_rep.push('<span class="stat-ok">' + val_min + '</span>');
            } else {
                list_stat_rep.push('<span class="stat-ok">' + val_min + 
                    ' =< ...<= ' + val_max + ' </span>');
            }
            list_stat_rep.push(': <span class="stat-count">' + count + 
                ' records</span>');
            if (cnt_undef > 0) 
                list_stat_rep.push('<span class="stat-undef-count">+' + 
                    cnt_undef + ' undefined</span>');
        }
    },
        
    _fillStatRepEnum: function(unit_stat, list_stat_rep) {
        var_list = unit_stat[2];
        list_count = 0;
        for (j = 0; j < var_list.length; j++) {
            if (var_list[j][1] > 0)
                list_count++;
        }
        if (list_count > 0) {
            list_stat_rep.push('<ul>');
            view_count = (list_count > 6)? 3: list_count; 
            for (j = 0; j < var_list.length && view_count > 0; j++) {
                var_name = var_list[j][0];
                var_count = var_list[j][1];
                if (var_count == 0)
                    continue;
                view_count -= 1;
                list_count--;
                list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                    '<span class="stat-count">' +
                    var_count + ' records</span></li>');
            }
            list_stat_rep.push('</ul>');
            if (list_count > 0) {
                list_stat_rep.push('<p><span class="stat-comment">...and ' + 
                    list_count + ' variants more...</span></p>');
            }
        } else {
            list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
        }
    },
    
    getCurUnitName: function() {
        return this.mCurUnit;
    },
    
    getCurUnitStat: function() {
        if (this.mCurUnit == null)
            return null;
        return this.mItems[this.mUnitMap[this.mCurUnit]];
    },
    
    selectUnit: function(stat_unit, force_it) {
        if (sDecisionTree  != null)
            return; 
        if (this.mCurUnit == stat_unit && !force_it) 
            return;
        var new_unit_el = document.getElementById("stat--" + stat_unit);
        if (new_unit_el == null) 
            return;
        if (this.mCurUnit != null) {
            var prev_el = document.getElementById("stat--" + this.mCurUnit);
            prev_el.className = prev_el.className.replace(" cur", "");
        }
        this.mCurUnit = stat_unit;
        new_unit_el.className = new_unit_el.className + " cur";
        sConditionsH.correctCurUnit(this.mCurUnit);
        sOpCondH.updateUnit(this.mCurUnit);
    }
    
};
    
/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mIdxToUpdate: null,
    mIdxToAdd: null,
    
    updateUnit: function() {
        unit_name = sUnitsH.getCurUnitName();
        document.getElementById("cond-title").innerHTML = (unit_name)? unit_name:"";
        if (unit_name == null) {
            sOpEnumH.suspend();
            sOpNumH.suspend();
            this.formCondition(null);
            return;
        } 
        unit_stat = sUnitsH.getCurUnitStat();
        unit_type = unit_stat[0];
        if (unit_type == "long" || unit_type == "float") {
            sOpEnumH.suspend();
            this.mCurTpHandler = sOpNumH;
        } else {
            sOpNumH.suspend();
            this.mCurTpHandler = sOpEnumH;
        }
        this.mCurTpHandler.updateUnit(unit_stat);

        if (sConditionsH.getCurCondNo() != null) {
            cond = sConditionsH.getCurCond();
            if (cond[1] == unit_name)
                this.mCurTpHandler.updateCondition(cond);
        }
        this.mCurTpHandler.checkControls();
    },
    
    formCondition: function(condition_data, error_msg, cond_mode, add_always) {
        cur_unit_name = sUnitsH.getCurUnitName();
        this.mCondition   = null;
        this.mIdxToAdd    = null;
        this.mIdxToUpdate = null;
        if (condition_data != null) {
            this.mCondition = [this.mCurTpHandler.getType(), cur_unit_name].concat(
                condition_data);
            this.mIdxToUpdate = sConditionsH.findCond(cur_unit_name, cond_mode);
            
            if (this.mIdxToUpdate == null) {
                if (add_always) 
                    this.mIdxToUpdate = sConditionsH.findCond(cur_unit_name);
                else {
                    this.mIdxToAdd = sConditionsH.findCond(cur_unit_name);
                    if (this.mIdxToAdd == null)
                        this.mIdxToAdd = sConditionsH.nextIdx();
                }
            }
            if (add_always) {
                this.mIdxToAdd = (this.mIdxToUpdate == null)?
                    sConditionsH.nextIdx(): this.mIdxToUpdate + 1;
            }
            
        }
        document.getElementById("cond-text").innerHTML = 
            (this.mCondition)? getConditionDescr(this.mCondition, true):"";
        document.getElementById("cond-error").innerHTML = (error_msg)? error_msg:"";
        this.careControls();
    },
    
    availableActions: function() {
        ret = []
        if (this.mCondition != null) {
            if (this.mIdxToAdd != null)
                ret.push("add");
            if (this.mIdxToUpdate != null)
                ret.push("update");
        }
        return ret;
    },
    
    applyCondition: function(condition_seq, func_name) {
        if ( func_name == "add" && this.mIdxToAdd != null) {
            new_seq = condition_seq.slice();
            new_seq.splice(this.mIdxToAdd, 0, this.mCondition);
            return new_seq;
        }
        if ( func_name == "update" && this.mIdxToUpdate != null) {
            new_seq = condition_seq.slice();
            new_seq[this.mIdxToUpdate] = this.mCondition;
            return new_seq;
        }
        return null;
    },
    
    careControls: function() {
    }
};

/**************************************/
var sOpNumH = {
    mInfo: null,
    mInputMin: null,
    mInputMax: null,
    mCheckUndef: null,
    mSpanUndefCount: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
        this.mCheckUndef = document.getElementById("cond-undef-check")
        this.mSpanUndefCount = document.getElementById("cond-undef-count");
    },
    
    getType: function() {
        return "numeric";
    },

    suspend: function() {
        this.mInfo = null;
        this.careControls();
    },
    
    updateUnit: function(unit_stat) {
        this.mInfo = {
            op:         0,
            val_cur:    null,
            updating:   false,
            with_undef: null,
            unit_type:  unit_stat[0],
            val_min:    unit_stat[2],
            val_max:    unit_stat[3],
            count:      unit_stat[4],
            cnt_undef:  unit_stat[5]}
            
        if (this.mInfo.cnt_undef > 0) 
            this.mInfo.with_undef = true;
        if (this.mInfo.val_min == this.mInfo.val_max) 
            this.mInfo.op = -1;

        document.getElementById("cond-min").innerHTML = this.mInfo.val_min;
        document.getElementById("cond-max").innerHTML = this.mInfo.val_max;
        document.getElementById("cond-sign").innerHTML = 
            (this.mInfo.val_min == this.mInfo.val_max)? "=":"&le;";
        this.mInputMin.value = this.mInfo.val_min;
        this.mInputMax.value = this.mInfo.val_max;
        this.mCheckUndef.checked = (this.mInfo.cnt_undef > 0);
        this.mSpanUndefCount.innerHTML = (this.mInfo.cnt_undef > 0)?
            ("undefined:" + this.mInfo.cnt_undef) : "";
    },

    updateCondition: function(cond) {
        this.mInfo.op           = cond[2];
        this.mInfo.val_cur      = cond[3];
        this.mInfo.with_undef   = cond[4];
        this.mInfo.updating     = true;
        if (this.mInfo.op == 0) {
            this.mInputMin.value = this.mInfo.val_cur;
        } else {
            this.mInputMax.value = this.mInfo.val_cur;
        }
        document.getElementById("cond-sign").innerHTML = "&le;";
        if (this.mInfo.with_undef != null) {
            this.mCheckUndef.checked = this.mInfo.with_undef;
            this.mSpanUndefCount.innerHTML = "undefined:" + this.mInfo.cnt_undef;
        }
    },

    careControls: function() {
        document.getElementById("cur-cond-numeric").style.display = 
            (this.mInfo == null)? "none":"block";
        this.mInputMin.style.visibility = 
            (this.mInfo && this.mInfo.op == 0)? "visible":"hidden";
        this.mInputMax.style.visibility = 
            (this.mInfo && this.mInfo.op == 1)? "visible":"hidden";
        this.mCheckUndef.style.visibility = 
            (this.mInfo && this.mInfo.cnt_undef > 0)? "visible":"hidden";
        this.mSpanUndefCount.style.visibility = 
            (this.mInfo && this.mInfo.cnt_undef > 0)? "visible":"hidden";
    },

    checkControls: function(opt) {
        if (this.mInfo == null) 
            return;
        var error_msg = null;
        if (opt == true && this.mInfo.op >= 0) {
            this.mInfo.op = 1 - this.mInfo.op;
        }
        if (this.mInfo.with_undef != null) {
            this.mInfo.with_undef = this.mCheckUndef.checked;
        }
        if (this.mInfo.op == 0) {
            val = toNumeric(this.mInfo.unit_type, this.mInputMin.value);
            if (val != null) {
                if (val < this.mInfo.val_min) {
                    if (!this.mInfo.updating)
                        error_msg = "Lower bound is above minimal value";
                    else
                        error_msg = "";
                }
                this.mInfo.val_cur = val;
            }
            else {
                error_msg = "Bad numeric value";
            }
            this.mInputMin.className = (error_msg == null)? "num-inp":"num-inp bad";
        } 
        if (this.mInfo.op == 1) {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value);
            if (val != null) {
                if (val > this.mInfo.val_max) {
                    if (!this.mInfo.updating)
                        error_msg = "Upper bound is below maximum value";
                    else
                        error_msg = "";
                }
                this.mInfo.val_cur = val;
            }
            else {
                error_msg = "Bad numeric value";
            }
            this.mInputMax.className = (error_msg == null)? "num-inp":"num-inp bad";
        }
        condition_data = null;
        if (!error_msg) {
            condition_data = this.formConditionData();
            if (condition_data == null)
                error = "";
        }
        sOpCondH.formCondition(
            condition_data, error_msg, this.mInfo.op, false);
        this.careControls();
    },

    formConditionData: function() {
        if (this.mInfo.op == -1) {
            if (this.mInfo.cnt_undef > 0 && this.mInfo.with_undef) {
                return [-1, null, true];
            }
        } else if (this.mInfo.op == 0) {
            if (this.mInfo.val_cur != null && (this.mInfo.updating ||
                    (this.mInfo.val_min != this.mInfo.val_cur))) {
                return [0, this.mInfo.val_cur, this.mInfo.with_undef];
            } else {
                if (this.mInfo.cnt_undef > 0 && !this.mInfo.with_undef) {
                    return [-1, null, false];
                }
            }
        } else {
            if (this.mInfo.val_cur != null && (this.mInfo.updating ||
                (this.mInfo.val_max != this.mInfo.val_cur))) {
                return [1, this.mInfo.val_cur, this.mInfo.with_undef];
            } else {
                if (this.mInfo.cnt_undef > 0 && !this.mInfo.with_undef) {
                    return [-1, null, false];
                }
            }
        }
        return null;
    }
};

/**************************************/
var sOpEnumH = {
    mVariants: null,
    mOperationMode: null,
    mDivVarList: null,

    init: function() {
        this.mDivVarList = document.getElementById("op-enum-list");
    },
    
    getType: function() {
        return "enum";
    },

    suspend: function() {
        this.mVariants = null;
        this.mOperationMode = null;
        this.careControls();
    },

    updateUnit: function(unit_stat) {
        this.mVariants = unit_stat[2];
        this.mOperationMode = (unit_stat[0] == "status")? null:0;
        this.careEnumZeros(false);
        
        list_val_rep = [];
        has_zero = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            var_count = this.mVariants[j][1];
            has_zero |= (var_count == 0);
            list_val_rep.push('<div class="enum-val' + 
                ((var_count==0)? " zero":"") +'">' +
                '<input id="elcheck--' + j + '" type="checkbox" ' + 
                'onchange="sOpEnumH.checkControls();"/>&emsp;' + var_name + 
                '<span class="enum-cnt">(' + var_count + ')</span></div>');
        }
        this.mDivVarList.innerHTML = list_val_rep.join('\n');
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero)? "block":"none";            
        this.careEnumZeros(false);
    },
    
    updateCondition: function(cond) {
        if (this.mOperationMode != null)
            this.mOperationMode = ["", "AND", "ONLY", "NOT"].indexOf(cond[2]);
        var_list = cond[3];
        needs_zeros = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            if (var_list.indexOf(var_name) < 0)
                continue;
            needs_zeros |= (this.mVariants[j][1] == 0);
            document.getElementById("elcheck--" + j).checked = true;
        }
        this.careEnumZeros(needs_zeros);
    },
    
    careControls: function() {
        document.getElementById("cur-cond-enum").style.display = 
            (this.mVariants == null)? "none":"block";
        for (idx = 1; idx < 4; idx++) {
            vmode = ["or", "and", "only", "not"][idx];
            document.getElementById("cond-mode-" + vmode + "-span").
                style.visibility = (this.mOperationMode == null)? "hidden":"visible";
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
    
    checkControls: function(opt) {
        if (this.mVariants == null) 
            return;
        this.careControls();
        var error_msg = null;
        if (opt != undefined && this.mOperationMode != null) {
            if (this.mOperationMode == opt)
                this.mOperationMode = 0;
            else
                this.mOperationMode = opt;
            
        }
        sel_names = [];
        for (j=0; j < this.mVariants.length; j++) {
            if (document.getElementById("elcheck--" + j).checked)
                sel_names.push(this.mVariants[j][0]);
        }
        op_mode = "";
        if (this.mOperationMode != null)
            op_mode = ["", "AND", "ONLY", "NOT"][this.mOperationMode];
        
        condition_data = null;
        if (sel_names.length > 0) {
            condition_data = [op_mode, sel_names];
        }

        sOpCondH.formCondition(condition_data, "", op_mode, true);
        this.careControls();
    }

};


/*************************************/
/* Top controls                      */
/*************************************/
var sViewH = {
    mShowToDrop: null,
    mDropCtrls: [],
    mModalCtrls: [],
    
    init: function() {
        window.onClick = function(event_ms) {sViewH.onclick(event_ms);}
        this.addToDrop(document.getElementById("ds-control-menu"));
    },

    addToDrop: function(ctrl) {
        this.mDropCtrls.push(ctrl);
    },

    dropOn: function(ctrl) {
        if (ctrl.style.display == "block") {
            this.dropOff();
        } else {
            this.dropOff();
            ctrl.style.display = "block";
            this.mShowToDrop = true;
        }
    },
    
    dropOff: function() {
        this.mShowToDrop = false;
        for (idx = 0; idx < this.mDropCtrls.length; idx++) {
            this.mDropCtrls[idx].style.display = "none";
        }
    },
    
    modalOn: function(ctrl) {
        if (this.mModalCtrls.indexOf(ctrl) < 0)
            this.mModalCtrls.push(ctrl);
        this.modalOff();
        ctrl.style.display = "block";
    },
    
    modalOff: function() {
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            this.mModalCtrls[idx].style.display = "none";
        }
    },
    
    onclick: function(event_ms) {
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            if (event_ms.target == this.mModalCtrls[idx]) 
                this.modalOff();
        }
        if (this.mShowToDrop && !event_ms.target.matches('.drop')) {
            this.dropOff();
        }
    }
};

function openControlMenu() {
    sViewH.dropOn(document.getElementById("ds-control-menu"));
}

function goHome() {
    sViewH.dropOff();
    window.open('dir', sCommonTitle + ':dir');
}

function openNote() {
    sViewH.dropOff();
    loadNote();
    sViewH.modalOn(document.getElementById("note-back"));
}

function saveNote() {
    sViewH.dropOff();
    loadNote(document.getElementById("note-content").value);
    sViewH.modalOff();
}

function loadNote(content) {
    args = "ds=" + sDSName;
    if (content) 
        args += "&note=" + encodeURIComponent(content);        
    ajaxCall("dsnote", args, function(info) {
        document.getElementById("note-ds-name").innerHTML = info["ds"];
        document.getElementById("note-content").value = info["note"];
    });
}

/*************************************/
/* Utilities                         */
/*************************************/
function getConditionDescr(cond, short_form) {
    rep_cond = (short_form)? []:[cond[1]];
    if (cond != null && cond[0] == "numeric") {
        if (cond[2]) 
                rep_cond.push("&le; " + cond[3]);
        else
                rep_cond.push("&ge; " + cond[3]);
        /*switch (cond[4]) {
            case true:
                rep_cond.push("with undef");
                break
            case false:
                rep_cond.push("w/o undef");
                break;
        }*/
        return rep_cond.join(" ");
    }
    if (cond != null && cond[0] == "enum") {
        rep_cond.push("IN");
        if (cond[2] && cond[2]!="OR") 
            rep_cond.push('[' + cond[2] + ']');
        sel_names = cond[3];
        if (sel_names.length > 0)
            rep_cond.push(sel_names[0]);
        else
            rep_cond.push("&lt;?&gt;")
        rep_cond = [rep_cond.join(' ')];        
        rep_len = rep_cond[0].length;
        for (j=1; j<sel_names.length; j++) {
            if (short_form && rep_len > 45) {
                rep_cond.push('<i>+ ' + (sel_names.length - j) + ' more</i>');
                break;
            }
            rep_len += 2 + sel_names[j].length;
            rep_cond.push(sel_names[j]);
        }
        return rep_cond.join(', ');
    }
    return ""
}

/*************************************/
function isStrInt(x) {
    xx = parseInt(x);
    return !isNaN(xx) && xx.toString() == x;
}

function isStrFloat(x) {
    if (isStrInt(x)) 
        return true;
    xx = parseFloat(x);
    return !isNaN(xx) && xx.toString().indexOf('.') != -1;
}

function toNumeric(tp, x) {
    if (tp == "int") {
        if (!isStrInt(x)) return null;
        return parseInt(x)
    }
    if (!isStrFloat(x)) return null;
    return parseFloat(x);
}

/*************************************/
var tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function replaceTag(tag) {
    return tagsToReplace[tag] || tag;
}

function escapeText(str) {
    return str.replace(/[&<>]/g, replaceTag);
}