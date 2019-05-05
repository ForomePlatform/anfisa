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
var sUnitsH = {
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,
    mCurZygName: null,
    mCounts: null,
    mTotal: null,
    mExportFormed: null,
    mCtx: {"timeout": 1},
    mRqId: null,
    mUnitsDelay: null,
    mWaiting: null,
    mTimeH: null,
    
    setup: function(conditions, filter_name, add_instr) {
        args = "ds=" + sDSName + "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
        if (filter_name) {
            args += "&filter=" + encodeURIComponent(filter_name);
        } else {
            if (conditions)
                args += "&conditions=" + 
                    encodeURIComponent(JSON.stringify(conditions)); 
        }
        if (add_instr)
            args += "&" + add_instr[0] + "=" + encodeURIComponent(add_instr[1]);
        this.mRqId = false;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mWaiting = true;
        ajaxCall("xl_filters", args, function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        this.mWaiting = false;
        this.mCount = info["count"];
        this.mTotal = info["total"];
        this.mRqId  = info["rq_id"];
        this.mExportFormed = false;
        document.getElementById("list-report").innerHTML = 
            (this.mCount == this.mTotal)? 
                this.mTotal : this.mCount + "/" + this.mTotal;
        this.mItems = info["stat-list"];
        sOpFilterH.update(info["cur-filter"], info["filter-list"]);
        this.mUnitMap = {}
        var list_stat_rep = [];
        this.mUnitsDelay = [];
        fillEnumStat(this.mItems, this.mUnitMap, list_stat_rep, this.mUnitsDelay);
        document.getElementById("stat-list").innerHTML = list_stat_rep.join('\n');
        
        this.mCurUnit = null;
        this.mCurZygName = null;
        sConditionsH.setup(info["conditions"]);
        
        if (this.mCurUnit == null)
            this.selectUnit(this.mItems[0][1]["name"]);
        sFiltersH.update();
        this.checkDelayed();
    },

    checkDelayed: function() {
        if (this.mWaiting || this.mTimeH != null || this.mUnitsDelay.length == 0)
            return;
        this.mTimeH = setInterval(function(){sUnitsH.loadUnits();}, 50);
    },
    
    loadUnits: function() {
        clearInterval(this.mTimeH);
        this.mTimeH = null;
        if (this.mWaiting || this.mUnitsDelay.length == 0)
            return;
        this.mWaiting = true;
        ajaxCall("xl_statunits", "ds=" + sDSName + 
            "&rq_id=" + encodeURIComponent(this.mRqId) + 
            "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx)) +
            "&units=" + encodeURIComponent(JSON.stringify(this.mUnitsDelay)) +
            "&conditions=" + encodeURIComponent(
                JSON.stringify(sConditionsH.getConditions())), 
            function(info){sUnitsH._loadUnits(info);})
    },

    _loadUnits: function(info) {
        if (info["rq_id"] != this.mRqId) 
            return;
        this.mWaiting = false;
        el_list = document.getElementById("stat-list");
        var cur_el = (this.mCurUnit)? document.getElementById("stat--" + this.mCurUnit): null;
        if (cur_el)
            var prev_top = cur_el.getBoundingClientRect().top;
        var prev_unit = this.mCurUnit;
        var prev_h =  (this.mCurUnit)? topUnitStat(this.mCurUnit):null;
        for (var idx = 0; idx < info["units"].length; idx++) {
            unit_stat = info["units"][idx];
            refillUnitStat(unit_stat);
            unit_name = unit_stat[1]["name"];
            var pos = this.mUnitsDelay.indexOf(unit_name);
            if (pos >= 0)
                this.mUnitsDelay.splice(pos, 1);
            this.mItems[this.mUnitMap[unit_name]] = unit_stat;
            if (this.mCurUnit == unit_name)
                this.selectUnit(unit_name, true);
            if (cur_el) {
                cur_top = cur_el.getBoundingClientRect().top;
                el_list.scrollTop += cur_top - prev_top;
            }
        }
        this.checkDelayed();
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
        var pos = this.mUnitsDelay.indexOf(stat_unit);
        if (pos >= 0) {
            this.mUnitsDelay.splice(pos, 1);
            this.mUnitsDelay.splice(0, 0, stat_unit);
        }
        if (pos >= 0) 
            this.checkDelayed();
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
    
    getCtx: function() {
        return this.mCtx;
    },
    
    setCtxPar: function(key, val) {
        this.mCtx[key] = val;
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
    
        if (unit_stat.length == 2)
            this.mCurTpHandler = null;
        else {
            if (unit_type == "long" || unit_type == "float") 
                this.mCurTpHandler = sOpNumH;
            else
                this.mCurTpHandler = sOpEnumH;
        }
        if (this.mCurTpHandler != sOpNumH)
            sOpNumH.suspend();
        if (this.mCurTpHandler != sOpEnumH)
            sOpEnumH.suspend();
        document.getElementById("cur-cond-loading").style.display = 
            (this.mCurTpHandler)? "none":"block";
        if (this.mCurTpHandler) {
            this.mCurTpHandler.updateUnit(unit_stat);
            if (sConditionsH.getCurCondNo() != null) {
                cond = sConditionsH.getCurCond();
                if (cond[1] == unit_name)
                    this.mCurTpHandler.updateCondition(cond);
            }
            this.mCurTpHandler.checkControls();
        }
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
        if (this.mCurTpHandler && this.mCondition != null) {
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
function wsCreate() {
    sCreateWsH.show();
}

function startWsCreate() {
    sCreateWsH.startIt();
}

function _prepareWsCreate() {
    return [sUnitsH.mCount, sUnitsH.mTotal];
}

function _callWsArgs() {
    return "&conditions= " + encodeURIComponent(
        JSON.stringify(sConditionsH.getConditions()));
}

/**************************************/
function onModalOff() {
}

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
