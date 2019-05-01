var sDSName = null;
var sTitlePrefix = null;
var sCommonTitle = null;
var sWsURL = null;

/*************************************/
function initXL(ds_name, common_title, ws_url) {
    sOpCondH.init();
    sOpNumH.init();
    sOpEnumH.init();
    sTreeCtrlH.init();
    sVersionsH.init();
    sViewH.init();
    sCreateWsH.init();
    sCodeEdit.init();
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    sCommonTitle = common_title;
    sWsURL = ws_url;
    sDSName = ds_name; 
    window.name = sCommonTitle + ":" + sDSName + ":L";
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
    mTreeCode: null,
    mPoints: null,
    mMarkers: null,
    mCounts: null,
    mTotalCount: null,
    mAcceptedCount: null,
    mCurPointNo: null,
    mOpCond: null,
    mMarkLoc: null,
    
    setup: function(tree_code, options) {
        args = "ds=" + sDSName;
        if (tree_code) {
            if (tree_code == true)
                tree_code = this.mTreeCode;
            args += "&code=" + encodeURIComponent(tree_code);
        }
        if (options) {
            if (options["version"])
                args += "&version=" + encodeURIComponent(options["version"]);
            if (options["instr"])
                args += "&instr=" + encodeURIComponent(JSON.stringify(options["instr"]));
            if (options["std"])
                args += "&std=" + encodeURIComponent(options["std"]);
        }
        ajaxCall("xltree", args, function(info){sDecisionTree._setup(info);})
    },
    
    _setup: function(info) {
        this.mTreeCode = info["code"];
        this.mTotalCount = info["total"];
        this.mCounts = info["counts"];
        this.mPoints = info["points"];
        this.mMarkers = info["markers"];
        sTreeCtrlH.update(info["cur_version"], info["versions"]);
        document.getElementById("std-code-select").value = 
            info["std_code"]? info["std_code"]:"";
        this.mAcceptedCount = 0;
        this.mMarkLoc = null;
        var list_rep = ['<table class="d-tree">'];
        for (var p_no = 0; p_no < this.mPoints.length; p_no++) {
            point = this.mPoints[p_no];
            p_kind = point[0];
            p_lev = point[1];
            p_decision = point[2];
            p_cond = point[3];
            p_html = point[4];
            p_count = this.mCounts[p_no];
            if (p_count > 0) {
                list_rep.push('<tr id="p_td__' + p_no + 
                    '" class="active" onclick="sDecisionTree.selectPoint(' + 
                    p_no + ');">');
            } else {
                list_rep.push('<tr>');
            }
            list_rep.push('<td class="point-no" id="p_no__' + p_no + '">' + 
                (p_no + 1) + '</td>');
            list_rep.push('<td class="point-code"><div class="highlight">' +
                p_html + '</div></td>');
            if (p_decision) {
                this.mAcceptedCount += p_count;
                list_rep.push('<td class="point-count-accept">+' + p_count + '</td>');
            } else {
                if (p_decision == false) 
                    list_rep.push(
                        '<td class="point-count-reject">-' + p_count + '</td>');
                else 
                    list_rep.push(
                        '<td class="point-count">' + p_count + '</td>');
            }
            list_rep.push('</tr>');
        }
        list_rep.push('</table>'); 
        document.getElementById("decision-tree").innerHTML = list_rep.join('\n');
        point_no = (this.mCurPointNo)? this.mCurPointNo: 0;
        while (point_no > 0) {
            if (point_no >= this.mPoints.length || this.mCounts[point_no] == 0)
                point_no--;
            else
                break;
        }
        this.mCurPointNo = null;
        this.selectPoint(point_no);
        
        document.getElementById("report-accepted").innerHTML = "" + 
            (this.mAcceptedCount);
        rep_rejected = this.mTotalCount - this.mAcceptedCount;
        document.getElementById("report-rejected").innerHTML = rep_rejected;
    },
    
    selectPoint: function(point_no) {
        if (this.mCurPointNo == point_no) 
            return;
        if (this.mCounts[point_no] == 0)
            return;
        if (sUnitsH.postAction(
            'sDecisionTree.selectPoint(' + point_no + ');', true))
            return;
        sViewH.modalOff();
        this._highlightCondition(false);
        this.mOpCond = null;
        this.mMarkLoc = null;
        var new_el = document.getElementById("p_td__" + point_no);
        if (new_el == null) 
            return;
        if (this.mCurPointNo != null) {
            var prev_el = document.getElementById("p_td__" + this.mCurPointNo);
            prev_el.className = "active";
        }
        this.mCurPointNo = point_no;
        new_el.className = "cur";
        sCodeEdit.setup(this.mTreeCode);
        sUnitsH.setup(this.mTreeCode, this.mCurPointNo);
    },
    
    markEdit: function(point_no, marker_idx) {
        this.selectPoint(point_no);
        if (sUnitsH.postAction(
                'sDecisionTree.markEdit(' + point_no + ', ' + marker_idx + ');', true))
            return;
        if (this.mCurPointNo != point_no)
            return
        this.mOpCond = this.mMarkers[point_no][marker_idx];
        this.mMarkLoc = [point_no, marker_idx];
        sOpCondH.show(this.mOpCond);
        this._highlightCondition(true);
    },

    _highlightCondition(mode) {
        if (this.mMarkLoc == null)
            return;
        mark_el = document.getElementById(
            '__mark_' + this.mMarkLoc[0] + '_' + this.mMarkLoc[1]);
        if (mode)
            mark_el.className += " active";
        else
            mark_el.className = mark_el.className.replace(" active", "");
    },
    
    editMarkCond: function(new_cond) {
        if (this.mMarkLoc == null)
            return;
        sTreeCtrlH.fixCurrent();
        this.setup(true, {"instr": ["mark", this.mMarkLoc, new_cond]});
    },
    
    getAcceptedCount: function() {
        return this.mAcceptedCount;
    },
    
    getTotalCount: function() {
        return this.mTotalCount;
    }
}

