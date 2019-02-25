var sDSName = null;
var sTitlePrefix = null;
var sCommonTitle = null;

/*************************************/
function initXL(ds_name, common_title) {
    sOpCondH.init();
    sOpNumH.init();
    sOpEnumH.init();
    sTreeCtrlH.init();
    sVersionsH.init();
    sViewH.init();
    sCreateWsH.init();
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
    mCounts: null,
    mStat: null,
    mCurPointNo: null,
    mOpCond: null,
    mOpIdx: null,
    
    setup: function(tree_descr, version, instruction) {
        args = "ds=" + sDSName;
        if (tree_descr) {
            if (tree_descr == true)
                tree_descr = JSON.stringify(this.mTree);
            args += "&tree=" + encodeURIComponent(tree_descr);
        }
        if (version != undefined && version != null)  {
            args += "&version=" + encodeURIComponent(version);
        }
        if (instruction)
            args += "&instr=" + encodeURIComponent(instruction);
        ajaxCall("xltree", args, function(info){sDecisionTree._setup(info);})
    },
    
    _setup: function(info) {
        this.mTree = info["tree"];
        this.mStat = info["stat"];
        this.mCounts = info["counts"];
        sTreeCtrlH.update(info["cur_version"], info["versions"])
        this.mPoints = [];
        this.mOpIdx = null;
        var list_rep = ['<table class="d-tree">'];
        for (var idx = 0; idx < this.mTree.length; idx++) {
            it = this.mTree[idx];
            p_kind = it[0];
            if (p_kind == "comment") {
                list_rep.push('<tr><td class="tree-comment" colspan="3" ># ' +
                    escapeText(it[1]) + '</td></tr>');
                continue;
            }
            p_no = this.mPoints.length; p_lev = it[1]; p_count = this.mCounts[p_no];
            this.mPoints.push(it);
            if (p_count > 0) {
                list_rep.push('<tr id="p_td__' + p_no + 
                    '" class="active" onclick="sDecisionTree.selectPoint(' + 
                    p_no + ');">');
            } else {
                list_rep.push('<tr>');
            }
            list_rep.push('<td class="point-no" id="p_no__' + p_no + '">' + 
                (p_no + 1) + '</td>');
            list_rep.push('<td class="point-cond">')
            for (var j=0; j < p_lev; j++)
                list_rep.push('&emsp;');
            p_count_class = "point-count";
            p_count_add = "";
            if (p_kind == "cond") {
                list_rep.push('<span class="point-instr">if</span> ');
                p_cond = it[2];
                if (p_cond[0] == "and") {
                    list_rep.push('<div class="point-block"><div class="point-block1">' + 
                        '<div class="point-op">and</div><div class="point-list">') 
                    for (var j=1; j < p_cond.length; j++) {
                        list_rep.push('<div class="point-cond" id="p_cond__' +
                            p_no + '_' + j + '">' + 
                            this._markEdit(p_cond[j], p_no, j, p_count > 0) +
                            getConditionDescr(p_cond[j]) + '</div>');
                    }
                    list_rep.push('</div></div></div>');
                } else {
                    list_rep.push('<div class="point-cond" id="p_cond__' +
                        p_no + '">' + this._markEdit(p_cond, p_no, -1, p_count > 0) + 
                        getConditionDescr(p_cond) + '</div>');
                }
            } else {
                p_decision = it[2]? "True": "False";
                p_count_class = it[2]? "point-count-accept":"point-count-reject";
                p_count_add = it[2]? "+":"-";
                list_rep.push('<span class="point-instr">return ' + p_decision +
                    '</span> ');
            }
            list_rep.push('</td><td class="' + p_count_class + '">' + p_count_add + 
                p_count + '</td></tr>');
        }
        list_rep.push('</table>'); 
        document.getElementById("decision-tree").innerHTML = list_rep.join('\n');
        //alert("tb:" + list_rep.join('\n'));
        point_no = (this.mCurPointNo)? this.mCurPointNo: 0;
        while (point_no > 0) {
            if (point_no >= this.mPoints.length || this.mCounts[point_no] == 0)
                point_no--;
            else
                break;
        }
        this.mCurPointNo = null;
        this.selectPoint(point_no);
        
        document.getElementById("report-accepted").innerHTML = "" + (this.mStat[1]);
        rep_rejected = "" + this.mStat[2];
        if (this.mStat[0] - this.mStat[1] - this.mStat[2] > 0) {
            rep_rejected += '/' + (this.mStat[0] - this.mStat[1] - this.mStat[2]);
        }
        document.getElementById("report-rejected").innerHTML = rep_rejected;
    },
    
    _markEdit: function(p_cond, point_no, cond_idx, not_empty) {
        if (!not_empty)
            return '';
        if (p_cond[0] == "numeric") 
            return '<span class="point-edit" onclick="sDecisionTree.editCond(' +
                point_no + ', ' + cond_idx + ');">&#9874;</span>';
        return '';
    },
    
    selectPoint: function(point_no) {
        if (this.mCurPointNo == point_no) 
            return;
        if (this.mCounts[point_no] == 0)
            return;
        if (sUnitsH.postAction(
            'sDecisionTree.selectPoint(' + point_no + ');'))
            return;
        sViewH.modalOff();
        this._highlightCondition(false);
        this.mOpCond = null;
        this.mOpIdx = null;
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
    },
    
    editCond: function(point_no, cond_idx) {
        this.selectPoint(point_no);
        if (sUnitsH.postAction(
                'sDecisionTree.editCond(' + point_no + ', ' + cond_idx + ');'))
            return;
        if (this.mCurPointNo != point_no)
            return
        var point = this.mPoints[point_no];
        this.mOpCond = point[2];
        if (cond_idx >= 0)
            this.mOpCond = this.mOpCond[cond_idx];
        this.mOpIdx = cond_idx;
        this._highlightCondition(true);
        sOpCondH.show(this.mOpCond);
    },

    _highlightCondition(mode) {
        if (this.mOpIdx == null)
            return;
        if (this.mOpIdx >= 0)
            cond_el = document.getElementById("p_cond__" + 
                this.mCurPointNo + "_" + this.mOpIdx);
        else
            cond_el = document.getElementById("p_cond__" + this.mCurPointNo);
        if (mode)
            cond_el.className += " active";
        else
            cond_el.className = cond_el.className.replace(" active", "");
    },
    
    fixCondition: function(new_cond) {
        if (this.mOpIdx == null)
            return;
        sTreeCtrlH.fixCurrent();
        if (this.mOpIdx >= 0) {
            this.mPoints[this.mCurPointNo][2][this.mOpIdx] = new_cond;
        } else {
            this.mPoints[this.mCurPointNo][2] = new_cond;
        }
        this.setup(true);
    },
    
    getAcceptedCount: function() {
        return this.mStat[1];
    },
    
    getTotalCount: function() {
        return this.mStat[0];
    }
}

