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
    mCurFuncName: null,
    mTotalCounts: null,
    mFilteredCounts: null,
    mRqId: null,
    mUnitsDelay: null,
    mWaiting: null,
    mTimeH: null,
    mDelayMode: null,
    mOffline: false,
    mCount: null,
    
    init: function(call_ds, delay_mode) {
        this.mCallDS = call_ds;
        this.mDivList = document.getElementById("stat-list");
        this.mDelayMode = delay_mode;
        sFiltersH.init();
        sOpCondH.init();
        sOpNumH.init();
        sOpEnumH.init("filter-cur-cond", 10);
        sCreateWsH.init();
        this.setup();
    },
    
    getRqArgs: function(use_id) {
        ret = this.mCallDS + "&conditions=" + 
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
        if (use_id)
            ret += "&rq_id=" + encodeURIComponent(this.mRqId);
        return ret;
    },
    
    formRqArgs: function(conditions, filter_name, use_delay, add_instr) {
        args =  this.mCallDS;
        if (filter_name) {
            args += "&filter=" + encodeURIComponent(filter_name);
        } else {
            if (conditions)
                args += "&conditions=" + 
                    encodeURIComponent(JSON.stringify(conditions)); 
        }
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
        ajaxCall("ds_stat", 
            this.formRqArgs(conditions, filter_name, true, add_instr), 
            function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        this.mOffline = true;
        this.mWaiting = false;
        this.mFilteredCounts = info["filtered-counts"];
        this.mTotalCounts = info["total-counts"];
        this.mCount = this.mFilteredCounts[0];
        this.mRqId  = info["rq-id"];
        var el_rep = document.getElementById("list-report");
        if (el_rep) {
            if (this.mFilteredCounts[0] != this.mTotalCounts[0])
                el_rep.innerHTML = 
                    this.mFilteredCounts[0] + "/" + this.mTotalCounts[0];
            else
                el_rep.innerHTML = this.mFilteredCounts[0] + "";
        }
        if (sSamplesCtrl)
            sSamplesCtrl.reset(this.mFilteredCounts[0]);
        this.mItems = [];
        for (var idx=0; idx < info["stat-list"].length; idx++) {
            if (sOpFuncH.notSupported(info["stat-list"][idx]))
                continue;
            this.mItems.push(info["stat-list"][idx]);
        }
        sConditionsH.setup(info);
        sOpFilterH.update(info["cur-filter"], info["filter-list"]);
        updateCurFilter(sOpFilterH.getCurFilterName(), true);
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
                if (unit_name == this.mItems[idx]["name"]) {
                    unit_idx = idx;
                    break;
                }                    
            }
            unit_name = (unit_idx !=null)? unit_name:null;
        }
        
        if (!unit_name) 
            unit_name = this.mItems[0]["name"];
        this.mCurUnit = null;
        this.mCurFuncName = null;
        
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
        if (info["rq-id"] != this.mRqId) 
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
            unit_name = unit_stat["name"];
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
        if (this.mCurUnit == null)
            return "?";
        if (this.mItems[this.mUnitMap[this.mCurUnit]]["kind"] == "func")
            return this.mCurUnit + "()";
        return this.mCurUnit;
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
        new_unit_el.className = new_unit_el.className + " cur";
        softScroll(new_unit_el, 1);
        sConditionsH.onUnitSelect();
        sOpCondH.onUnitSelect();
    },
    
    updateFuncUnit: function(unit_name, unit_stat) {
        if (this.mCurFuncName != null) {
            this.mCurFuncName = unit_name;
            this.mItems[this.mUnitMap[unit_name]] = unit_stat;
            this.selectUnit(this.mCurUnit, true);
        }
    },
    
    prepareWsCreate: function() {
        return [this.mFilteredCounts[0], this.mTotalCounts[0]];
    },
    
    getWsCreateArgs: function() {
        return this.mCallDS + "&conditions=" + 
            encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
    },
    
    getCurCount: function() {
        return this.mFilteredCounts[0];
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
    },
    
    checkRqId: function(info) {
        if (info["rq-id"] != this.mRqId) 
            return false;
        return true;
    }
};