/**************************************/
var sUnitsH = {
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,
    mWaiting: false,
    mPostAction: null,
    
    setup: function(tree_code, point_no) {
        args = "ds=" + sDSName + "&code=" +
            encodeURIComponent(tree_code) + 
            "&no=" + point_no;
        this.mWaiting = true;
        document.body.className = "wait";
        document.getElementById("stat-list").className = "wait";
        document.getElementById("list-report").innerHTML = 
            '<marquee behavior="alternate" direction="right">| - | -</marquee>';
        ajaxCall("xlstat", args, function(info){sUnitsH._setup(info);})
    },

    postAction: function(action, no_wait) {
        if (!no_wait || this.mWaiting) {
            if (this.mPostAction) 
                this.mPostAction += "\n" + action;
            else
                this.mPostAction = action;
            return true;
        }
        return false;
    },
    
    _setup: function(info) {
        document.body.className = "";
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
            if (unit_type == "zygosity")
                continue;
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
        //cnt_undef = unit_stat[5];
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
    
    formCondition: function(condition_data, err_msg, cond_mode, add_always) {
        if (condition_data != null) {
            cur_unit_name = this.mCondition[1];
            this.mNewCondition = [this.mCurTpHandler.getCondType(), 
                cur_unit_name].concat(condition_data);
        } else
            this.mNewCondition = null;
        message_el = document.getElementById("cond-message");
        message_el.innerHTML = (err_msg)? err_msg:"";
        message_el.className = (this.mNewCondition == null && 
            !err_msg.startsWith(' '))? "bad":"message";
        this.mButtonSet.disabled = (condition_data == null);
    },
    
    editMarkCond: function() {
        if (this.mNewCondition && this.mNewCondition != this.mCondition)
            sDecisionTree.editMarkCond(this.mNewCondition);
    },
    
    careControls: function() {
    }
};

/**************************************/
var sOpNumH = {
    mInfo: null,
    mInputMin: null,
    mInputMax: null,    
    mUpdateCondStr: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
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
            cur_bounds: [null, null],
            unit_type:  unit_stat[0],
            val_min:    unit_stat[2],
            val_max:    unit_stat[3],
            count:      unit_stat[4]}
            
        document.getElementById("cond-min").innerHTML = this.mInfo.val_min;
        document.getElementById("cond-max").innerHTML = this.mInfo.val_max;
        document.getElementById("cond-sign").innerHTML = 
            (this.mInfo.val_min == this.mInfo.val_max)? "=":"&le;";
        this.mInputMin.value = "";
        this.mInputMax.value = "";
    },

    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        this.mInfo.cur_bounds   = [cond[2][0], cond[2][1]];
        this.mInputMin.value = (this.mInfo.cur_bounds[0] != null)?
            this.mInfo.cur_bounds[0] : "";
        this.mInputMax.value = (this.mInfo.cur_bounds[1] != null)?
            this.mInfo.cur_bounds[1] : "";
        document.getElementById("cond-sign").innerHTML = "&le;";
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
            this.mInfo.cur_bounds[1] = null;
            this.mInputMax.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value)
            this.mInputMax.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                err_msg = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[1] = val;
            }
        }
        if (err_msg == null) {
            if (this.mInfo.cur_bounds[0] == null && 
                    this.mInfo.cur_bounds[1] == null)
                err_msg = "";            
            if (this.mInfo.cur_bounds[0] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[0] > this.mInfo.val_max)
                err_msg = "Lower bound is above maximum value";
            if (this.mInfo.cur_bounds[1] != null && !this.mUpdateCondStr && 
                    this.mInfo.cur_bounds[1] < this.mInfo.val_min)
                err_msg = "Upper bound is below minimum value";
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[1] != null && 
                    this.mInfo.cur_bounds[0] > this.mInfo.cur_bounds[1])
                err_msg = "Bounds are mixed up";
        }

        condition_data = null;
        if (err_msg == null) {
            condition_data = [this.mInfo.cur_bounds, null]
            if (this.mInfo.cur_bounds[0] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[0] < this.mInfo.val_min)
                err_msg = "Lower bound is below minimal value";
            if (this.mInfo.cur_bounds[1] != null &&  !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[1] > this.mInfo.val_max)
                err_msg = "Upper bound is above maximal value";
        }
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }
        sOpCondH.formCondition(
            condition_data, err_msg, this.mInfo.op, false);
        this.careControls();
    }
};

