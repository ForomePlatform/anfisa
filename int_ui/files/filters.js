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
/* Filtering common support
 * Used in regimes: 
 * WS/XL-Filter
/**************************************/
var sUnitsH = {
    mCallDS: null,
    mDivList: null,
    mItems: null,
    mUnitMap: null,
    mCurUnit: null,
    mCurZygName: null,
    mCounts: null,
    mTotal: null,
    mExportFormed: null,
    mCtx: {},
    mRqId: null,
    mUnitsDelay: null,
    mWaiting: null,
    mTimeH: null,
    mDelayMode: null,
    mCompData: null,
    mOffline: false,
    
    init: function(call_ds, delay_mode) {
        this.mCallDS = call_ds;
        this.mDivList = document.getElementById("stat-list");
        this.mDelayMode = delay_mode;
        sFiltersH.init();
        sOpCondH.init();
        sOpNumH.init();
        sOpEnumH.init();
        this.setup();
    },
    
    formRqArgs: function(conditions, filter_name, use_delay, add_instr) {
        args =  this.mCallDS + sAppModeRq +
            "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
        if (filter_name) {
            args += "&filter=" + encodeURIComponent(filter_name);
        } else {
            if (conditions)
                args += "&conditions=" + 
                    encodeURIComponent(JSON.stringify(conditions)); 
        }
        if (this.mCompData)
            args += "&compiled=" + encodeURIComponent(JSON.stringify(this.mCompData));        
        if (add_instr)
            args += "&" + add_instr[0] + "=" + encodeURIComponent(add_instr[1]);
        if (use_delay && this.mDelayMode)
            args += "&tm=0";
        return args;
    },
    
    setup: function(conditions, filter_name, add_instr) {
        this.mRqId = false;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDivList.className = "wait";
        this.mWaiting = true;
        ajaxCall("stat", 
            this.formRqArgs(conditions, filter_name, true, add_instr), 
            function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        this.mOffline = true;
        this.mWaiting = false;
        this.mCount = info["count"];
        this.mTotal = info["total"];
        this.mRqId  = info["rq_id"];
        this.mCompData = info["compiled"];
        this.mExportFormed = false;
        var el_rep = document.getElementById("list-report");
        if (el_rep)
            el_rep.innerHTML = (this.mCount == this.mTotal)? 
                this.mTotal : this.mCount + "/" + this.mTotal;
        if (sSubViewH)
            sSubViewH.reset(this.mCount);
        this.mItems = info["stat-list"];
        sConditionsH.setup(info["conditions"], info["bad-idxs"]);
        sOpFilterH.update(info["cur-filter"], info["filter-list"]);
        sOpCondH.setupAvailImport(info["avail-import"]);
        this.mUnitMap = {}
        var list_stat_rep = [];
        this.mUnitsDelay = [];
        fillStatList(this.mItems, this.mUnitMap, list_stat_rep, this.mUnitsDelay);
        this.mDivList.className = "";
        this.mDivList.innerHTML = list_stat_rep.join('\n');
        
        var unit_name = this.mCurUnit;
        if (unit_name) {
            var unit_idx = null;
            for (idx = 0; idx < this.mItems.length; idx++) {
                if (unit_name == this.mItems[idx][1]["name"]) {
                    unit_idx = idx;
                    break;
                }                    
            }
            unit_name = (unit_idx !=null)? unit_name:null;
        }
        
        if (! unit_name) 
            unit_name = this.mItems[0][1]["name"];
        this.mCurUnit = null;
        this.mCurZygName = null;
        
        this.mOffline = false;
        this.selectUnit(unit_name);
        sFiltersH.update();
        this.checkDelayed();
    },

    checkDelayed: function() {
        if (this.mWaiting || this.mTimeH != null || this.mUnitsDelay.length == 0)
            return;
        this.mTimeH = setInterval(function(){sUnitsH.loadUnits();}, 50);
    },
    
    getRqArgs: function(no_ctx) {
        ret = this.mCallDS + sAppModeRq + "&conditions=" + 
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
        if (!no_ctx) {
            ret += "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
            if (this.mCompData)
                ret += "&compiled=" + 
                    encodeURIComponent(JSON.stringify(this.mCompData));        
        }
        return ret;
    },
    
    loadUnits: function() {
        clearInterval(this.mTimeH);
        this.mTimeH = null;
        if (this.mWaiting || this.mUnitsDelay.length == 0)
            return;
        this.mWaiting = true;
        this.sortVisibleDelays();
        ajaxCall("statunits", this.getRqArgs() +
            ((this.mDelayMode)? "&tm=1":"") + 
            "&rq_id=" + encodeURIComponent(this.mRqId) + 
            "&units=" + encodeURIComponent(JSON.stringify(this.mUnitsDelay)), 
            function(info){sUnitsH._loadUnits(info);})
    },

    _unitDivEl: function(unit_name) {
        return document.getElementById("stat--" + unit_name);
    },
    
    _loadUnits: function(info) {
        if (info["rq_id"] != this.mRqId) 
            return;
        this.mWaiting = false;
        var cur_el = (this.mCurUnit)? this._unitDivEl(this.mCurUnit): null;
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
                this.mDivList.scrollTop += cur_top - prev_top;
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
        if (this.mOffline) {
            this.mCurUnit = stat_unit;
            return;
        }
        var pos = this.mUnitsDelay.indexOf(stat_unit);
        if (pos > 0) {
            this.mUnitsDelay.splice(pos, 1);
            this.mUnitsDelay.splice(0, 0, stat_unit);
        }
        if (pos >= 0) 
            this.checkDelayed();
        if (this.mCurUnit == stat_unit && !force_it) 
            return;
        var new_unit_el = this._unitDivEl(stat_unit);
        if (new_unit_el == null) 
            return;
        if (this.mCurUnit != null) {
            var prev_el = this._unitDivEl(this.mCurUnit);
            if (prev_el)
                prev_el.className = prev_el.className.replace(" cur", "");
        }
        this.mCurUnit = stat_unit;
        this.mCurZygName = sZygosityH.checkUnitTitle(stat_unit);
        new_unit_el.className = new_unit_el.className + " cur";
        softScroll(new_unit_el, 1);
        sConditionsH.onUnitSelect();
        sOpCondH.onUnitSelect();
    },
    
    updateZygUnit: function(zyg_name, unit_stat) {
        if (this.mCurZygName != null) {
            this.mCurZygName = zyg_name;
            this.mItems[this.mUnitMap[zyg_name]] = unit_stat;
            this.selectUnit(this.mCurUnit, true);
        }
    },
    
    setCtxPar: function(key, val) {
        this.mCtx[key] = val;
    },
    
    prepareWsCreate: function() {
        return [this.mCount, this.mTotal];
    },
    
    getWsCreateArgs: function() {
        return this.mCallDS + sAppModeRq + "&conditions=" + 
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
    },
    
    getCurCount: function() {
        return this.mCount;
    },
    
    sortVisibleDelays: function() {
        var view_height = this.mDivList.getBoundingClientRect().height;
        view_seq = [];
        hidden_seq = [];
        for (var idx=0; idx < this.mUnitsDelay.length; idx++) {
            var rect = this._unitDivEl(this.mUnitsDelay[idx]).getBoundingClientRect();
            if ((rect.top + rect.height < 0) || (rect.top > view_height))
                hidden_seq.push(this.mUnitsDelay[idx]);
            else
                view_seq.push(this.mUnitsDelay[idx]);
        }
        this.mUnitsDelay = view_seq.concat(hidden_seq);
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
        updateCurFilter(this.mCurFilter, true);
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
    },

    addCondition: function(new_cond, idx) {
        new_seq = sConditionsH.getConditions().slice();
        if (idx == undefined)
            new_seq.push(new_cond);
        else
            new_seq.splice(idx, 0, new_cond);
        this._updateConditions(new_seq);
    },
    
    deleteCondition: function(idx_to_remove) {
        new_seq = sConditionsH.getConditions().slice();
        new_seq.splice(idx_to_remove, 1);
        this._updateConditions(new_seq);
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
            }
        }
        if (action == "redo") {
            if (this.mRedoStack.length > 0) {
                this.mHistory.push(
                    [this.mCurFilter, sConditionsH.getConditions()]);
                hinfo = this.mRedoStack.pop();
                sUnitsH.setup(hinfo[1], hinfo[0]);
            }
        }        
    }
};
    