/**************************************/
var sUnitsH = {
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,
    mWaiting: false,
    mPostAction: null,
    
    setup: function(decision_tree, point_no) {
        args = "ds=" + sDSName + "&tree=" +
            encodeURIComponent(JSON.stringify(decision_tree)) + 
            "&no=" + point_no;
        this.mWaiting = true;
        document.getElementById("_body").className = "wait";
        document.getElementById("stat-list").className = "wait";
        document.getElementById("list-report").innerHTML = 
            '<marquee behavior="alternate" direction="right">| - | -</marquee>';
        ajaxCall("xlstat", args, function(info){sUnitsH._setup(info);})
    },

    postAction: function(action) {
        if (this.mWaiting) {
            this.mPostAction = action;
            return true;
        }
        return false;
    },
    
    _setup: function(info) {
        document.getElementById("_body").className = "";
        document.getElementById("stat-list").className = "";
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
        
        var post_action = this.mPostAction;
        this.mWaiting = false;
        this.mPostAction = null;
        if (post_action)
            eval(post_action);
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
    
    getUnitStat: function(unit_name) {
        return this.mItems[this.mUnitMap[unit_name]];
    },
    
    selectUnit: function(stat_unit, force_it) {
    }
    
};
    
/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mNewCondition: null,
    mButtonSet: null,

    init: function() {
        this.mButtonSet   = document.getElementById("cond-button-set");
    },
    
    show: function(condition) {
        this.mCondition = condition;
        this.mNewCondition = null;
        unit_name = this.mCondition[1];
        document.getElementById("cond-title").innerHTML = unit_name;
        unit_stat = sUnitsH.getUnitStat(unit_name);
        unit_type = unit_stat[0];
        if (unit_type == "long" || unit_type == "float") {
            sOpEnumH.suspend();
            this.mCurTpHandler = sOpNumH;
            mode = "num";
        } else {
            sOpNumH.suspend();
            this.mCurTpHandler = sOpEnumH;
            mode = "enum";
        }
        this.mCurTpHandler.updateUnit(unit_stat);
        this.mCurTpHandler.updateCondition(this.mCondition);
        this.mCurTpHandler.checkControls();
        document.getElementById("cur-cond-mod").className = mode;
        sViewH.modalOn(document.getElementById("cur-cond-back"), "flex");
    },
    
    formCondition: function(condition_data, error_msg, cond_mode, add_always) {
        if (condition_data != null) {
            cur_unit_name = this.mCondition[1];
            this.mNewCondition = [this.mCurTpHandler.getType(), cur_unit_name].concat(
                    condition_data);
        } else
            this.mNewCondition = null;
        document.getElementById("cond-error").innerHTML = (error_msg)? error_msg:"";
        this.mButtonSet.disabled = (condition_data == null);
    },
    
    fixCondition: function() {
        if (this.mNewCondition && this.mNewCondition != this.mCondition)
            sDecisionTree.fixCondition(this.mNewCondition);
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
        this.mInfo.val_cur = null;
        if (this.mInfo.op == 0) {
            val = toNumeric(this.mInfo.unit_type, this.mInputMin.value);
            if (val != null) {
                if (val > this.mInfo.val_max) {
                    error_msg = "Incorrrect lower bound";
                } else {
                    if (val < this.mInfo.val_min) {
                        error_msg = "Lower bound is above minimal value";
                    }
                    this.mInfo.val_cur = val;
                }
            }
            else {
                error_msg = "Bad numeric value";
            }
            this.mInputMin.className = (error_msg == null)? "num-inp":"num-inp bad";
        } 
        if (this.mInfo.op == 1) {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value);
            if (val != null) {
                if (val < this.mInfo.val_min) {
                    error_msg = "Incorrrect upper bound";
                } else {
                    if (val > this.mInfo.val_max) {
                        error_msg = "Upper bound is below maximum value";
                    }
                    this.mInfo.val_cur = val;
                }
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

/**************************************/
var sTreeCtrlH = {
    mHistory: [],
    mRedoStack: [],
    mCurVersion: "",
    
    mButtonUndo: null,
    mButtonRedo: null,
    mButtonSaveVersion: null,
    mSpanCurVersion: null,

    init: function() {
        this.mButtonUndo = document.getElementById("tree-undo");
        this.mButtonRedo = document.getElementById("tree-redo");
        this.mButtonSaveVersion = document.getElementById("tree-version");
        this.mSpanCurVersion = document.getElementById("tree-current-version");
        
    },
    
    update: function(cur_version, versions) {
        sVersionsH.setup(cur_version, versions);
        this.mCurVersion = (cur_version != null)? cur_version + "": "";
        this.mSpanCurVersion.innerHTML = this.mCurVersion;
        this.mButtonUndo.disabled = (this.mHistory.length == 0);
        this.mButtonRedo.disabled = (this.mRedoStack.length == 0);
        this.mButtonSaveVersion.disabled = (cur_version != null);
    },
    
    getCurVersion: function() {
        return this.mCurVersion;
    },
    
    _evalCurState: function() {
        return [sDecisionTree.mCurPointNo,
            JSON.stringify(sDecisionTree.mTree)];
    },
    
    fixCurrent: function() {
        this.mHistory.push(this._evalCurState());
        while (this.mHistory.length > 50)
            this.mHistory.shift();
        this.mRedoStack = [];
    },

    doUndo: function() {
        if (this.mHistory.length > 0) {
            this.mRedoStack.push(this._evalCurState());
            state = this.mHistory.pop()
            sDecisionTree.mCurPointNo = state[0];
            sDecisionTree.setup(state[1]);
        }
    },

    doRedo: function() {
        if (this.mRedoStack.length > 0) {
            this.mHistory.push(this._evalCurState());
            state = this.mRedoStack.pop()
            sDecisionTree.mCurPointNo = state[0];
            sDecisionTree.setup(state[1]);
        }
    },
    
    curVersionSaved: function() {
        return !!this.mCurVersion;
    },
    
    doSaveVersion: function() {
        if (!this.mCurVersion)
            sDecisionTree.setup(true, null, "add_version");
    },
    
    availableActions: function() {
        var ret = [];
        if (this.mHistory.length > 0)
            ret.push("undo");
        if (this.mRedoStack.length > 0)
            ret.push("redo");
        return ret;
    },
    
    _updateConditions: function(new_seq, filter_name) {
        this.mHistory.push(
            [this.mCurFilter, sConditionsH.getConditions()]);
        this.mRedoStack = [];
        sUnitsH.setup(new_seq, filter_name);
    },

    modify: function(action) {
        if (action == "undo") {
            if (this.mHistory.length > 0) {
                this.mRedoStack.push(
                    [this.mCurFilter, sConditionsH.getConditions()]);
                hinfo = this.mHistory.pop();
                sUnitsH.setup(hinfo[1], hinfo[0]);
                this._onChangeFilter();
            }
        }
        if (action == "redo") {
            if (this.mRedoStack.length > 0) {
                this.mHistory.push(
                    [this.mCurFilter, sConditionsH.getConditions()]);
                hinfo = this.mRedoStack.pop();
                sUnitsH.setup(hinfo[1], hinfo[0]);
                this._onChangeFilter();
            }
        }        
    }
};

/**************************************/
var sVersionsH = {
    mVersions: null,
    mBaseCmpVer: null,
    mCurCmpVer: null,
    
    mDivVersionTab: null,
    mDivVersionCmp: null,
    mButtonVersionSelect: null,
    mButtonVersionDelete: null,
    
    init: function() {
        this.mDivVersionTab = document.getElementById("versions-tab");
        this.mDivVersionCmp = document.getElementById("versions-cmp");
        this.mButtonVersionSelect = document.getElementById("btn-version-select");
        this.mButtonVersionDelete = document.getElementById("btn-version-delete");
    },
    
    setup: function(cur_version, versions) {
        if (versions == null)
            versions = [];
        this.mBaseCmpVer = cur_version;
        this.mVersions= versions;
        this.mCurCmpVer = null;
        rep = ['<table id="ver-tab">'];
        if (this.mBaseCmpVer == null)
            rep.push('<tr class="v-base"><td class="v-no">&lt;&gt;</td>' +
                '<td class="v-date"></td></tr>');
        for (var idx = versions.length - 1; idx >= 0; idx--) {
            if (versions[idx][0] == this.mBaseCmpVer) 
                rep.push('<tr class="v-base">');
            else {
                rep.push('<tr class="v-norm" id="ver__' + versions[idx][0] + '" ' + 
                    'onclick="sVersionsH.selIt(' + versions[idx][0] + ')">');
            }
            date_repr = Date(versions[idx][1]).toLocaleString("en-US").
                replace(/GMT.*/i, "");
            rep.push('<td class="v-no">' + versions[idx][0] + '</td>' +
                '<td class="v-date">' + date_repr + '</td></tr>');
        }
        rep.push('</table>');
        this.mDivVersionTab.innerHTML = rep.join('\n');
        this.mDivVersionCmp.innerHTML = "";
        this.mDivVersionCmp.className = "empty";
        this.checkControls();
    },
            
    show: function() {
        if (this.mVersions.length > 1 || 
                (this.mVersions.length == 1 && this.mBaseCmpVer == null))
            sViewH.modalOn(document.getElementById("versions-back"));
    },
    
    checkControls: function(){
        this.mButtonVersionSelect.disabled = (this.mCurCmpVer == null);
        this.mButtonVersionDelete.disabled = true;
    },
    
    selIt: function(ver_no) {
        if (ver_no == this.mCurCmpVer)
            return;
        if (this.mCurCmpVer != null) {
            prev_el = document.getElementById("ver__" + this.mCurCmpVer);
            prev_el.className = prev_el.className.replace(" cur", "");
        }
        this.mCurCmpVer = ver_no;
        if (this.mCurCmpVer != null) {
            new_el = document.getElementById("ver__" + this.mCurCmpVer);
            new_el.className += " cur";
        }
        this.checkControls();
        
        if (this.mCurCmpVer != null) {
            args = "ds=" + sDSName + "&ver=" + this.mCurCmpVer;
            if (this.mBaseCmpVer == null) 
                args += "&tree=" + encodeURIComponent(
                    JSON.stringify(sDecisionTree.mTree));
            else
                args += "&verbase=" + this.mBaseCmpVer;
            ajaxCall("cmptree", args, function(info){sVersionsH._setCmp(info);});
        }
    },
    
    _setCmp: function(info) {
        if (!info["cmp"]) {
            this.mDivVersionCmp.innerHTML = "";
            this.mDivVersionCmp.className = "empty";
        } else {
            rep = [];
                        
            for (var j = 0; j < info["cmp"].length; j++) {
                block = info["cmp"][j];
                cls_name = "cmp";
                sign = block[0][0];
                if (sign == "+") 
                    cls_name += " plus";
                if (sign == "-")
                    cls_name += " minus";
                if (sign == '?')
                    cls_name += " note";
                rep.push('<div class="' + cls_name + '">' + 
                    escapeText(block.join('\n')) + '</div>');
            }
            this.mDivVersionCmp.innerHTML = rep.join('\n');
            this.mDivVersionCmp.className = "";
        }
    },
    
    selectVersion: function() {
        if (this.mCurCmpVer != nsull) {
            sViewH.modalOff();
            sDecisionTree.setup(false, this.mCurCmpVer);
        }
        
    },
    
    deleteVersion: function() {
        //TRF: write it later!!!
    }
};

/**************************************/
var sCreateWsH = {
    mStage: null,
    mDSNames: null,
    mSpanModTitle: null,
    mInputModName: null,
    mDivModProblems: null,
    mDivModStatus: null,
    mButtonModStart: null,
    mTaskId: null,
    mTimeH: null,
    
    init: function() {
        this.mSpanModTitle = document.getElementById("create-ws-title");
        this.mInputModName = document.getElementById("create-ws-name");
        this.mDivModProblems = document.getElementById("create-ws-problems");
        this.mDivModStatus = document.getElementById("create-ws-status");
        this.mButtonModStart = document.getElementById("create-ws-start");
    },
    
    show: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDSNames = null;
        this.mTaskId = null;
        this.mSpanModTitle.innerHTML = 'Create workspace for ' +
            sDecisionTree.getAcceptedCount() + ' of ' + 
            sDecisionTree.getTotalCount();
        var error_msg = "";
        if (!sTreeCtrlH.curVersionSaved())
            error_msg = "Save current version before";
        if (sDecisionTree.getAcceptedCount() >= 5000)
            error_msg = "Too many records, try to reduce";
        if (sDecisionTree.getAcceptedCount() < 10)
            error_msg = "Too small workspace";
        this.mDivModProblems.innerHTML = error_msg;
        if (error_msg) {
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
        this.mDSNames = [];
        for (idx = 0; idx < dirinfo["xl-datasets"].length; idx++)
            this.mDSNames.push(dirinfo["xl-datasets"][idx]["name"]);
        for (idx = 0; idx < dirinfo["workspaces"].length; idx++)
            this.mDSNames.push(dirinfo["workspaces"][idx]["name"]);
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
        error_msg = "";
        if (this.mStage == "READY") {
            if (this._nameReserved(this.mInputModName.value)) 
                error_msg = "Name is reserved, try another one";
            this.mDivModProblems.innerHTML = error_msg;
        }
        this.mButtonModStart.disabled = (this.mStage != "READY" || error_msg);
        if (this.mStage == "BAD" || this.mStage == "READY") {
            this.mDivModProblems.style.display = "block";
            this.mDivModStatus.style.display = "none";
            this.mDivModStatus.innerHTML = "";
        } else {
            this.mDivModProblems.style.display = "none";
            this.mDivModStatus.style.display = "block";
        }
    },
    
    startIt: function() {
        if (this.mStage != "READY")
            return;
         this.checkControls();
        if (this.mButtonModStart.disabled)
            return;
        sViewH.blockModal(true);
        this.mStage = "WAIT";
        ajaxCall("xl2ws", "ds=" + sDSName + "&verbase= " + 
            sTreeCtrlH.getCurVersion() + "&ws=" + 
            encodeURIComponent(this.mInputModName.value),
            function(info) {
                sCreateWsH._setupTask(info);})
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
        if (info[0] == false) {
            this.mDivModStatus.innerHTML = info[1];
            if (this.mTimeH == null)
                this.mTimeH = setInterval(function() {sCreateWsH.checkTask()}, 300);
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
        if (info[0] == null) {
            this.mDivModStatus.innerHTML = info[1];
        } else {
            this.mDivModStatus.innerHTML = 'Done: <a href="ws?ws=' + 
                info[0]["ws"] + '" target="' + sTitlePrefix + '/' + 
                info[0]["ws"] + '">Open it</a>';
        }
    }
};

/*************************************/
/* Top controls                      */
/*************************************/
var sViewH = {
    mShowToDrop: null,
    mDropCtrls: [],
    mModalCtrls: [],
    mBlock: false,
    
    init: function() {
        window.onclick = function(event_ms) {sViewH.onclick(event_ms);}
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
    
    modalOn: function(ctrl, disp_mode) {
        this.mBlock = false;
        if (this.mModalCtrls.indexOf(ctrl) < 0)
            this.mModalCtrls.push(ctrl);
        this.modalOff();
        ctrl.style.display = (disp_mode)? disp_mode: "block";
    },
    
    modalOff: function() {
        if (this.mBlock)
            return;
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            this.mModalCtrls[idx].style.display = "none";
        }
    },
    
    blockModal: function(mode) {
        this.mBlock = mode;
        document.getElementById("_body").className = (mode)? "wait":"";
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

function modalOff() {
    sViewH.modalOff();
}

function fixCond() {
    sViewH.modalOff();
    sOpCondH.fixCondition();
}

function treeUndo() {
    sTreeCtrlH.doUndo();
}

function treeRedo() {
    sTreeCtrlH.doRedo();
}

function treeVersionSave() {
    sTreeCtrlH.doSaveVersion();
}

function modVersions() {
    sVersionsH.show();
}

function versionSelect() {
    sVersionsH.selectVersion();
}

function versionDelete() {
    sVersionsH.deleteVersion();
}

function wsCreate() {
    sCreateWsH.show();
}


function startWsCreate() {
    sCreateWsH.startIt();
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