/**************************************/
var sOpFilterH = {
    mCurFilter: "",
    mHistory: [],
    mRedoStack: [],

    update: function(filter_name, filter_list) {
        this.mCurFilter = (filter_name)? filter_name:"";
        var all_filters = sFiltersH.setup(filter_name, filter_list)
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
    
    getCurFilterName: function() {
        return this.mCurFilter;
    },
    
    tryLoadFilter: function(filter_name) {
        if (filter_name == this.mCurFilter)
            return false;
        if (sConditionsH.isEmpty() || !!this.mCurFilter) {
            this._updateConditions(null, filter_name);
            return true;
        }
        return false;
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
    
    _fixCurConditions: function() {
        this.mHistory.push(
            [this.mCurFilter, sConditionsH.getConditions()]);
        this.mRedoStack = [];
    },
        
    _updateConditions: function(new_seq, filter_name) {
        this._fixCurConditions();
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
    mCondSeq: [],
    mCurCondIdx: null,

    setup: function(info) {
        this.mList = info["conditions"];
        this.mCondSeq = info["cond-seq"];
        var list_cond_rep = [sFiltersH.getCurUpdateReport(info["eval-status"])];
        for (idx = 0; idx < this.mCondSeq.length; idx++) {
            cond_info = this.mCondSeq[idx];
            if (!cond_info["unit"]) {
                list_cond_rep.push('<div id="cond--' + idx + 
                    '" class="cond-descr"><span title="' + cond_info["err"] + 
                    '">&#x26d4;</span>&emsp;' +
                    '<button onclick="sConditionsH.delBadCond(' + idx + 
                    ')">delete it</button>&emsp;<s>' + cond_info["repr"] + '</s></div>');
            } else {
                list_cond_rep.push('<div id="cond--' + idx + '" class="cond-descr" ' +
                    'onclick="sConditionsH.selectCond(\'' + idx + '\');"')
                if (cond_info["err"])
                    list_cond_rep.push('><span class="warn" title="' + cond_info["err"] + 
                    '">&#x2699;</span>&emsp;');
                else
                    list_cond_rep.push('>&bull;&emsp;');
                list_cond_rep.push(cond_info["repr"]);
            }
            list_cond_rep.push('</div>')
        }
        document.getElementById("cond-list").innerHTML = list_cond_rep.join('\n');
        var cond_idx = (this.mCurCondIdx != null && 
            this.mCurCondIdx < this.mCondSeq.length)? 
            this.mCurCondIdx: this.mCondSeq.length - 1;
        this.mCurCondIdx = null;
        if (cond_idx >= 0 && this.mCondSeq[cond_idx]["unit"])
            this.selectCond(cond_idx, true);
    },
    
    selectCond: function(cond_no, force_it) {
        if (!force_it && this.mCurCondIdx == cond_no) 
            return;
        if (cond_no != null && this.mCondSeq[cond_no]["unit"]) {
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
            sUnitsH.selectUnit(this.mCondSeq[cond_no]["unit"], true);
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
                this.mCondSeq[this.mCurCondIdx]["unit"] != sUnitsH.getCurUnitName())
            this.selectCond(this.findCond(sUnitsH.getCurUnitName()));
    },

    findCond: function(unit_name, cond_type) {
        if (this.mCurCondIdx != null && 
                this.mCondSeq[this.mCurCondIdx]["unit"] == unit_name)
            return this.mCurCondIdx;
        for (idx = 0; idx < this.mCondSeq.length; idx++) {
            if (this.mCondSeq[idx]["unit"] == unit_name) {
                if (!cond_type || cond_type == this.mList[idx][0])
                    return idx;
            }
        }
        return null;
    },
    
    nextIdx: function() {
        return this.mCondSeq.length;
    },
    
    isEmpty: function() {
        return (this.mCondSeq.length == 0);
    },
    
    getCondCount: function() {
        return this.mCondSeq.length;
    },
    
    report: function() { 
        if (this.mCondSeq.length == 0)
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
        sOpFilterH.deleteCondition(idx);
    }
};

/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mIdxToUpdate: null,
    mIdxToAdd: null,
    
    init: function() {
    },
    
    onUnitSelect: function() {
        unit_name = sUnitsH.getCurUnitName();
        document.getElementById("cond-title").innerHTML = sUnitsH.getCurUnitTitle();
        if (unit_name == null) {
            sOpEnumH.suspend();
            sOpNumH.suspend();
            this.formCondition(null);
            return;
        } 
        unit_stat = sUnitsH.getCurUnitStat();
    
        if (unit_stat["incomplete"])
            this.mCurTpHandler = null;
        else {
            switch(unit_stat["kind"]) {
                case "numeric":
                    this.mCurTpHandler = sOpNumH;
                    break;
                default:
                    this.mCurTpHandler = sOpEnumH;
            }
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
    
    formCondition: function(condition_data, err_msg, add_always) {
        cur_unit_name = sUnitsH.getCurUnitName();
        this.mCondition   = null;
        this.mIdxToAdd    = null;
        this.mIdxToUpdate = null;
        if (condition_data != null) {
            this.mCondition = [this.mCurTpHandler.getCondType(), cur_unit_name].concat(
                condition_data);
            this.mIdxToUpdate = sConditionsH.findCond(cur_unit_name, 
                this.mCurTpHandler.getCondType());
            if (this.mIdxToUpdate == null) {
                if (add_always) { 
                    this.mIdxToUpdate = sConditionsH.findCond(cur_unit_name, 
                        this.mCurTpHandler.getCondType());
                } else {
                    this.mIdxToAdd = sConditionsH.findCond(cur_unit_name, 
                        this.mCurTpHandler.getCondType());
                    if (this.mIdxToAdd == null)
                        this.mIdxToAdd = sConditionsH.nextIdx();
                }
            }
            if (add_always) {
                this.mIdxToAdd = (this.mIdxToUpdate == null)?
                    sConditionsH.nextIdx(): this.mIdxToUpdate + 1;
            }
        }
        message_el = document.getElementById("cur-cond-message");
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
    }
};

/*************************************/
var sFiltersH = {
    mTimeH: null,
    mCurOp: null,
    mSelName: null,
    mComboName: null,
    mCurFilterName: null,
    mCurFilterInfo: null,
    mCurFilterIdx: null,
    mBtnOp: null,
    
    mAllList: [],
    mOpList: [],
    mFltTimeDict: null,

    init: function() {
        this.mInpName   = document.getElementById("filter-name-input");
        this.mSelName   = document.getElementById("filter-name-combo-list");
        this.mComboName = document.getElementById("filter-name-combo");
        this.mBtnOp     = document.getElementById("filter-act-op");
    },

    setup: function(filter_name, filter_list) {
        this.mCurFilterName = filter_name;
        this.mCurFilterInfo = null;
        var prev_all_list = JSON.stringify(this.mAllList);
        this.mOpList = [];
        this.mAllList = [];
        this.mFltTimeDict = {};
        this.mCurFilterIdx = 0;
        for (idx = 0; idx < filter_list.length; idx++) {
            flt_info = filter_list[idx];
            if (flt_info["name"] == this.mCurFilterName)
                this.mCurFilterInfo = flt_info;
            if (flt_info["name"] ==this.mCurFilterName)
                this.mCurFilterIdx = this.mAllList.length;
            this.mAllList.push(flt_info["name"]);
            if (!flt_info["standard"])
                this.mOpList.push(flt_info["name"]);
            this.mFltTimeDict[flt_info["name"]] = filter_list["upd-time"];
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
        
        if (!this.mCurFilterName) {
            this.mComboName.style.display = "none";
            this.mInpName.value = "";
        } else {
            this.mInpName.value = this.mCurFilterName;
            this.mInpName.disabled = true;
            this.mSelName.disabled = true;
            this.mComboName.style.display = "block";
        }
        this.mInpName.style.visibility = "visible";
        no_cond = sConditionsH.isEmpty();
        has_name = !!this.mCurFilterName;
        no_op_names = (this.mOpList.length == 0);
        
        document.getElementById("filters-op-create").className = 
            (no_cond || has_name)? "disabled":"";
        document.getElementById("filters-op-modify").className = 
            (no_cond || has_name || no_op_names)? "disabled":"";
        document.getElementById("filters-op-join").className = 
            (no_cond)? "disabled":"";
        document.getElementById("filters-op-delete").className = 
            (this.mCurFilterName == "" || 
                this.mOpList.indexOf(this.mCurFilterName) < 0)? "disabled":"";
        this.mBtnOp.style.display = "none";
    },

    getCurUpdateReport: function(eval_status) {
        if (this.mCurFilterInfo == null && eval_status == "ok")
            return '';
        var ret = ['<div class="upd-note">'];
        if (eval_status == "fatal") {
            ret.push('<span class="bad">Conditions contain errors</span>');
        } else {
            if (eval_status == "runtime")
                ret.push('<span class="warn">Runtime problems</span>'); 
        }
        if (this.mCurFilterInfo != null) {
            if (this.mCurFilterInfo["upd-time"] != null) {
                ret.push('Updated at ' + 
                    timeRepr(this.mCurFilterInfo["upd-time"]));
                if (this.mCurFilterInfo["upd-from"] != sDSName) 
                    ret.push(' from ' + this.mCurFilterInfo["upd-from"]);
            }
        }
        ret.push('</div>');
        return ret.join('\n');
    },
    
    checkName: function() {
        if (this.mCurOp == null)
            return;

        cur_filter = sOpFilterH.getCurFilterName();
        filter_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(filter_name) >= 0;
        q_op  = this.mOpList.indexOf(filter_name) >= 0;
        
        if (this.mCurOp == "modify") {
            this.mBtnOp.disabled = (!q_op) || filter_name == cur_filter;
            return;
        }
        if (this.mCurOp == "load" || this.mCurOp == "join") {
            this.mBtnOp.disabled = (!q_all) || filter_name == cur_filter;
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
    
    select: function() {
        this.mInpName.value = this.mSelName.value;
        this.checkName();
    },

    startLoad: function() {
        this.mCurOp = "load";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.fillSelNames(false, this.mAllList, this.mCurFilterIdx);
        this.mSelName.disabled = false;
        this.mBtnOp.innerHTML = "Load";
        this.mBtnOp.style.display = "block";
        this.select();
        this.mComboName.style.display = "block";
    },

    startJoin: function() {
        this.mCurOp = "join";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.fillSelNames(false, this.mAllList, this.mCurFilterIdx);
        this.mSelName.disabled = false;
        this.mBtnOp.innerHTML = "Join";
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
            ["instr", JSON.stringify(["DELETE", this.mInpName.value])]);
    },

    action: function() {
        cur_filter = sOpFilterH.getCurFilterName();
        filter_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(filter_name) >= 0;
        q_op = this.mOpList.indexOf(filter_name) >= 0;
        
        switch (this.mCurOp) {
            case "create":
                if (!q_all && checkIdentifier(filter_name)) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", JSON.stringify(["UPDATE", filter_name])]);
                }
                break;
            case "modify":
                if (q_op && filter_name != cur_filter) {
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", JSON.stringify(["UPDATE", filter_name])]);
                }
                break;
            case "join":
                if (q_all && filter_name != cur_filter) {
                    sOpFilterH._fixCurConditions();
                    sUnitsH.setup(sConditionsH.getConditions(), cur_filter,
                        ["instr", JSON.stringify(["JOIN", filter_name])]);
                }
                break;
            case "load":
                if (q_all && filter_name != cur_filter) {
                    sOpFilterH._updateConditions(null, filter_name);
                }
                break;
        }
    },

    fillSelNames: function(with_empty, filter_list, sel_idx) {
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
        this.mSelName.selectedIndex = (sel_idx)? sel_idx : 0;
    },
    
    getAllList: function() {
        return this.mAllList;
    }
};

/*************************************/
/* Export                            */
/*************************************/
function showExport() {
    relaxView();
    if (getCurCount() <= 300)
        res_content = 'Export ' + getCurCount() + ' variants?<br>' +
            '<button class="popup" onclick="doExport();">To Excel</button>' + 
            '&emsp;<button class="popup" onclick="doCSVExport();">To CSV</button>' + 
            '&emsp;<button class="popup" onclick="relaxView();">Cancel</button>';
    else
        res_content = 'Too many variants for export: ' + 
            getCurCount() + ' > 300.<br>' +
            '<button class="popup" onclick="relaxView();">Cancel</button>';
    res_el = document.getElementById("export-result");
    res_el.innerHTML = res_content;
    sViewH.popupOn(res_el);
}

function setupExport(info) {
    res_el = document.getElementById("export-result");
    if (info["fname"]) {
        res_el.className = "popup";
        res_el.innerHTML = 'Exported ' + getCurCount() + ' variants<br>' +
        '<a href="' + info["fname"] + '" target="blank" ' + 'download>Download</a>';
    } else {
        res_el.className = "popup problems";
        res_el.innerHTML = 'Bad configuration';
    }
    sViewH.popupOn(res_el);
}

