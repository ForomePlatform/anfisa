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

/*************************************/
function setupDTree(ds_name, ds_kind, common_title, ws_pub_url) {
    sDSName = ds_name; 
    sDSKind = ds_kind;
    sCommonTitle = common_title;
    sWsPubURL = ws_pub_url;
    window.onresize  = arrangeControls;
    window.onkeydown = onKey;
    window.name = sCommonTitle + ":" + sDSName + ":TREE";
    document.getElementById("ds-name").innerHTML = sDSName;
    
    setupDSControls();
    sUnitsH.init();
    sOpCondH.init();
    sHistoryH.init();
    sVersionsH.init();
    sCodeEditH.init();
    sDTreesH.init();
    sDecisionTree.clear();
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
    mMarkLoc: null,
    mErrorMode: null,
    mPointDelay: null,
    mRqId: null,
    mPostTreeAction: null,
    
    setup: function(tree_code, options) {
        args = "ds=" + sDSName + "&tm=0";
        if (tree_code == true)
            tree_code = this.mTreeCode;
        if (tree_code != false)
            args += "&code=" + encodeURIComponent(tree_code);
        if (options) {
            for (j=0; j < 2; j++) {
                var opt_key = ["dtree", "instr"][j];
                if (options[opt_key])
                    args += "&" + opt_key + "=" + encodeURIComponent(options[opt_key]);
            }
        }
        ajaxCall("dtree_set", args, function(info){sDecisionTree._setup(info);})
    },
    
    _setup: function(info) {
        this.mTreeCode = info["code"];
        this.mTotalCount = info["total"];
        this.mRqId = info["rq_id"];
        sDTreesH.setup(info["dtree-name"], info["dtree-list"]);
        sHistoryH.update(info["hash"]);
        this.mMarkLoc = null;
        this.mPostTreeAction = null;
        this.mPointDelay = [];
        this.mErrorMode = false;
        this.mCounts = info["counts"];
        this.mPoints = info["points"];
        this.mMarkers = info["markers"];
        this._fillTreeTable();
        /*if (info["error"]) {
            this.mErrorMode = true;
            this.mCounts = [];
            this.mPoints = [];
            this.mMarkers = [];
            this._fillNoTree();
        }
        else {
        }*/
        
        point_no = 0;
        if (this.mCurPointNo && this.mCurPointNo >= 0) {
            if (this.mCurPointNo >= this.mPoints.length)
                point_no = this.mPoints.length - 1;
            else
                point_no = this.mCurPointNo;
        }
        this.mCurPointNo = null;
        this.selectPoint(point_no);
        
        sCodeEditH.setup(this.mTreeCode);
        arrangeControls();
        this.careControls();
        this.loadDelayed();
    },

    _fillTreeTable: function() {
        this.mAcceptedCount = 0;
        var list_rep = ['<table class="d-tree">'];
        for (var p_no = 0; p_no < this.mPoints.length; p_no++) {
            point = this.mPoints[p_no];
            p_kind = point[0];
            p_lev = point[1];
            p_decision = point[2];
            p_cond = point[3];
            p_html = point[4];
            p_count = this.mCounts[p_no];
            if (p_kind == "Import" || p_kind == "Error") {
                list_rep.push('<tr><td class="point-no">' + (p_no + 1) + '</td>' +
                    '<td class="point-code"><div class="highlight">' + p_html + '</div></td>' +
                    '<td class="point-count-undef">---</td></tr>');
                continue
            }
            list_rep.push('<tr id="p_td__' + p_no + 
                '" class="active" onclick="sDecisionTree.selectPoint(' + p_no + ');">');
            list_rep.push('<td class="point-no">' + (p_no + 1) + '</td>');
            list_rep.push('<td class="point-code"><div class="highlight">' +
                p_html + '</div></td>');
            if (p_count == null) {
                this.mPointDelay.push(p_no);
                count_repr = '<span id="p_count__' + p_no + '">...</span>';
            } else 
                count_repr = p_count;
            if (p_decision) {
                this.mAcceptedCount += p_count;
                list_rep.push('<td class="point-count-accept">+' + 
                    count_repr + '</td>');
            } else {
                if (p_decision == false) 
                    list_rep.push(
                        '<td class="point-count-reject">-' + count_repr + '</td>');
                else 
                    list_rep.push(
                        '<td class="point-count">' + count_repr + '</td>');
            }
            list_rep.push('</tr>');
        }
        list_rep.push('</table>'); 
        document.getElementById("decision-tree").innerHTML = list_rep.join('\n');
    },
    
    _fillNoTree: function() {
        this.mAcceptedCount = 0;
        document.getElementById("decision-tree").innerHTML = 
            '<div class="error">Tree code has errors, <br/>' +
            '<a onclick="sCodeEditH.show();">Edit</a> ' +
            'or choose another code from repository</div>';
    },

    getTreeRqArgs: function(no_comp) {
        args = "ds=" + sDSName + "&no=" + 
            ((this.mCurPointNo == null)? -1:this.mCurPointNo)  +
            "&code=" + encodeURIComponent(this.mTreeCode);
        return args;
    },
    
    loadDelayed: function(post_tree_action) {
        if (this.mPointDelay.length == 0) {
            eval(post_tree_action);
            return;
        }
        var args = this.getTreeRqArgs() +
            "&points=" + encodeURIComponent(JSON.stringify(this.mPointDelay)) + 
            "&rq_id=" + encodeURIComponent(this.mRqId);
        if (!post_tree_action)
            args += "&tm=1";
        else
            this.mPostTreeAction = post_tree_action;
        ajaxCall("dtree_counts", args, function(info){sDecisionTree._loadDelayed(info);})
    },
    
    _loadDelayed: function(info) {
        if (info["rq_id"] != this.mRqId)
            return;
        for (var p_no = 0; p_no < info["counts"].length; p_no++) {
            p_count = info["counts"][p_no];
            if (p_count == null)
                continue;
            pos = this.mPointDelay.indexOf(p_no);
            if (pos < 0)
                continue;
            this.mPointDelay.splice(pos, 1);
            this.mCounts[p_no] = p_count;
            if (this.mPoints[p_no][2]) 
                this.mAcceptedCount += p_count;
            document.getElementById("p_count__" + p_no).innerHTML = "" + p_count;
        }
        this.careControls();
        if (this.mPointDelay.length > 0) {
            this.loadDelayed()
            return;
        }
        if (this.mPostTreeAction) {
            post_tree_action = this.mPostTreeAction;
            this.mPostTreeAction = null;
            eval(post_tree_action);
        }
    },
    
    careControls: function() {
        var accepted = this.getAcceptedCount();
        if (accepted != null) {
            rep_accepted = accepted;
            rep_rejected = this.mTotalCount - accepted;
        } else {
            rep_accepted = "?";
            rep_rejected = "?";
        }
        document.getElementById("report-accepted").innerHTML = rep_accepted;
        document.getElementById("report-rejected").innerHTML = rep_rejected;
    },
    
    selectPoint: function(point_no) {
        var pos = this.mPointDelay.indexOf(point_no);
        if ( pos > 0) {
            this.mPointDelay.splice(pos, 1);
            this.mPointDelay.splice(0, 0, point_no);
        }
        if (this.mCurPointNo == point_no) 
            return;
        if (sUnitsH.postAction(
            'sDecisionTree.selectPoint(' + point_no + ');', true))
            return;
        sViewH.modalOff();
        this._highlightCondition(false);
        this.mMarkLoc = null;
        if (point_no >= 0) {
            var new_el = document.getElementById("p_td__" + point_no);
            if (new_el == null) 
                return;
        }
        if (this.mCurPointNo != null && this.mCurPointNo >= 0) {
            var prev_el = document.getElementById("p_td__" + this.mCurPointNo);
            prev_el.className = "active";
        }
        this.mCurPointNo = point_no;
        if (point_no >= 0)
            new_el.className = "cur";
        sUnitsH.setup();
    },
    
    markEdit: function(point_no, marker_idx) {
        this.selectPoint(point_no);
        if (sUnitsH.postAction(
                'sDecisionTree.markEdit(' + point_no + ', ' + marker_idx + ');', true))
            return;
        this.mMarkLoc = [point_no, marker_idx];
        sOpCondH.show(this.mMarkers[point_no][marker_idx]);
        this._highlightCondition(true);
    },
    
    markRenewEdit: function() {
        if (this.mMarkLoc) 
            this.markEdit(this.mMarkLoc[0], this.mMarkLoc[1]);
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
        if (this.mMarkLoc != null)
            this.setup(true, {"instr": 
                JSON.stringify(["EDIT", "mark", this.mMarkLoc, new_cond])});
    },
    
    getAcceptedCount: function() {
        if (this.mPointDelay.length > 0)
            return null;
        return this.mAcceptedCount;
    },
    
    hasError: function() {
        return this.mErrorMode;
    },
    
    getTotalCount: function() {
        return this.mTotalCount;
    },
    
    getTreeCode: function() {
        return this.mTreeCode;
    },
    
    getCurPointNo: function() {
        return this.mCurPointNo;
    },
    
    clear: function() {
        this.setup("return False");
    },
    
    isEmpty: function() {
        return (this.mPoints.length < 2);
    }
}

