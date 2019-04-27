var sDSName = null;
var sTitlePrefix = null;
var sCommonTitle = null;
var sWsURL = null;

/*************************************/
function initXL(ds_name, common_title, ws_url) {
    sFiltersH.init();
    sOpNumH.init();
    sOpEnumH.init();
    sViewH.init();
    sCreateWsH.init()
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    sCommonTitle = common_title;
    sWsURL = ws_url;
    sDSName = ds_name; 
    window.name = sCommonTitle + ":" + sDSName + ":R";
    document.title = sTitlePrefix + "/" + sDSName;
    document.getElementById("xl-name").innerHTML = sDSName;
    sUnitsH.setup();
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
var sUnitsH = {
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,
    mCurZygName: null,
    mCounts: null,
    mTotal: null,
    mExportFormed: null,
    mCtx: null,
    
    setup: function(conditions, filter_name, add_instr) {
        args = "ds=" + sDSName;
        if (filter_name) {
            args += "&filter=" + encodeURIComponent(filter_name);
        } else {
            if (conditions)
                args += "&conditions=" + 
                    encodeURIComponent(JSON.stringify(conditions)); 
        }
        if (this.mCtx != null)
            args += "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
        if (add_instr)
            args += "&" + add_instr[0] + "=" + encodeURIComponent(add_instr[1]);
        ajaxCall("xl_filters", args, function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        this.mCount = info["count"];
        this.mTotal = info["total"];
        this.mExportFormed = false;
        sCreateWsH.reset();
        document.getElementById("list-report").innerHTML = 
            (this.mCount == this.mTotal)? 
                this.mTotal : this.mCount + "/" + this.mTotal;

        this.mCtx = null;
        this.mItems = info["stat-list"];
        sOpFilterH.update(info["cur-filter"], info["filter-list"]);
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
            if (false && unit_name == "Rules") {
                list_stat_rep.push(
                    '<span id="flt-run-rules" title="Rules evaluation setup" ' +
                    ' onclick="rulesModOn();">&#9874;</span>')
            }
            if (unit_type == "zygosity") 
                sZygosityH.setup(unit_stat, list_stat_rep);
            else {
                if (unit_type == "long" || unit_type == "float") {
                    this._fillStatRepNum(unit_stat, list_stat_rep);
                } else {
                    this._fillStatRepEnum(unit_stat, list_stat_rep);
                }
            }
            list_stat_rep.push('</div>')
        }
        if (group_title != false) {
            list_stat_rep.push('</div>')
        }
        document.getElementById("stat-list").innerHTML = list_stat_rep.join('\n');
        
        this.mCurUnit = null;
        this.mCurZygName = null;
        sConditionsH.setup(info["conditions"]);
        
        if (this.mCurUnit == null)
            this.selectUnit(this.mItems[0][1]["name"]);
        sFiltersH.update();
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
    
    getCurUnitTitle: function() {
        return (this.mCurZygName == null)? this.mCurUnit: this.mCurZygName;
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
        this.mCurZygName = sZygosityH.checkUnitTitle(stat_unit);
        new_unit_el.className = new_unit_el.className + " cur";
        sConditionsH.correctCurUnit(this.mCurUnit);
        sOpCondH.updateUnit(this.mCurUnit);
    },
    
    updateZygUnit: function(zyg_name) {
        if (this.mCurZygName != null) {
            this.mCurZygName = zyg_name;
            this.selectUnit(this.mCurUnit, true);
        }
    },
    
    setCtx: function(ctx) {
        this.mCtx = ctx;
    }
    
};

/**************************************/
var sOpFilterH = {
    mCurFilter: "",
    mHistory: [],
    mRedoStack: [],

    update: function(filter_name, filter_list) {
        this.mCurFilter = (filter_name)? filter_name:"";
        var all_filters = sFiltersH.setup(filter_list)
        for (idx = 0; idx < this.mHistory.length; idx++) {
            hinfo = this.mHistory[idx];
            if (hinfo[0] != "" && all_filters.indexOf(hinfo[0]) < 0)
                hinfo[0] = "";
        }
        for (idx = 0; idx < this.mRedoStack.length; idx++) {
            hinfo = this.mRedoStack[idx];
            if (hinfo[0] != "" && all_filters.indexOf(hinfo[0]) < 0)
                hinfo[0] = "";
        }
        if (this.mCurFilter != "" && 
                all_filters.indexOf(this.mCurFilter) < 0)
            this.mCurFilter = "";
    },
    
    _onChangeFilter: function() {
    },
    
    getCurFilterName: function() {
        return this.mCurFilter;
    },
    
    availableActions: function() {
        var ret = sOpCondH.availableActions();
        if (sConditionsH.getCurCondNo() != null)
            ret.push("delete");
        if (!sConditionsH.isEmpty())
            ret.push("clear-all");
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
        this._onChangeFilter();
    },

    modify: function(action) {
        if (action == "add" || action == "update") {
            new_seq = sOpCondH.applyCondition(
                sConditionsH.getConditions(), action);
            if (new_seq != null)
                this._updateConditions(new_seq);
        }
        if (action == "delete") {
            cond_no = sConditionsH.getCurCondNo();
            if (cond_no != null) {
                new_seq = sConditionsH.getConditions().slice();
                new_seq.splice(cond_no, 1);
                this._updateConditions(new_seq);
            }
        }
        if (action == "clear-all") {
            if (!sConditionsH.isEmpty()) {
                this._updateConditions([]);
            }
        }
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
var sConditionsH = {
    mList: [],
    mCurNo: null,

    setup: function(cond_list) {
        this.mList = (cond_list)? cond_list:[];
        var list_cond_rep = [];
        for (idx = 0; idx < this.mList.length; idx++) {
            cond = this.mList[idx];
            list_cond_rep.push('<div id="cond--' + idx + '" class="cond-descr" ' +
                'onclick="sConditionsH.selectCond(\'' + idx + '\');">');
            list_cond_rep.push('&bull;&emsp;' + getCondDescription(cond, false));
            list_cond_rep.push('</div>')
        }
        document.getElementById("cond-list").innerHTML = list_cond_rep.join('\n');
        this.mCurNo = null;
        if (this.mList.length > 0) 
            this.selectCond(this.mList.length - 1);
    },
    
    selectCond: function(cond_no, force_it) {
        if (!force_it && this.mCurNo == cond_no) 
            return;
        if (cond_no != null) {
            new_cond_el = document.getElementById("cond--" + cond_no);
            if (new_cond_el == null) 
                return;
        } else {
            new_cond_el = null;
        }
        if (this.mCurNo != null) {
            var prev_el = document.getElementById("cond--" + this.mCurNo);
            prev_el.className = prev_el.className.replace(" cur", "");
        }
        this.mCurNo = cond_no;
        if (new_cond_el != null) {
            new_cond_el.className = new_cond_el.className + " cur";
            sZygosityH.onSelectCondition(this.mList[cond_no]);
            sUnitsH.selectUnit(this.mList[cond_no][1], true);
        }
    },

    getConditions: function() {
        return this.mList;
    },
    
    getCurCondNo: function() {
        return this.mCurNo;
    },

    getCurCond: function() {
        if (this.mCurNo == null)
            return null;
        return this.mList[this.mCurNo];
    },
    
    correctCurUnit: function(unit_name) {
        if (this.mCurNo == null || this.mList[this.mCurNo][1] != unit_name)
            this.selectCond(this.findCond(unit_name));
    },

    findCond: function(unit_name, cond_mode) {
        for (idx = 0; idx < this.mList.length; idx++) {
            if (this.mList[idx][1] == unit_name) {
                if (cond_mode == undefined || this.mList[idx][2] == cond_mode)
                    return idx;
            }
        }
        return null;
    },
    
    nextIdx: function() {
        return this.mList.length;
    },
    
    isEmpty: function() {
        return this.mList.length == 0;
    },
    
    report: function() { // checkCurConditionsProblem()
        if (this.mList.length == 0)
            return "no conditions";
        if (this.mCurFilter != "")
            return this.mCurFilter + " in work";
        return null;
    }
};

/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mIdxToUpdate: null,
    mIdxToAdd: null,
    
    updateUnit: function() {
        unit_title = sUnitsH.getCurUnitTitle();
        unit_name = sUnitsH.getCurUnitName();
        document.getElementById("cond-title").innerHTML = (unit_title)? unit_title:"";
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
    
    formCondition: function(condition_data, err_msg, cond_mode, add_always) {
        cur_unit_name = sUnitsH.getCurUnitName();
        this.mCondition   = null;
        this.mIdxToAdd    = null;
        this.mIdxToUpdate = null;
        if (condition_data != null) {
            this.mCondition = [this.mCurTpHandler.getCondType(), cur_unit_name].concat(
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
            (this.mCondition)? getCondDescription(this.mCondition, true):"";
        message_el = document.getElementById("cond-message");
        message_el.innerHTML = (err_msg)? err_msg:"";
        message_el.className = (this.mCondition == null && 
            !err_msg.startsWith(' '))? "bad":"message";
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
  
    mActions: ["add", "update", "delete", "undo", "redo", "clear-all"],
    
    careControls: function() {
        var avail_actions = sOpFilterH.availableActions();
        for (var idx = 0; idx < this.mActions.length; idx++) {
            action = this.mActions[idx];
            document.getElementById("filter-" + action + "-cond").disabled = 
                avail_actions.indexOf(action) < 0;
        }
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
        this.mUpdateCondStr = null;
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
            if (this.mInfo.cur_bounds[1] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[1] > this.mInfo.val_max)
                err_msg = "Upper bound is above maximal value";
            if (this.mUpdateCondStr && !err_msg &&    
                    (JSON.stringify(condition_data) == this.mUpdateCondStr)) {
                err_msg = " ";
                condition_data = null;
            }
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
    mSpecCtrl: null,
    mStatusMode: null,
    mUpdateCondStr: null,

    init: function() {
        this.mDivVarList = document.getElementById("op-enum-list");
    },
    
    getCondType: function() {
        if (this.mSpecCtrl != null)
            return this.mSpecCtrl.getCondType();
        return "enum";
    },
    
    suspend: function() {
        this.mVariants = null;
        this.mOperationMode = null;
        this.careControls();
    },

    updateUnit: function(unit_stat) {
        this.mUpdateCondStr = null;
        if (unit_stat[0] == "zygosity") {
            this.mSpecCtrl = sZygosityH;
            this.mVariants = sZygosityH.getVariants(unit_stat);
            this.mOperationMode = null;
            this.mStatusMode = null;
        } else {
            this.mVariants = unit_stat[2];
            this.mOperationMode = 0;
            this.mStatusMode = (unit_stat[0] == "status");
            this.mSpecCtrl = null;
        }
        
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
        if (this.mSpecCtrl != null) {
            this.mSpecCtrl = sZygosityH;
            var_list = this.mSpecCtrl.getCondVarList(cond);
            op_mode = this.mSpecCtrl.getCondOpMode(cond);
        } else {
            var_list = cond[3];
            op_mode = cond[2];
        }
        if (this.mOperationMode != null)
            this.mOperationMode = ["", "AND", "ONLY", "NOT"].indexOf(op_mode);
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
                style.visibility = (this.mOperationMode == null ||
                    (this.mStatusMode && idx != 3))? "hidden":"visible";
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
        if (this.mSpecCtrl != null) {
            condition_data = this.mSpecCtrl.transCondition(condition_data);
            err_msg = this.mSpecCtrl.checkError(condition_data, err_msg);
        }
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }

        sOpCondH.formCondition(condition_data, err_msg, op_mode, true);
        this.careControls();
    }
};

/**************************************/
var sZygosityH = {
    mFamily: null,
    mProblemIdxs: null,
    mUnitName: null,
    mDefaultIdxs: null,
    mZStat: null,
    mZEmpty: null,
    
    setup: function(unit_stat, list_stat_rep) {
        this.mUnitName = unit_stat[1]["name"];
        this.mFamily = unit_stat[1]["family"];
        this.mDefaultIdxs = unit_stat[1]["affected"];
        this.mProblemIdxs = unit_stat[2];
        this.mZStat = unit_stat[3] ;
        if (this.mProblemIdxs == null)
            this.mProblemIdxs = [];
        list_stat_rep.push('<div class="zyg-wrap"><div class="zyg-family">');
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            q_checked = (this.mProblemIdxs.indexOf(idx)>=0)? " checked":"";
            list_stat_rep.push('<div class="zyg-fam-member">' + 
                '<input type="checkbox" id="zyg_fam_m__' + idx + '" ' + q_checked + 
                ' onchange="sZygosityH.checkMember(' + idx + ');" />' +
                this.mFamily[idx] + '</div>');
        }
        if (this.mDefaultIdxs.length > 0) {
            reset_dis = (this.mDefaultIdxs.join(',') == this.mProblemIdxs.join(','))?
                'disabled="true"':'';
            list_stat_rep.push('<button id="zyg_fam_reset" ' +
                'title="Reset affected group" ' + reset_dis + 
                ' onclick="sZygosityH.resetGrp()">Reset</button>');
        }
        list_stat_rep.push('</div><div id="zyg-stat">');
        this._reportStat(list_stat_rep);
        list_stat_rep.push('</div></div>');
        sUnitsH.setCtx({"problem_group": this.mProblemIdxs.slice()})
    },
    
    getCondType: function() {
        return "zygosity";
    },
    
    getVariants: function(unit_stat) {
        return (this.mZStat == null)? []:this.mZStat;
    },
    
    transCondition: function(condition_data) {
        if (condition_data == null)
            return null;
        ret = condition_data.slice();
        ret.splice(0, 0, this.mProblemIdxs.slice());
        return ret;
    },
    
    checkError: function(condition_data, err_msg) {
        if (this.mZStat == null)
            return " Determine problem group";
        if (this.mZEmpty)
            return "Out of choice";
        return err_msg;
    },
    
    getUnitTitle: function(problem_group) {
        if (problem_group == undefined)
            problem_group = this.mProblemIdxs;
        return this.mUnitName + '({' + problem_group.join(',') + '})';        
    },
    
    checkUnitTitle: function(unit_name) {
        if (unit_name != this.mUnitName)
            return null;
        return this.getUnitTitle();
    },
    
    getCondOpMode: function(condition_data) {
        return condition_data[3];
    },
    
    getCondVarList: function(condition_data) {
        return condition_data[4];
    },
    
    onSelectCondition: function(condition_data) {
        if (condition_data[1] != this.mUnitName)
            return;
        if (this.mProblemIdxs.join(",") != condition_data[2].join(",")) {
            this.mProblemIdxs = condition_data[2];
            this._reselectFamily();
        }
    },
    
    _reselectFamily: function() {
        for (var m_idx = 0; m_idx < this.mFamily.length; m_idx++)
            document.getElementById("zyg_fam_m__" + m_idx).checked =
                (this.mProblemIdxs.indexOf(m_idx) >= 0);
        this.refreshContext();
    },
    
    _reportStat: function(list_stat_rep) {
        this.mZEmpty = true;
        if (this.mZStat == null) {
            list_stat_rep.push('<span class="stat-bad">Determine problem group</span>');
        } else {
            list_count = 0;
            for (j = 0; j < this.mZStat.length; j++) {
                if (this.mZStat[j][1] > 0)
                    list_count++;
            }
            if (list_count > 0) {
                list_stat_rep.push('<ul>');
                for (j = 0; j < this.mZStat.length; j++) {
                    var_name = this.mZStat[j][0];
                    var_count = this.mZStat[j][1];
                    if (var_count == 0)
                        continue;
                    this.mZEmpty = false;
                    list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                        '<span class="stat-count">' +
                        var_count + ' records</span></li>');
                }
            } else {
                list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
            }
        }
    },
    
    resetGrp: function() {
        if (this.mDefaultIdxs != this.mProblemIdxs) {
            this.mProblemIdxs = this.mDefaultIdxs;
            this._reselectFamily();
            return;
        }
    },
    
    checkMember: function(m_idx) {
        m_checked = document.getElementById("zyg_fam_m__" + m_idx).checked;
        if (m_checked && this.mProblemIdxs.indexOf(m_idx) < 0) {
            this.mProblemIdxs.push(m_idx);
            this.mProblemIdxs.sort();
            this.refreshContext();
            return;
        } 
        if (!m_checked) {
            pos = this.mProblemIdxs.indexOf(m_idx);
            if (pos >= 0) {
                this.mProblemIdxs.splice(pos, 1);
                this.refreshContext();
            }
        }
    },
    
    refreshContext: function() {
        if (this.mDefaultIdxs.length > 0)
            document.getElementById("zyg_fam_reset").disabled = 
                (this.mDefaultIdxs.join(',') == this.mProblemIdxs.join(','));
        var ctx = {"problem_group": this.mProblemIdxs.slice()};
        sUnitsH.setCtx(ctx);

        args = "ds=" + sDSName + "&unit=" + this.mUnitName + "&conditions=" +
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions())) +
            "&ctx=" + encodeURIComponent(JSON.stringify(ctx));
        ajaxCall("xl_statunit", args, function(info){sZygosityH._refresh(info);})
    },
    
    _refresh: function(info) {
        this.mZStat = info[3];
        rep_list = [];
        this._reportStat(rep_list);
        document.getElementById("zyg-stat").innerHTML = rep_list.join('\n');
        sUnitsH.updateZygUnit(this.getUnitTitle());
    }
};

/*************************************/
var sFiltersH = {
    mTimeH: null,
    mCurOp: null,
    mSelName: null,
    mComboName: null,
    mDivOpList: null,
    mBtnOp: null,
    
    mAllList: [],
    mOpList: [],
    mLoadList: [],

    init: function() {
        document.getElementById("cond-mode-only-span").style.display = "none";
        this.mInpName   = document.getElementById("filter-name-filter");
        this.mSelName   = document.getElementById("filter-name-filter-list");
        this.mComboName = document.getElementById("filter-name-combo");
        this.mDivOpList  = document.getElementById("filters-op-list");
        this.mBtnOp     = document.getElementById("filter-flt-op");
        sViewH.addToDrop(this.mDivOpList);
    },

    setup: function(filter_list) { // reduced monitor.js//setupNamedFilters()
        this.mOpList = [];
        this.mLoadList = [];
        this.mAllList = [];
        for (idx = 0; idx < filter_list.length; idx++) {
            flt_name = filter_list[idx][0];
            this.mAllList.push(flt_name);
            if (!filter_list[idx][1])
                this.mOpList.push(flt_name);
            if (filter_list[idx][2])
                this.mLoadList.push(flt_name);
        }
        return this.mAllList;
    },
    
    update: function() {
        this.mCurOp = null;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        cur_filter = sOpFilterH.getCurFilterName();
        if (cur_filter == "") {
            this.mComboName.style.display = "none";
        } else {
            this.mInpName.value = cur_filter;
            this.mInpName.disabled = true;
            this.mSelName.disabled = true;
            this.mComboName.style.display = "block";
        }
        this.mInpName.style.visibility = "visible";
        document.getElementById("filters-op-create").className = 
            (sConditionsH.isEmpty())? "disabled":"";
        document.getElementById("filters-op-modify").className = 
            (sConditionsH.isEmpty() || cur_filter != "" ||
                (this.mOpList.length == 0))? "disabled":"";
        document.getElementById("filters-op-delete").className = 
            (cur_filter == "" || 
                this.mOpList.indexOf(cur_filter) < 0)? "disabled":"";
        this.mBtnOp.style.display = "none";
        sViewH.dropOff();
    },

    checkName: function() {
        if (this.mCurOp == null)
            return;

        cur_filter = sOpFilterH.getCurFilterName();
        filter_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(filter_name) >= 0;
        q_op  = this.mOpList.indexOf(filter_name) >= 0;
        q_load = this.mLoadList.indexOf(filter_name) >= 0;
        
        if (this.mCurOp == "modify") {
            this.mBtnOp.disabled = (!q_op) || filter_name == cur_filter;
            return;
        }
        if (this.mCurOp == "load") {
            this.mBtnOp.disabled = (!q_load) || filter_name == cur_filter;
            return;
        }
        
        if (this.mCurOp != "create") {
            return; /*assert false! */
        }
        
        q_ok = (q_all)? false: checkFilterAsIdent(filter_name);
        
        this.mInpName.className = (q_ok)? "": "bad";
        this.mBtnOp.disabled = !q_ok;
        
        if (this.mTimeH == null) 
            this.mTimeH = setInterval(function(){sFiltersH.checkName();}, 100);
    },
    
    clearOpMode: function() {
    },

    menu: function() {
        if (this.mDivOpList.style.display != "none") {
            sViewH.dropOff();
            this.update();
            return;
        }
        this.update();
        sViewH.dropOff();
        this.mDivOpList.style.display = "block";
    },

    select: function() {
        this.mInpName.value = this.mSelName.value;
        this.checkName();
    },

    startLoad: function() {
        sViewH.dropOff();
        this.mCurOp = "load";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.fillSelNames(false, this.mLoadList);
        this.mSelName.disabled = false;
        this.mBtnOp.innerHTML = "Load";
        this.mBtnOp.style.display = "block";
        this.select();
        this.mComboName.style.display = "block";
    },

    startCreate: function() {
        if (sConditionsH.isEmpty())
            return;
        sViewH.dropOff();
        this.mCurOp = "create";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "visible";
        this.mSelName.disabled = false;
        this.mInpName.disabled = false;
        this.fillSelNames(true, this.mAllList);
        this.mBtnOp.innerHTML = "Create";
        this.mBtnOp.style.display = "block";
        this.checkName();
        this.mComboName.style.display = "block";
    },

    startModify: function() {
        cur_filter = sOpFilterH.getCurFilterName();
        if (sConditionsH.isEmpty() || cur_filter != "")
            return;
        sViewH.dropOff();
        this.fillSelNames(false, this.mOpList);
        this.mCurOp = "modify";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.mSelName.disabled = false;
        this.mBtnOp.innerHTML = "Modify";
        this.mBtnOp.style.display = "block";
        this.select();
        this.mComboName.style.display = "block";
    },

    deleteIt: function() {
        cur_filter = sOpFilterH.getCurFilterName();
        if (cur_filter == "" ||  this.mOpList.indexOf(cur_filter) < 0)
            return;
        sViewH.dropOff();
        sUnitsH.setup(sConditionsH.getConditions(), "",
            ["instr", "DROP/" + this.mInpName.value]);
        sOpFilterH._onChangeFilter();
    },

    action: function() {
        cur_filter = sOpFilterH.getCurFilterName();
        filter_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(filter_name) >= 0;
        q_op = this.mOpList.indexOf(filter_name) >= 0;
        q_load = this.mLoadList.indexOf(filter_name) >= 0;
        
        switch (this.mCurOp) {
            case "create":
                if (!q_all && checkFilterAsIdent(filter_name)) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", "UPDATE/" + filter_name]);
                    sOpFilterH._onChangeFilter();
                }
                break;
            case "modify":
                if (q_op && filter_name != cur_filter) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", "UPDATE/" + filter_name]);
                    sOpFilterH._onChangeFilter();
                }
                break;
            case "load":
                if (q_load && filter_name != cur_filter) {
                    sOpFilterH._updateConditions(null, filter_name);
                }
                break;
        }
    },

    fillSelNames: function(with_empty, filter_list) {
        if (this.mSelName == null || this.mAllList == null)
            return;
        for (idx = this.mSelName.length -1; idx >= 0; idx--) {
            this.mSelName.remove(idx);
        }
        if (with_empty) {
            var option = document.createElement('option');
            option.innerHTML = "";
            option.value = "";
            this.mSelName.append(option)
        }
        for (idx = 0; idx < filter_list.length; idx++) {
            flt_name = filter_list[idx];
            var option = document.createElement('option');
            option.innerHTML = flt_name;
            option.value = flt_name;
            this.mSelName.append(option)
        }
        this.mSelName.selectedIndex = 0;
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
    mWSFormed: false,
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
    
    reset: function() {
        this.mWSFormed = false;
    },
    
    show: function() {
        if (this.mWSFormed) {
            sViewH.dropOn(this.mDivModStatus);
            return;
        }
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDSNames = null;
        this.mTaskId = null;
        this.mSpanModTitle.innerHTML = 'Create workspace for ' +
            sUnitsH.mCount + ' of ' + sUnitsH.mTotal;
        var err_msg = "";
        if (sUnitsH.mCount >= 5000)
            err_msg = "Too many records, try to reduce";
        if (sUnitsH.mCount < 1)
            err_msg = "Empty set";
        /*if (sUnitsH.mCount < 10)
            err_msg = "Too small workspace";*/
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
        ajaxCall("xl2ws", "ds=" + sDSName + "&conditions= " +
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions())) +
            "&ws=" + encodeURIComponent(this.mInputModName.value),
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
            self.mWSFormed = true;
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
        if (this.mDropCtrls.indexOf(ctrl) < 0)
            this.mDropCtrls.push(ctrl);
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

function goToTree() {
    sViewH.dropOff();
    window.open("xl_tree?ds=" + sDSName, sCommonTitle + ":" + sDSName + ":L");
}

function wsCreate() {
    sCreateWsH.show();
}

function startWsCreate() {
    sCreateWsH.startIt();
}

/*************************************/
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

/*************************************/
function showExport() {
    sViewH.dropOff();
    if (sUnitsH.mExportFormed) {
        sViewH.dropOn(document.getElementById("ws-export-result"));
        return;
    }
    if (sUnitsH.mCount <= 300)
        res_content = 'Export ' + sUnitsH.mCount + ' records?<br>' +
            '<button class="drop" onclick="doExport();">Export</button>' + 
            '&emsp;<button class="drop" onclick="sViewH.dropOff();">Cancel</button>';
    else
        res_content = 'Too many records for export: ' + 
            sUnitsH.mCount + ' > 300.<br>' +
            '<button class="drop" onclick="sViewH.dropOff();">Cancel</button>';
    res_el = document.getElementById("ws-export-result");
    res_el.innerHTML = res_content;
    sViewH.dropOn(res_el);
}

function doExport() {
    args = "ds=" + sDSName + "&conditions=" + 
        encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
    ajaxCall("xl_export", args, setupExport);
}

function setupExport(info) {
    res_el = document.getElementById("ws-export-result");
    if (info["fname"]) {
        res_el.className = "drop";
        res_el.innerHTML = 'Exported ' + sUnitsH.mCount + ' records<br>' +
        '<a href="' + info["fname"] + '" target="blank" ' + 'download>Download</a>';
    } else {
        res_el.className = "drop problems";
        res_el.innerHTML = 'Bad configuration';
    }
    sUnitsH.mExportFormed = true;
    showExport();
}

/*************************************/
