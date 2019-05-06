var sDSName = null;
var sTitlePrefix = null;
var sCommonTitle = null;
var sWsURL = null;

/*************************************/
function initXL(ds_name, common_title, ws_url) {
    sUnitsH.init();
    sOpCondH.init();
    sOpNumH.init();
    sOpEnumH.init();
    sTreeCtrlH.init();
    sVersionsH.init();
    sViewH.init();
    sCreateWsH.init();
    sCodeEditH.init();
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    sCommonTitle = common_title;
    sWsURL = ws_url;
    sDSName = ds_name; 
    window.onresize  = updateSizes;
    window.name = sCommonTitle + ":" + sDSName + ":L";
    document.title = sTitlePrefix + "/" + sDSName;
    document.getElementById("xl-name").innerHTML = sDSName;
    sDecisionTree.setup();
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
    mErrorMode: null,
    
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
        sTreeCtrlH.update(info["cur_version"], info["versions"]);
        document.getElementById("std-code-select").value = 
            info["std_code"]? info["std_code"]:"";
        this.mMarkLoc = null;
        if (info["error"]) {
            this.mErrorMode = true;
            this.mCounts = [];
            this.mPoints = [];
            this.mMarkers = [];
            this._fillNoTree();
        }
        else {
            this.mErrorMode = false;
            this.mCounts = info["counts"];
            this.mPoints = info["points"];
            this.mMarkers = info["markers"];
            this._fillTreeTable();
        }
        
        point_no = (this.mCurPointNo && this.mCurPointNo>0)? this.mCurPointNo: 0;
        while (point_no >= 0) {
            if (point_no >= this.mPoints.length || this.mCounts[point_no] == 0)
                point_no--;
            else
                break;
        }
        this.mCurPointNo = null;
        this.selectPoint(point_no);
        
        document.getElementById("report-accepted").innerHTML =  
            (this.mErrorMode)? "?" : ("" + this.mAcceptedCount);
        if (this.mErrorMode)
            rep_rejected = "?"
        else
            rep_rejected = this.mTotalCount - this.mAcceptedCount;
        document.getElementById("report-rejected").innerHTML = rep_rejected;
        sCodeEditH.setup(this.mTreeCode);
        updateSizes();
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
    },
    
    _fillNoTree: function() {
        this.mAcceptedCount = 0;
        document.getElementById("decision-tree").innerHTML = 
            '<div class="error">Tree code has errors, <br/>' +
            '<a onclick="sCodeEditH.show();">Edit</a> ' +
            'or choose another code from repository</div>';
    },
    
    selectPoint: function(point_no) {
        if (this.mCurPointNo == point_no) 
            return;
        if (point_no >=0 && this.mCounts[point_no] == 0)
            return;
        if (sUnitsH.postAction(
            'sDecisionTree.selectPoint(' + point_no + ');', true))
            return;
        sViewH.modalOff();
        this._highlightCondition(false);
        this.mOpCond = null;
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
        sUnitsH.setup(this.mTreeCode, this.mCurPointNo);
    },
    
    markEdit: function(point_no, marker_idx) {
        this.selectPoint(point_no);
        if (sUnitsH.postAction(
                'sDecisionTree.markEdit(' + point_no + ', ' + marker_idx + ');', true))
            return;
        if (this.mCurPointNo != point_no || this.mCurPointNo < 0)
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
    },
    
    getTreeCode: function() {
        return this.mTreeCode;
    }
}

/**************************************/
var sUnitsH = {
    mDivList: null,
    mItems: null,
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
    
    setup: function(tree_code, point_no) {
        args = "ds=" + sDSName + "&code=" + encodeURIComponent(tree_code) + 
            "&no=" + point_no + "&tm=0" +
            "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx));
        this.mRqId = false;
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDivList.className = "wait";
        this.mWaiting = true;
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
        this.mWaiting = false;
        this.mRqId  = info["rq_id"];
        count = info["count"];
        total = info["total"];
        document.getElementById("list-report").innerHTML = (count == total)?
            total : count + "/" + total;
            
        this.mItems = info["stat-list"];
        this.mUnitMap = {};
        this.mUnitsDelay = [];
        var list_stat_rep = [];
        fillEnumStat(this.mItems, this.mUnitMap, list_stat_rep, this.mUnitsDelay);
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
    
    loadUnits: function() {
        clearInterval(this.mTimeH);
        this.mTimeH = null;
        if (this.mWaiting || this.mUnitsDelay.length == 0)
            return;
        this.mWaiting = true;
        
        ajaxCall("xl_statunits", "ds=" + sDSName + "&tm=1" +
            "&rq_id=" + encodeURIComponent(this.mRqId) + 
            "&ctx=" + encodeURIComponent(JSON.stringify(this.mCtx)) +
            "&units=" + encodeURIComponent(JSON.stringify(this.mUnitsDelay.splice(0, 1))) +
            "&code=" + encodeURIComponent(sDecisionTree.getTreeCode()) + 
            "&no=" + point_no, 
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
            this.selectUnit(this.mCurUnit, true);
        }
    },
    
    setCtxPar: function(key, val) {
        this.mCtx[key] = val;
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
            if (unit_type == "long" || unit_type == "float") 
                this.mCurTpHandler = sOpNumH;
            else {
                this.mCurTpHandler = sOpEnumH;
                mode = "enum";
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
        updateSizes();
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
        if (this.mCurPointNo < 0)
            return;
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
        this.validateContent(this.mBaseContent);
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
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
        ajaxCall("xltree_code", "ds=" + sDSName + "&code=" +
            encodeURIComponent(this.mCurContent), 
            function(info) {sCodeEditH._validation(info);});
    },
    
    _validation: function(info) {
        if (info["code"] != this.mCurContent) 
            return;
        this.mWaiting = false;
        if (info["error"]) {
            this.mCurError = "At line " + info["line"] + " pos " + info["pos"] + ": " +
                info["error"];
            this.mErrorPos = [info["line"], info["pos"]];
        } else {
            this.mCurError = null;
            this.mErrorPos = null;
        }
        this.checkControls();
        if (this.mNeedsSave) {
            this.mNeedsSave = false;
            this.setupContent();
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
        if (this.mCurError == null && this.mBaseContent != this.mCurContent)
            sDecisionTree.setup(this.mCurContent);
        this.checkControls();
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
    if (!sTreeCtrlH.curVersionSaved()) {
        sUnitsH.postAction("sCreateWsH.show();");
        treeVersionSave();
        return null;
    }
    return [sDecisionTree.getAcceptedCount(), sDecisionTree.getTotalCount()];
}

function _callWsArgs() {
    return "&verbase= " + sTreeCtrlH.getCurVersion();
}

/**************************************/
function updateSizes() {
    el_cond_mod = document.getElementById("cur-cond-mod");
    if (el_cond_mod.className == "enum") {
        cond_mod_height = el_cond_mod.offsetHeight;
        el_zyp_problem = document.getElementById("cur-cond-zyg-problem-group");
        if (el_zyp_problem.style.display != "none") 
            cond_mod_height -= el_zyp_problem.getBoundingClientRect().height;
        document.getElementById("wrap-cond-enum").style.height = 
            Math.max(10, cond_mod_height - 110);
    }
}

function onModalOff() {
    sDecisionTree._highlightCondition(false);
}

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

function editMark(point_no, instr_idx) {
    sDecisionTree.markEdit(point_no, instr_idx);
}

function pickStdCode() {
    std_name = document.getElementById("std-code-select").value;
    if (std_name) 
        sDecisionTree.setup(null, {"std" : std_name});
}