/**************************************/
var sConditionsH = {
    mList: [],
    mBadIdxs: null,
    mCurCondIdx: null,

    setup: function(cond_list, bad_idxs) {
        this.mList = (cond_list)? cond_list:[];
        this.mBadIdxs = (bad_idxs)? bad_idxs:[];
        var list_cond_rep = [];
        for (idx = 0; idx < this.mList.length; idx++) {
            cond = this.mList[idx];
            list_cond_rep.push('<div id="cond--' + idx + '" class="cond-descr" ' +
                'onclick="sConditionsH.selectCond(\'' + idx + '\');">&bull;&emsp;');
            var descr = getCondDescription(cond, false);
            if (this.mBadIdxs.indexOf(idx) >= 0) {
                list_cond_rep.push('<button onclick="sConditionsH.delBadCond(' + idx + 
                    ')">delete it</button>&emsp;<s>' + descr + '</s>');
            } else {
                list_cond_rep.push(descr)
            }
            list_cond_rep.push('</div>')
        }
        document.getElementById("cond-list").innerHTML = list_cond_rep.join('\n');
        var cond_idx = (this.mCurCondIdx != null && this.mCurCondIdx < this.mList.length)?
            this.mCurCondIdx: this.mList.length - 1;
        this.mCurCondIdx = null;
        if (cond_idx >= 0 && this.mBadIdxs.indexOf(cond_idx) < 0)
            this.selectCond(cond_idx, true);
    },
    
    selectCond: function(cond_no, force_it) {
        if (!force_it && this.mCurCondIdx == cond_no) 
            return;
        if (cond_no != null && this.mBadIdxs.indexOf(cond_no) < 0) {
            new_cond_el = document.getElementById("cond--" + cond_no);
            if (new_cond_el == null) 
                return;
        } else {
            new_cond_el = null;
        }
        if (this.mCurCondIdx != null) {
            var prev_el = document.getElementById("cond--" + this.mCurCondIdx);
            prev_el.className = prev_el.className.replace(" cur", "");
        }
        this.mCurCondIdx = cond_no;
        if (new_cond_el != null) {
            new_cond_el.className = new_cond_el.className + " cur";
            sZygosityH.onSelectCondition(this.mList[cond_no]);
            sUnitsH.selectUnit(this.mList[cond_no][1], true);
        }
    },

    getCondRqArgs: function(filter_name, zone_data, use_conditions) {
        if (filter_name == null || sFiltersH.filterExists(filter_name)) {
            conditions = null;
        } else {
            filter_name = null;
            conditions = (use_conditions)? this.mList:null;
        }
        add_instr = (zone_data == null)? null: ["zone", JSON.stringify(zone_data)];
        return sUnitsH.formRqArgs(conditions, filter_name, false, add_instr);
    },
        
    getConditions: function() {
        return this.mList;
    },
    
    getCurCondNo: function() {
        return this.mCurCondIdx;
    },

    getCurCond: function() {
        if (this.mCurCondIdx == null)
            return null;
        return this.mList[this.mCurCondIdx];
    },
    
    onUnitSelect: function() {
        if (this.mCurCondIdx == null || 
                this.mList[this.mCurCondIdx][1] != sUnitsH.getCurUnitName())
            this.selectCond(this.findCond(sUnitsH.getCurUnitName()));
    },

    findCond: function(unit_name, cond_mode) {
        if (this.mCurCondIdx != null && 
                this.mBadIdxs.indexOf(this.mCurCondIdx) < 0 &&
                this.mList[this.mCurCondIdx][1] == unit_name &&
                this.mList[this.mCurCondIdx][0] != "import")
            return this.mCurCondIdx;
        for (idx = 0; idx < this.mList.length; idx++) {
            if (this.mBadIdxs.indexOf(idx) >= 0)
                continue;
            if (this.mList[idx][1] == unit_name) {
                if (this.mList[idx][0] == "import")
                    continue;
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
        return (this.mList.length == 0);
    },
    
    getSeqLength: function() {
        return this.mList.length;
    },
    
    report: function() { 
        if (this.mList.length == 0)
            return "no conditions";
        cur_filter = sOpFilterH.getCurFilterName();
        if (cur_filter)
            return cur_filter + " in work";
        return null;
    },

    preSelectCond: function(idx) {
        this.mCurCondIdx = idx;
    },

    delBadCond: function(idx) {
        if (this.mBadIdxs.indexOf(idx) < 0)
            return;
        if (this.mCurCondIdx != null && this.mCurCondIdx > idx)
            this.mCurCondIdx -= 1;
        sOpFilterH.deleteCondition(idx);
    }
};

/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mIdxToUpdate: null,
    mIdxToAdd: null,
    mBtnImportMenu: null,
    mDivImportList: null,
    mAvailImportList: null,
    
    init: function() {
        this.mBtnImportMenu = document.getElementById("filter-import-op");
        this.mDivImportList = document.getElementById("filters-import-op-list");
    },
    
    setupAvailImport: function(avail_list) {
        this.mDivImportList.style.display = "hidden";
        this.mAvailImportList = avail_list;
        if (this.mAvailImportList) {
            var rep = [];
            for (var j = 0; j < this.mAvailImportList.length; j++)
                rep.push('<a class="drop" onclick="sOpCondH.doImport(\'' + 
                    this.mAvailImportList[j] + '\');">import ' + 
                    this.mAvailImportList[j] + '</a>');            
            this.mDivImportList.innerHTML = rep.join('\n');
            this.mBtnImportMenu.disabled = false;
        } else {
            this.mDivImportList.innerHTML = "";
            this.mBtnImportMenu.disabled = true;
        }
    },
    
    onUnitSelect: function() {
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
            if (unit_type == "int" || unit_type == "float") 
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
                if (add_always) { 
                    this.mIdxToUpdate = sConditionsH.findCond(cur_unit_name);
                } else {
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
            sConditionsH.preSelectCond(this.mIdxToAdd);
            return new_seq;
        }
        if ( func_name == "update" && this.mIdxToUpdate != null) {
            new_seq = condition_seq.slice();
            new_seq[this.mIdxToUpdate] = this.mCondition;
            sConditionsH.preSelectCond(this.mIdxToUpdate);
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
    },
    
    doImport: function(imp_name) {
        sConditionsH.preSelectCond(sConditionsH.getConditions().length);
        sOpFilterH.addCondition(["import", imp_name])
    }
};

/*************************************/
var sFiltersH = {
    mTimeH: null,
    mCurOp: null,
    mSelName: null,
    mComboName: null,
    mBtnOp: null,
    
    mAllList: [],
    mOpList: [],
    mLoadList: [],
    mFltTimeDict: null,

    init: function() {
        this.mInpName   = document.getElementById("filter-name-filter");
        this.mSelName   = document.getElementById("filter-name-filter-list");
        this.mComboName = document.getElementById("filter-name-combo");
        this.mBtnOp     = document.getElementById("filter-flt-op");
    },

    setup: function(filter_list) { // reduced monitor.js//setupNamedFilters()
        var prev_all_list = JSON.stringify(this.mAllList);
        this.mOpList = [];
        this.mLoadList = [];
        this.mAllList = [];
        this.mFltTimeDict = {};
        for (idx = 0; idx < filter_list.length; idx++) {
            flt_name = filter_list[idx][0];
            this.mAllList.push(flt_name);
            if (!filter_list[idx][1])
                this.mOpList.push(flt_name);
            if (filter_list[idx][2])
                this.mLoadList.push(flt_name);
            this.mFltTimeDict[flt_name] = filter_list[idx][3];
        }
        if (prev_all_list != JSON.stringify(this.mAllList))
            onFilterListChange();
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
            (sConditionsH.isEmpty() || cur_filter != "")? "disabled":"";
        document.getElementById("filters-op-modify").className = 
            (sConditionsH.isEmpty() || cur_filter != "" ||
                (this.mOpList.length == 0))? "disabled":"";
        document.getElementById("filters-op-delete").className = 
            (cur_filter == "" || 
                this.mOpList.indexOf(cur_filter) < 0)? "disabled":"";
        this.mBtnOp.style.display = "none";
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
        
        q_ok = (q_all)? false: checkIdentifier(filter_name);
        
        this.mInpName.className = (q_ok)? "": "bad";
        this.mBtnOp.disabled = !q_ok;
        
        if (this.mTimeH == null) 
            this.mTimeH = setInterval(function(){sFiltersH.checkName();}, 100);
    },
    
    filterExists: function(filter_name) {
        return this.mAllList.indexOf(filter_name) >= 0;
    },
    
    clearOpMode: function() {
    },

    select: function() {
        this.mInpName.value = this.mSelName.value;
        this.checkName();
    },

    startLoad: function() {
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
        sUnitsH.setup(sConditionsH.getConditions(), "",
            ["instr", "DELETE/" + this.mInpName.value]);
    },

    action: function() {
        cur_filter = sOpFilterH.getCurFilterName();
        filter_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(filter_name) >= 0;
        q_op = this.mOpList.indexOf(filter_name) >= 0;
        q_load = this.mLoadList.indexOf(filter_name) >= 0;
        
        switch (this.mCurOp) {
            case "create":
                if (!q_all && checkIdentifier(filter_name)) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", "UPDATE/" + filter_name]);
                }
                break;
            case "modify":
                if (q_op && filter_name != cur_filter) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", "UPDATE/" + filter_name]);
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
    },
    
    getAllList: function() {
        return this.mAllList;
    }
};