/**************************************/
var sOpEnumH = {
    mVariants: null,
    mOperationMode: null,
    mDivVarList: null,
    mUpdateCondStr: null,

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
        this.mUpdateCondStr = null;
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
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
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
        var err_msg = null;
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
            err_msg = "";
        } else
            err_msg = " Empty selection"
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
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
        return [sDecisionTree.mCurPointNo, sDecisionTree.mTreeCode];
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
            sDecisionTree.setup(true, {"instr": ["add_version"]});
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
            rep.push('<td class="v-no">' + versions[idx][0] + '</td>' +
                '<td class="v-date">' + timeRepr(versions[idx][1]) + '</td></tr>');
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
                args += "&code=" + encodeURIComponent(sDecisionTree.mTreeCode);
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
        if (this.mCurCmpVer != null) {
            sViewH.modalOff();
            sDecisionTree.setup(null, {"version": this.mCurCmpVer});
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
        this.mSpanModTitle.innerHTML = 'Create workspace for ' +
            sDecisionTree.getAcceptedCount() + ' of ' + 
            sDecisionTree.getTotalCount();
        var err_msg = "";
        if (sDecisionTree.getAcceptedCount() >= 5000)
            err_msg = "Too many records, try to reduce";
        if (sDecisionTree.getAcceptedCount() < 10)
            err_msg = "Too small workspace";
        if (!sTreeCtrlH.curVersionSaved()) {
            sUnitsH.postAction("sCreateWsH.show();");
            treeVersionSave();
            return;
        }
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
        ajaxCall("xl2ws", "ds=" + sDSName + "&verbase= " + 
            sTreeCtrlH.getCurVersion() + "&ws=" + 
            encodeURIComponent(this.mInputModName.value),
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
                target_ref = (sWsURL != "ws")? '': (' target="' + 
                    sTitlePrefix + '/' + info[0]["ws"] + '"'); 
                this.mDivModStatus.innerHTML = 'Done: <a href="' + sWsURL + 
                    '?ws=' +  info[0]["ws"] + '"' + target_ref + '>Open it</a>';
            }
        }
    }
};