/**************************************/
var sUnitsH = {
    mDivList: null,
    mItems: null,
    mCount: null,
    mTotal: null,
    mUnitMap: null,
    mCurUnit: null,
    mCurZygName: null,
    mWaiting: false,
    mPostAction: null,
    mCtx: {},
    mRqId: null,
    mUnitsDelay: null,
    mTimeH: null,
    
    init: function() {
        this.mDivList = document.getElementById("stat-list");
    },
    
    setup: function() {
        var args = sDecisionTree.getTreeRqArgs() + "&tm=0" +
            "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
        this.mRqId = false;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDivList.className = "wait";
        this.mWaiting = true;
        ajaxCall("dtree_stat", args, function(info){sUnitsH._setup(info);})
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
        this.mWaiting = false;
        this.mRqId  = info["rq_id"];
        this.mCount = info["count"];
        this.mTotal = info["total"];
        document.getElementById("list-report").innerHTML = (this.mCount == this.mTotal)?
            this.mTotal : this.mCount + "/" + this.mTotal;
        sSubVRecH.reset(this.mCount);
            
        this.mItems = info["stat-list"].slice();
        this.mUnitMap = {};
        this.mUnitsDelay = [];
        var list_stat_rep = [];
        fillStatList(this.mItems, this.mUnitMap, list_stat_rep, this.mUnitsDelay, 1);
        this.mDivList.className = "";
        this.mDivList.innerHTML = list_stat_rep.join('\n');
        this.mCurUnit = null;        
        
        if (this.mCurUnit == null)
            this.selectUnit(this.mItems[0][1]["name"]);
        
        this.checkDelayed();
    },

    checkDelayed: function() {
        var post_action = this.mPostAction;
        this.mPostAction = null;
        if (post_action)
            eval(post_action);
        if (this.mWaiting || this.mTimeH != null || this.mUnitsDelay.length == 0)
            return;
        this.mTimeH = setInterval(function(){sUnitsH.loadUnits();}, 50);
    },
    
    getRqArgs: function(no_ctx) {
        ret = sDecisionTree.getTreeRqArgs(no_ctx);
        if (!no_ctx)
            ret += "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
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
            "&tm=1" + "&rq_id=" + encodeURIComponent(this.mRqId) + 
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
        el_list = document.getElementById("stat-list");
        var cur_el = (this.mCurUnit)? this._unitDivEl(this.mCurUnit): null;
        if (cur_el)
            var prev_top = cur_el.getBoundingClientRect().top;
        var prev_unit = this.mCurUnit;
        var prev_h =  (this.mCurUnit)? topUnitStat(this.mCurUnit):null;
        for (var idx = 0; idx < info["units"].length; idx++) {
            unit_stat = info["units"][idx];
            refillUnitStat(unit_stat, 1);
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
            sOpCondH.checkDelay(unit_name);
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
    
    getUnitStat: function(unit_name) {
        this.checkUnitDelay(unit_name);
        return this.mItems[this.mUnitMap[unit_name]];
    },
    
    checkUnitDelay: function(unit_name) {
        var pos = this.mUnitsDelay.indexOf(unit_name);
        if (pos >= 0) {
            this.mUnitsDelay.splice(pos, 1);
            this.mUnitsDelay.splice(0, 0, unit_name);
        }
        if (pos >= 0) 
            this.checkDelayed();
    },
    
    selectUnit: function(stat_unit, force_it) {
        this.checkUnitDelay(stat_unit);
    },
    
    updateZygUnit: function(zyg_name) {
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
        accepted = sDecisionTree.getAcceptedCount();
        if (accepted == null) {
            sDecisionTree.loadDelayed("sCreateWsH.show();");
            return null;
        }
        return [sDecisionTree.getAcceptedCount(), sDecisionTree.getTotalCount()];
    },
    
    getWsCreateArgs: function() {
        return "ds=" + sDSName + "&code=" + encodeURIComponent(sDecisionTree.mTreeCode);
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
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mNewCondition: null,
    mButtonSet: null,
    mCurUnitName: null,

    init: function() {
        this.mButtonSet   = document.getElementById("cond-button-set");
    },
    
    checkDelay: function(unit_name) {
        if (unit_name == this.mCurUnitName && 
                document.getElementById("cur-cond-back").style.display != "none")
            this.show(this.mCondition);
    },
    
    show: function(condition) {
        this.mCondition = condition;
        this.mNewCondition = null;
        this.mCurUnitName = this.mCondition[1];
        document.getElementById("cond-title").innerHTML = this.mCurUnitName;
        unit_stat = sUnitsH.getUnitStat(this.mCurUnitName);
        unit_type = unit_stat[0];
        mode = "num";
        if (unit_stat.length == 2) {
            this.mCurTpHandler = null;
        } else {
            if (unit_type == "int" || unit_type == "float") 
                this.mCurTpHandler = sOpNumH;
            else {
                if (sOpEnumH.readyForCondition(unit_stat, this.mCondition)) {
                    this.mCurTpHandler = sOpEnumH;
                    mode = "enum";
                } else {
                    this.mCurTpHandler = null;
                }
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
            this.mCurTpHandler.updateCondition(this.mCondition);
            this.mCurTpHandler.checkControls();
        }
        document.getElementById("cur-cond-mod").className = mode;
        sViewH.modalOn(document.getElementById("cur-cond-back"), "flex");
        arrangeControls();
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

/*************************************/
var sDTreesH = {
    mTimeH: null,
    mCurOp: null,
    mSelName: null,
    mComboName: null,
    mCurDTreeName: null,
    mBtnOp: null,
    
    mAllList: [],
    mOpList: [],
    mLoadList: [],
    mDTreeTimeDict: null,

    init: function() {
        this.mInpName   = document.getElementById("dtree-name-input");
        this.mSelName   = document.getElementById("dtree-name-combo-list");
        this.mComboName = document.getElementById("dtree-name-combo");
        this.mBtnOp     = document.getElementById("dtree-act-op");
    },

    setup: function(dtree_name, dtree_list) {
        this.mCurDTreeName = dtree_name;
        var prev_all_list = JSON.stringify(this.mAllList);
        this.mOpList = [];
        this.mLoadList = [];
        this.mAllList = [];
        this.mDTreeTimeDict = {};
        for (idx = 0; idx < dtree_list.length; idx++) {
            dtree_name = dtree_list[idx][0];
            this.mAllList.push(dtree_name);
            if (!dtree_list[idx][1])
                this.mOpList.push(dtree_name);
            if (dtree_list[idx][2])
                this.mLoadList.push(dtree_name);
            this.mDTreeTimeDict[dtree_name] = dtree_list[idx][3];
        }
        //if (prev_all_list != JSON.stringify(this.mAllList))
        //    onDTreeListChange();
        this.update();
    },
    
    update: function() {
        this.mCurOp = null;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        if (!this.mCurDTreeName) {
            this.mComboName.style.display = "none";
            this.mInpName.value = "";
        } else {
            this.mInpName.value = this.mCurDTreeName;
            this.mInpName.disabled = true;
            this.mSelName.disabled = true;
            this.mComboName.style.display = "block";
        }
        this.mInpName.style.visibility = "visible";
        document.getElementById("dtree-op-create").className = 
            (!!this.mCurDTreeName)? "disabled":"";
        document.getElementById("dtree-op-modify").className = 
            (!!this.mCurDTreeName ||
                (this.mOpList.length == 0))? "disabled":"";
        document.getElementById("dtree-op-delete").className = 
            (!this.mCurDTreeName || 
                this.mOpList.indexOf(this.mCurDTreeName) < 0)? "disabled":"";
        this.mBtnOp.style.display = "none";
    },

    checkName: function() {
        if (this.mCurOp == null)
            return;

        dtree_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(dtree_name) >= 0;
        q_op  = this.mOpList.indexOf(dtree_name) >= 0;
        q_load = this.mLoadList.indexOf(dtree_name) >= 0;
        
        if (this.mCurOp == "modify") {
            this.mBtnOp.disabled = (!q_op) || dtree_name == this.mCurDTreeName;
            return;
        }
        if (this.mCurOp == "load") {
            this.mBtnOp.disabled = (!q_load) || dtree_name == this.mCurDTreeName;
            return;
        }
        
        if (this.mCurOp != "create") {
            return; /*assert false! */
        }
        
        q_ok = (q_all)? false: checkIdentifier(dtree_name);
        
        this.mInpName.className = (q_ok)? "": "bad";
        this.mBtnOp.disabled = !q_ok;
        
        if (this.mTimeH == null) 
            this.mTimeH = setInterval(function(){sDTreesH.checkName();}, 100);
    },
    
    dtreeExists: function(dtree_name) {
        return this.mAllList.indexOf(dtree_name) >= 0;
    },
    
    select: function() {
        this.mInpName.value = this.mSelName.value;
        this.checkName();
        //if (this.mCurOp == "load" || this.mCurOp == "modify")
        //    this.action();
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
        if (sDecisionTree.isEmpty())
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
        if (sDecisionTree.isEmpty() || !this.mCurDTreeName)
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
        if (!this.mCurDTreeName || 
                this.mOpList.indexOf(this.mCurDTreeName) < 0)
            return;
        sDecisionTree.setup(true, 
            {"instr": JSON.stringify(["DELETE", this.mCurDTreeName])});
    },

    action: function() {
        dtree_name = this.mInpName.value;
        q_all = this.mAllList.indexOf(dtree_name) >= 0;
        q_op = this.mOpList.indexOf(dtree_name) >= 0;
        q_load = this.mLoadList.indexOf(dtree_name) >= 0;
        
        switch (this.mCurOp) {
            case "create":
                if (!q_all && checkIdentifier(dtree_name)) {
                    sDecisionTree.setup(true,
                        {"instr": JSON.stringify(["UPDATE", dtree_name])});
                }
                break;
            case "modify":
                if (q_op && dtree_name != this.mCurDTreeName) {
                    sDecisionTree.setup(true,
                        {"instr": JSON.stringify(["UPDATE", dtree_name])});
                }
                break;
            case "load":
                if (q_load && dtree_name != this.mCurDTreeName) {
                    sDecisionTree.setup(false,
                        {"dtree": dtree_name});
                }
                break;
        }
    },

    fillSelNames: function(with_empty, dtree_list) {
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
        for (idx = 0; idx < dtree_list.length; idx++) {
            dtree_name = dtree_list[idx];
            var option = document.createElement('option');
            option.innerHTML = dtree_name;
            option.value = dtree_name;
            this.mSelName.append(option)
        }
        this.mSelName.selectedIndex = 0;
    },
    
    getAllList: function() {
        return this.mAllList;
    }
};

/**************************************/
var sHistoryH = {
    mHistory: [],
    mRedoStack: [],
    mCurVersion: null,
    
    mButtonUndo: null,
    mButtonRedo: null,

    init: function() {
        this.mButtonUndo = document.getElementById("dtree-undo");
        this.mButtonRedo = document.getElementById("dtree-redo");
        
    },
    
    _curState: function() {
        return [sDecisionTree.mCurPointNo, 
            this.mCurVersion[0], this.mCurVersion[1]];
    },
    
    update: function(hash_code) {
        if (this.mCurVersion == null || hash_code != this.mCurVersion[1]) {
            if (this.mCurVersion != null) {
                this.mHistory.push(this._curState());
                while (this.mHistory.length > 50)
                    this.mHistory.shift();
                this.mRedoStack = [];
            }
            this.mCurVersion = [sDecisionTree.mTreeCode, hash_code];
        }
        this.mButtonUndo.disabled = (this.mHistory.length == 0);
        this.mButtonRedo.disabled = (this.mRedoStack.length == 0);
    },
    
    doUndo: function() {
        if (this.mHistory.length > 0) {
            this.mRedoStack.push(this._curState());
            state = this.mHistory.pop()
            sDecisionTree.mCurPointNo = state[0];
            this.mCurVersion = [state[1], state[2]];
            sDecisionTree.setup(state[1]);
        }
    },

    doRedo: function() {
        if (this.mRedoStack.length > 0) {
            this.mHistory.push(this._curState());
            state = this.mRedoStack.pop()
            sDecisionTree.mCurPointNo = state[0];
            this.mCurVersion = [state[1], state[2]];
            sDecisionTree.setup(state[1]);
        }
    },
    
    availableActions: function() {
        var ret = [];
        if (this.mHistory.length > 0)
            ret.push("undo");
        if (this.mRedoStack.length > 0)
            ret.push("redo");
        return ret;
    }
};

/*************************************/
var sCodeEditH = {
    mBaseContent: null,
    mCurContent: null,
    mCurError: false,
    mButtonShow: null,
    mButtonDrop: null,
    mButtonSave: null,
    mSpanPos: null,
    mSpanError: null,
    mAreaContent: null,
    mErrorPos: null,
    mTimeH: null,
    mWaiting: null,
    mNeedsSave: null,
    
    init: function() {
        this.mButtonShow = document.getElementById("code-edit-show");
        this.mButtonDrop = document.getElementById("code-edit-drop");
        this.mButtonSave = document.getElementById("code-edit-save");
        this.mSpanPos = document.getElementById("code-edit-pos");
        this.mSpanError = document.getElementById("code-edit-error");
        this.mAreaContent = document.getElementById("code-edit-content");
    },
    
    setup: function(tree_code) {
        this.mBaseContent = tree_code;
        this.mAreaContent.value = this.mBaseContent;
        this.mCurContent = this.mBaseContent;
        this.mCurError = false;
        this.mErrorPos = null;
        this.mWaiting = false;
        this.mNeedsSave = false;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.validateContent(this.mBaseContent);
        this.checkControls();
    },
    
    checkControls: function() {
        var same_cnt = (this.mBaseContent == this.mCurContent);
        this.mButtonShow.innerText = (same_cnt)? "Edit code":"Continue edit code"; 
        this.mButtonShow.setAttribute("class", (this.mCurError)? "bad":"");
        this.mButtonDrop.disabled = same_cnt;
        this.mButtonSave.disabled = same_cnt|| this.mCurError; 
        this.mSpanError.innerHTML = (this.mCurError)? this.mCurError:"";
    },
    
    show: function() {
        sViewH.modalOn(document.getElementById("code-edit-back"));
    },

    validateContent: function(code_content) {
        if (this.mCurError != false && this.mCurContent == code_content) {
            this.checkControls();
            return;
        }
        if (this.mTimeH != null)
            clearInterval(this.mTimeH);
        this.mCurContent = code_content;
        this.mTimeH = setInterval(function(){sCodeEditH.validation();}, 300);
    },
    
    validation: function() {
        clearInterval(this.mTimeH);
        this.mTimeH = null;
        this.mCurError = false;
        this.mErrorPos = null;
        this.mWaiting = true;
        ajaxCall("dtree_check", "ds=" + sDSName + "&code=" +
            encodeURIComponent(this.mCurContent), 
            function(info) {sCodeEditH._validation(info);});
    },
    
    _validation: function(info) {
        this.mCurContent = info["code"];
        this.mWaiting = false;
        if (info["error"]) {
            this.mCurError = "At line " + info["line"] + 
                " pos " + (info["pos"] + 1) + ": " +
                info["error"];
            this.mErrorPos = [info["line"], info["pos"]];
        } else {
            this.mCurError = null;
            this.mErrorPos = null;
        }
        this.checkControls();
        if (this.mNeedsSave) {
            this.mNeedsSave = false;
            if (this.setupContent()) 
                sViewH.modalOff();
        }
    },
    
    posError: function() {
        if (this.mErrorPos == null) 
            return;
        var content = this.mCurContent;
        var nlines = this.mErrorPos[0];
        var idx = 0;
        while (nlines > 1) {
            idx = content.indexOf('\n', idx);
            if (idx < 0)
                return;
            idx++;
            nlines--;
        }
        idx += this.mErrorPos[1];
        var a_c = this.mAreaContent;
        setTimeout(function() {  
            a_c.selectionStart = idx; a_c.selectionEnd = idx; a_c.focus()}, 1);
    },
    
    drop: function() {
        this.mAreaContent.value = this.mBaseContent;
        this.validateContent(this.mBaseContent);
        sViewH.modalOff();
    },
    
    checkContent: function() {
        this.validateContent(this.mAreaContent.value);
    }, 
    
    save: function() {
        this.mNeedsSave = true;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
        }
        if (!this.mWaiting)
            this.validation();            
    },
    
    setupContent: function() {
        var ret = this.mCurError == null && this.mBaseContent != this.mCurContent;
        if (ret)
            sDecisionTree.setup(this.mCurContent);
        this.checkControls();
        return ret;
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
    
    init: function() {
        this.mDivVersionTab = document.getElementById("cmp-code-tab");
        this.mDivVersionCmp = document.getElementById("cmp-code-cmp");
        this.mButtonVersionSelect = document.getElementById("btn-version-select");
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
            sViewH.modalOn(document.getElementById("cmp-code-back"));
    },
    
    checkControls: function(){
        this.mButtonVersionSelect.disabled = (this.mCurCmpVer == null);
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
            var args = "ds=" + sDSName + "&ver=" + this.mCurCmpVer;
            if (this.mBaseCmpVer == null) 
                args += "&code=" + encodeURIComponent(sDecisionTree.mTreeCode);
            else
                args += "&verbase=" + this.mBaseCmpVer;
            ajaxCall("dtree_cmp", args, function(info){sVersionsH._setCmp(info);});
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
    }
};

/**************************************/
function arrangeControls() {
    el_cond_mod = document.getElementById("cur-cond-mod");
    if (el_cond_mod.className == "enum") {
        cond_mod_height = el_cond_mod.offsetHeight;
        el_zyp_problem = document.getElementById("cur-cond-zyg-problem-group");
        if (el_zyp_problem.style.display != "none") 
            cond_mod_height -= el_zyp_problem.getBoundingClientRect().height;
        document.getElementById("wrap-cond-enum").style.height = 
            Math.max(10, cond_mod_height - 110);
    }
    sSubVRecH.arrangeControls();
}

function onKey(key_event) {
    sSubVRecH.onKey(key_event);
}

function onModalOff() {
    sDecisionTree._highlightCondition(false);
}

function updateZygCondStat(unit_name) {
    sDecisionTree.markRenewEdit();
}

function fixMark() {
    sOpCondH.editMarkCond();
    sViewH.modalOff();
}

function versionSelect() {
    sVersionsH.selectVersion();
}

function editMark(point_no, instr_idx) {
    sDecisionTree.markEdit(point_no, instr_idx);
}

function exposeEnum(unit_name, expand_mode) {
    exposeEnumUnitStat(sUnitsH.getUnitStat(unit_name), expand_mode);
}