/*************************************/
var sCodeEdit = {
    mBaseContent: null,
    mCurContent: null,
    mCurError: null,
    mButtonShow: null,
    mButtonDrop: null,
    mSpanError: null,
    mAreaContent: null,
    
    init: function() {
        this.mButtonShow = document.getElementById("code-edit-show");
        this.mButtonDrop = document.getElementById("code-edit-drop");
        this.mSpanError = document.getElementById("code-edit-error");
        this.mAreaContent = document.getElementById("code-edit-content");
    },
    
    setup: function(tree_code) {
        this.mBaseContent = tree_code;
        this.mAreaContent.value = this.mBaseContent;
        this.mCurContent = this.mBaseContent;
        this.mCurError = false;
        this.validateContent(this.mBaseContent);
    },
    
    checkControls: function() {
        this.mButtonShow.text = (this.mCurError != null)? 
            "Continue edit code" : "Edit code"; 
        this.mButtonDrop.disabled = (this.mCurContent != this.mBaseContent);
        this.mSpanError.innerHTML = (this.mCurError)? this.mCurError:"";
    },
    
    show: function() {
        sViewH.modalOn(document.getElementById("code-edit-back"));
    },

    validateContent: function(content) {
        if (this.mCurError != false && this.mCurContent == content)
            return;
        this.mCurContent = content;
        this.mCurError = false;
        ajaxCall("xltree_code", "ds=" + sDSName + "&code=" +
            encodeURIComponent(this.mCurContent), 
            function(info){sCodeEdit._validation(info);});
    },
    
    _validation: function(info) {
        if (info["code"] != this.mCurContent) 
            return;
        if (info["error"]) {
            this.mCurError = "At line " + info["line"] + " pos " + info["pos"] + ": " +
                info["error"];
        } else {
            this.mCurError = null;
        }
        this.checkControls();
    },
    
    drop: function() {
        this.mAreaContent.value = this.mBaseContent;
        this.validateContent(this.mBaseContent);
        sViewH.modalOff();
    },
    
    checkContent: function() {
        this.validateContent(this.mAreaContent.value);
    }, 
    
    relax: function() {
        if (this.mCurError == null && this.mBaseContent != this.mCurContent)
            sDecisionTree.setup(this.mCurContent);
        this.checkControls();
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
        sDecisionTree._highlightCondition(false);
        sCodeEdit.relax();
    },
    
    blockModal: function(mode) {
        this.mBlock = mode;
        document.body.className = (mode)? "wait":"";
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

function goToFilters() {
    sViewH.dropOff();
    window.open("xl_flt?ds=" + sDSName, sCommonTitle + ":" + sDSName + ":R");
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
        document.getElementById("note-ds-name").innerHTML = info["name"];
        document.getElementById("note-content").value = info["note"];
        document.getElementById("note-time").innerHTML = 
            (info["time"] == null)? "" : "Modified at " + timeRepr(info["time"]);
    });
}

function modalOff() {
    sViewH.modalOff();
}

function fixMark() {
    sOpCondH.editMarkCond();
    sViewH.modalOff();
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

function editMark(point_no, instr_idx) {
    sDecisionTree.markEdit(point_no, instr_idx);
}

function pickStdCode() {
    std_name = document.getElementById("std-code-select").value;
    if (std_name) 
        sDecisionTree.setup(null, {"std" : std_name});
}