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
    window.name = sCommonTitle + ":" + sDSName + ":DTREE";
    document.getElementById("ds-name").innerHTML = sDSName;
    
    setupDSControls();
    sUnitsH.init();
    sOpCondH.init();
    sHistoryH.init();
    sVersionsH.init();
    sCodeEditH.init();
    sDTreesH.init();
    sDecisionTree.clear();
    sViewH.addNotifier(sDecisionTree);
    sTraceDTreeH.init();
}
    
function viewRejectionMode() {
    return sDecisionTree.viewRejectionMode();
}
    
/**************************************/
var sDecisionTree = {
    mTreeCode: null,
    mTreeName: null,
    mPoints: null,
    mCondAtoms: null,
    mPointCounts: null,
    mTotalCounts: null,
    mEvalState: null,
    mAcceptedCounts: null,
    mCurPointNo: null,
    mCondAtomLoc: null,
    mErrorMode: null,
    mPointDelay: null,
    mRqId: null,
    mPostTreeAction: null,
    
    setup: function(tree_code, instr, dtree_name) {
        args = "ds=" + sDSName + "&tm=0&actsym=1";
        if (tree_code == true)
            tree_code = this.mTreeCode;
        if (tree_code != false)
            args += "&code=" + encodeURIComponent(tree_code);
        if (instr)
            args += "&instr=" + encodeURIComponent(JSON.stringify(instr));
        if (dtree_name)
            args += "&dtree=" + encodeURIComponent(dtree_name)
        ajaxCall("dtree_set", args, function(info){sDecisionTree._setup(info);})
    },
    
    makeArgs: function() {
        args = "ds=" + sDSName;
        if (this.mTreeName)
            args += "&dtree=" + encodeURIComponent(this.mTreeName);
        else            
            args += "&code=" + encodeURIComponent(this.mTreeCode);
        return args;
    },
    
    _setup: function(info) {
        this.mTreeCode = info["code"];
        this.mTreeName = info["dtree-name"];
        this.mTotalCounts = info["total-counts"];
        this.mRqId = info["rq-id"];
        this.mEvalStatus = info["eval-status"];
        sDTreesH.setup(this.mTreeName, info["dtree-list"]);
        sHistoryH.update(info["hash"]);
        this.mCondAtomLoc = null;
        this.mPostTreeAction = null;
        this.mPointDelay = [];
        this.mErrorMode = false;
        this.mPointCounts = info["point-counts"];
        this.mPoints = info["points"];
        this.mCondAtoms = info["cond-atoms"];
        this._fillTreeTable();
        
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

    _renderCounts: function(counts) {
        c_repr = "" + counts[0];
        if (counts.length > 1 && counts[0] > 0) {
            c_repr += '<div class="tr-count">&#x00D7;&thinsp;' + 
                counts[2] + ' &#x21C9;&thinsp;' + counts[1] + '</div>';
        }
        return c_repr;
    },                
    
    _renderInstrMenu: function(p_no, point) {
        var menu_rep = ['<div class="instr-dropdown"><span>' + 
                (p_no + 1) + '</span>',
            '<div class="instr-dropdown-content">'];
        for (var idx = 0; idx < point["actions"].length; idx++) {
            action = point["actions"][idx];
            q_disable = false;
            switch(action) {
                case "join-and":
                    title = "Join as AND";
                    break;
                case "join-or":
                    title = "Join as OR";
                    break;
                case "bool-true":
                    q_disable = point["decision"]; 
                    title = ((q_disable)? '&#x2713;':'&emsp;') + "True";
                    break;
                case "bool-false":
                    q_disable = !point["decision"];
                    title = ((!q_disable)? '&emsp;':'&#x2713;') + "False";
                    break;
                default:          
                    title = action.charAt(0).toUpperCase() + action.slice(1);
            }
            if (q_disable)
                menu_rep.push('<a class="disabled">' + title + '</a>');
            else
                menu_rep.push('<a onclick="sDecisionTree.instrAction(\'' + 
                    action  + '\', ' + p_no + ');">' + title + '</a>');
        }
        menu_rep.push('</div></div');
        return menu_rep.join('\n');
    },
    
    _fillTreeTable: function() {
        this.mAcceptedCounts = (this.mTotalCounts.length > 1)? [0, 0] : [0];
        var list_rep = [sDTreesH.getCurUpdateReport(this.mEvalStatus)];
        
        list_rep.push('<table class="d-tree">');
        for (var p_no = 0; p_no < this.mPoints.length; p_no++) {
            point = this.mPoints[p_no];
            p_count = this.mPointCounts[p_no];
            if (point["kind"] == "Label" || point["kind"] == "Error") {
                list_rep.push('<tr><td class="point-count undef">---</td>');
                list_rep.push('<td class="point-no">' + 
                    this._renderInstrMenu(p_no, point) + '</td>');
                list_rep.push('<td class="point-code"><div class="highlight">' + 
                    point["code-frag"] + '</div></td></tr>');
                continue
            }
            list_rep.push('<tr id="p_td__' + p_no + 
                '" class="active" onclick="sDecisionTree.selectPoint(' + p_no + ');">');
            if (p_count == null) {
                this.mPointDelay.push(p_no);
                count_repr = '<span id="p_count__' + p_no + '">...</span>';
            } else {
                count_repr = this._renderCounts(p_count);
                if (point["decision"]) {
                    this.mAcceptedCounts[0] += p_count[0];
                    if (p_count.length > 1)
                        this.mAcceptedCounts[1] += p_count[1];
                }
            }
            mode = "";
            sign_mode = "";
            if (point["decision"]) {
                mode = " accept";
                sign_mode = "+";
            } else {
                if (point["decision"] == false) { 
                    mode = " reject"
                    sign_mode = "-";
                }
            }
            meta_mark = "";
            if (point["meta-err"]) {
                meta_mark = '<div class="point-count-warn" title="' +
                    point["meta-err"][0].replace(/"/g, '&quot;') + '">&#x2699;</div> ';
            }
            
            list_rep.push('<td class="point-count' + mode + '">' + 
                meta_mark + sign_mode + count_repr + '</td>');
                list_rep.push('<td class="point-no">' + 
                    this._renderInstrMenu(p_no, point) + '</td>');
            list_rep.push('<td class="point-code"><div class="highlight">' +
                point["code-frag"] + '</div></td>');
            list_rep.push('</tr>');
        }
        list_rep.push('</table>'); 
        document.getElementById("decision-tree").innerHTML = list_rep.join('\n');

        var seq_el = document.getElementsByClassName("dtree-atom-mark");
        for (j = 0; j < seq_el.length; j++) {
            seq_el[j].addEventListener("click", editAtom); 
            seq_el[j].innerHTML = "&#x2699;";
        }
        seq_el = document.getElementsByClassName("dtree-atom-drop");
        for (j = 0; j < seq_el.length; j++) {
            seq_el[j].addEventListener("click", dropAtom); 
            seq_el[j].innerHTML = "&times;";
        }
    },
    
    _fillNoTree: function() {
        this.mAcceptedCounts = [0];
        document.getElementById("decision-tree").innerHTML = 
            '<div class="error">Tree code has errors, <br/>' +
            '<a onclick="sCodeEditH.show();">Edit</a> ' +
            'or choose another code from repository</div>';
    },
    
    onModalOff: function() {
        this._highlightCondition(false);
    },

    getTreeRqArgs: function(use_id) {
        args = "ds=" + sDSName + "&no=" + 
            ((this.mCurPointNo == null)? -1:this.mCurPointNo)  +
            "&code=" + encodeURIComponent(this.mTreeCode);
        if (use_id)
            args += "&rq_id=" + encodeURIComponent(this.mRqId);
        return args;
    },
    
    loadDelayed: function(post_tree_action) {
        if (this.mPointDelay.length == 0) {
            eval(post_tree_action);
            return;
        }
        var args = this.getTreeRqArgs(true) +
            "&points=" + encodeURIComponent(JSON.stringify(this.mPointDelay));
        if (!post_tree_action)
            args += "&tm=1";
        else
            this.mPostTreeAction = post_tree_action;
        ajaxCall("dtree_counts", args, function(info){sDecisionTree._loadDelayed(info);})
    },
    
    _loadDelayed: function(info) {
        if (info["rq-id"] != this.mRqId)
            return;
        for (var p_no = 0; p_no < info["point-counts"].length; p_no++) {
            p_count = info["point-counts"][p_no];
            if (p_count == null)
                continue;
            pos = this.mPointDelay.indexOf(p_no);
            if (pos < 0)
                continue;
            this.mPointDelay.splice(pos, 1);
            this.mPointCounts[p_no] = p_count;
            if (this.mPoints[p_no]["decision"]) {
                this.mAcceptedCounts[0] += p_count[0];
                if (p_count.length > 1)
                    this.mAcceptedCounts[1] += p_count[1];
            }
            count_repr = this._renderCounts(p_count);
            document.getElementById("p_count__" + p_no).innerHTML = count_repr;
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
        var accepted = this.getAcceptedCounts();
        if (accepted != null) {
            rep_accepted = '' + accepted[0];
            if (accepted[0] > 0 && accepted.length > 1) 
                rep_accepted += ' <span class="tr-count">&#x21C9;&thinsp;' + 
                    accepted[1] + '</span>';
            rep_rejected = (this.mTotalCounts[0] - accepted[0]);
            if (accepted[0] < this.mTotalCounts[0] && accepted.length > 1)
                rep_rejected += ' <span class="tr-count">&#x21C9;&thinsp;' + 
                    (this.mTotalCounts[1] - accepted[1]) + '</span>';
        } else {
            rep_accepted = "?";
            rep_rejected = "?";
        }
        document.getElementById("report-accepted").innerHTML = rep_accepted;
        document.getElementById("report-rejected").innerHTML = rep_rejected;
    },
    
    deselectCurPoint: function() {
        if (this.mCurPointNo != null && this.mCurPointNo >= 0) {
            var prev_el = document.getElementById("p_td__" + this.mCurPointNo);
            prev_el.className = "";
        }
        this.mCurPointNo = null;
    },
    
    selectPoint: function(point_no) {
        var pos = this.mPointDelay.indexOf(point_no);
        if ( pos > 0) {
            this.mPointDelay.splice(pos, 1);
            this.mPointDelay.splice(0, 0, point_no);
        }
        if (this.mCurPointNo == point_no) 
            return;
        if (sEvalCtrlH.postAction(
            'sDecisionTree.selectPoint(' + point_no + ');', true))
            return;
        sViewH.modalOff();
        this._highlightCondition(false);
        this.mCondAtomLoc = null;
        if (point_no >= 0) {
            var new_el = document.getElementById("p_td__" + point_no);
            if (new_el == null) 
                return;
        }
        this.deselectCurPoint();
        this.mCurPointNo = point_no;
        if (point_no >= 0)
            new_el.className = "cur";
        sUnitsH.setup();
    },
    
    viewRejectionMode: function() {
        if (this.mCurPointNo !== null) {
            return (this.mPoints[this.mCurPointNo]["decision"] === false);
        }
        return false;
    },
    
    atomEdit: function(point_no, atom_idx) {
        this.selectPoint(point_no);
        if (sEvalCtrlH.postAction(
                'sDecisionTree.atomEdit(' + point_no + ', ' + atom_idx + ');', true))
            return;
        this.mCondAtomLoc = [point_no, atom_idx];
        this.showAtomCond();
        this._highlightCondition(true);
    },
    
    atomDrop: function(point_no, atom_idx) {
        this.selectPoint(point_no);
        if (sEvalCtrlH.postAction(
                'sDecisionTree.atomDrop(' + point_no + ', ' + atom_idx + ');', true))
            return;
        if (this.mCondAtoms[point_no].length > 1) {
            sDecisionTree.setup(true, ["ATOM", "DELETE", [point_no, atom_idx]]);
        } else {
            sDecisionTree.setup(true, ["INSTR", "DELETE", point_no]);
        }
    },
    
    atomRenewEdit: function() {
        if (this.mCondAtomLoc) 
            this.atomEdit(this.mCondAtomLoc[0], this.mCondAtomLoc[1]);
    },

    _highlightCondition(mode) {
        if (this.mCondAtomLoc == null)
            return;
        atom_el = document.getElementById(
            '__atom_' + this.mCondAtomLoc[0] + '-' + this.mCondAtomLoc[1]);
        if (mode)
            atom_el.className += " active";
        else
            atom_el.className = atom_el.className.replaceAll(" active", "");
    },
    
    getCurAtomLoc: function() {
        return this.mCondAtomLoc;
    },

    getCurAtomCond: function() {
        if (this.mCondAtomLoc == null)
            return null;
        return this.mCondAtoms[this.mCondAtomLoc[0]][this.mCondAtomLoc[1]];
    },

    showAtomCond: function() {
        var actions = ["atom-set"];
        if (this.mCondAtoms[this.mCondAtomLoc[0]].length > 1)
            actions.push("atom-delete");
        else
            actions.push("point-delete");
        sOpCondH.careButtons(actions);
        sOpCondH.show(this.getCurAtomCond());
    },    
    
    showUnitCond: function(unit_name) {
        if (this.mCurPointNo == null)
            return;
        cur_point = this.mPoints[this.mCurPointNo];
        var actions = null;
        if (cur_point["kind"] == "Return") {
            if (cur_point["level"] == 0)
                actions = ["point-insert"];
            else
                actions = ["point-up-join-and", 
                    "point-up-join-or", "point-up-replace"];
        } else {
            if (cur_point["kind"] == "If") 
                actions = ["point-replace", "point-insert", 
                    "point-join-and", "point-join-or"];
            else
                return;
        }
        sOpCondH.careButtons(actions);
        sOpCondH.show(null, unit_name);
    },    

    getAcceptedCounts: function() {
        if (this.mPointDelay.length > 0)
            return null;
        return this.mAcceptedCounts;
    },
    
    hasError: function() {
        return this.mErrorMode;
    },
    
    getTotalCount: function() {
        return this.mTotalCounts[0];
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
        return this.mPoints && (this.mPoints.length < 2);
    },
    
    instrAction: function(action, point_no) {
        this.selectPoint(point_no);
        this.setup(true, ["INSTR", action.toUpperCase(), point_no]);
    }
}

/**************************************/
var sUnitsH = {
    init: function() {
    },
    
    setup: function() {
        sEvalCtrlH.waitForSetup();
        var args = sDecisionTree.getTreeRqArgs() + "&tm=0";
        ajaxCall("dtree_stat", args, function(info){sUnitsH._setup(info);})
    },

    _setup: function(info) {
        var prev_cur_name = sEvalCtrlH.getCurUnitName();
        sEvalCtrlH._startSetup(info, sSubVRecH, 1, "sDecisionTree.showUnitCond");
        this.selectUnit(sEvalCtrlH.chooseCurName(prev_cur_name), true);
        sEvalCtrlH.checkDelayed();
    },

    getRqArgs: function(use_id) {
        ret = sDecisionTree.getTreeRqArgs();
        if (use_id)
            ret += sEvalCtrlH.argRqId();
        return ret;
    },
    
    loadUnits: function() {
        sEvalCtrlH.waitForLoad();
        ajaxCall("statunits", 
            this.getRqArgs(true) + "&tm=1" + sEvalCtrlH.argDelays(),
            function(info){sUnitsH._loadUnits(info);})
    },
    
    _loadUnits: function(info) {
        sEvalCtrlH.loadUnits(info, 1, sOpCondH);
    },
    
    selectUnit: function(stat_unit, force_it) {
        sEvalCtrlH.checkUnitDelay(stat_unit);
        sEvalCtrlH.setCurUnit(stat_unit);
        if (force_it == "func")
            sDecisionTree.showUnitCond(stat_unit);
    },
    
    selectFunction: function() {
        //TRF: write it
    },
    
    prepareWsCreate: function() {
        var accepted = sDecisionTree.getAcceptedCounts();
        if (accepted == null) {
            sDecisionTree.loadDelayed("sCreateWsH.show();");
            return null;
        }
        return [accepted[0], sDecisionTree.getTotalCount()];
    },
    
    getWsCreateArgs: function() {
        return "ds=" + sDSName + "&code=" + encodeURIComponent(sDecisionTree.mTreeCode);
    },

    infoIsUpToDate: function(info, force_it) {
        if (!sEvalCtrlH.checkRqId(info))
            return false;
        if (info["no"] == undefined && !force_it)
            return true;
        point_no = sDecisionTree.getCurPointNo();
        if (point_no == null)
            point_no = -1;
        return info["no"] == ("" + point_no);
    }
    
};
    
/**************************************/
var sOpCondH = {
    mCurTpHandler: null,
    mCondition: null,
    mNewCondition: null,
    mButtons: {},
    mCurUnitName: null,
    mActionList: ["atom-set", "atom-delete", "point-delete", 
        "point-insert", "point-replace", "point-join-and", "point-join-or", 
        "point-up-replace", "point-up-join-and", "point-up-join-or"],
    mCurActions: null,

    init: function() {
        for (idx = 0; idx < this.mActionList.length; idx++)
            this.mButtons[this.mActionList[idx]] =
                document.getElementById("cond-button-" + this.mActionList[idx]);
    },
    
    checkDelay: function(unit_name) {
        if (unit_name == this.mCurUnitName && 
                document.getElementById("cur-cond-back").style.display != "none")
            this.show(this.mCondition, this.mCurUnitName); 
    },

    careButtons: function(actions) {
        this.mCurActions = actions;
        for (idx = 0; idx < this.mActionList.length; idx++)
            this.mButtons[this.mActionList[idx]].style.display =
                (this.mCurActions.indexOf(this.mActionList[idx]) >= 0)?
                "inline" : "none";
    },
    
    show: function(condition, unit_name) {
        this.mCondition = condition;
        this.mNewCondition = null;
        if (this.mCondition != null)
            this.mCurUnitName = this.mCondition[1];
        else
            this.mCurUnitName = unit_name;
        unit_stat = sEvalCtrlH.getUnitStat(this.mCurUnitName);
        document.getElementById("cond-title").innerHTML = this.mCurUnitName + 
            ((unit_stat["kind"] == "func")? "()" : "");
        mode = "num";
        if (unit_stat === undefined || unit_stat["incomplete"]) {
            this.mCurTpHandler = null;
        } else {
            if (unit_stat["kind"] == "numeric") 
                this.mCurTpHandler = sOpNumH;
            else  {
                if (unit_stat["kind"] == "enum" || unit_stat["kind"] == "func") {
                    this.mCurTpHandler = sOpEnumH;
                    mode = "enum";
                } else {
                    this.mCurTpHandler = null;
                }
            }
        }
        sOpNumH.suspend();
        sOpEnumH.suspend();
        document.getElementById("cur-cond-loading").style.display = 
            (this.mCurTpHandler)? "none":"block";
        if (this.mCurTpHandler) {
            this.mCurTpHandler.updateUnit(unit_stat);
            if (this.mCondition)
                this.mCurTpHandler.updateCondition(this.mCondition);
            this.mCurTpHandler.checkControls();
        }
        document.getElementById("cur-cond-mod").className = mode;
        sViewH.modalOn(document.getElementById("cur-cond-back"), "flex");
        arrangeControls();
    },
    
    formCondition: function(condition_data, err_msg, add_always) {
        if (condition_data != null) {
            this.mNewCondition = [this.mCurTpHandler.getCondType(), 
                this.mCurUnitName].concat(condition_data);
        } else
            this.mNewCondition = null;
        message_el = document.getElementById("cond-message");
        message_el.innerHTML = (err_msg)? err_msg:"";
        message_el.className = (this.mNewCondition == null && 
            !err_msg.startsWith(' '))? "bad":"message";
        var no_action = (this.getNewCondition() == null);
        for (idx = 0; idx < this.mCurActions.length; idx++) {
            this.mButtons[this.mCurActions[idx]].disabled = 
                (this.mCurActions[idx].endsWith('-delete'))? false:no_action;
        }
    },
    
    getNewCondition: function() {
        if (!this.mNewCondition || 
                this.mNewCondition == this.mCondition)
            return null;
        return this.mNewCondition;
    },
    
    careControls: function() {
    }
};

/*************************************/
var sDTreesH = {
    mTimeH: null,
    mInpName: null,
    mListName: null,
    mComboName: null,
    mCurDTreeName: null,
    mCurDTreeInfo: null,
    mCurOp: null,
    mBtnOp: null,
    
    mAllNames: [],
    mOpNames: [],
    mDTreeTimeDict: null,

    init: function() {
        this.mInpName   = document.getElementById("dtree-name-input");
        this.mListName   = document.getElementById("dtree-name-combo-list");
        this.mComboName = document.getElementById("dtree-name-combo");
        this.mBtnOp     = document.getElementById("dtree-act-op");
    },

    setup: function(dtree_name, dtree_list) {
        this.mCurDTreeName = dtree_name;
        this.mCurDTreeInfo = null;
        var prev_all_list = JSON.stringify(this.mAllNames);
        this.mOpNames = [];
        this.mAllNames = [];
        this.mDTreeTimeDict = {};
        for (idx = 0; idx < dtree_list.length; idx++) {
            dtree_info = dtree_list[idx];
            if (dtree_info["name"] == this.mCurDTreeName)
                this.mCurDTreeInfo = dtree_info;
            this.mAllNames.push(dtree_info["name"]);
            if (!dtree_info["standard"])
                this.mOpNames.push(dtree_info["name"]);
            this.mDTreeTimeDict[dtree_info["name"]] = dtree_info["upd-time"];
        }
        //if (prev_all_list != JSON.stringify(this.mAllNames))
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
            this.mListName.disabled = true;
            this.mComboName.style.display = "block";
        }
        this.mInpName.style.visibility = "visible";
        document.getElementById("dtree-op-create").className = 
            (!!this.mCurDTreeName)? "disabled":"";
        document.getElementById("dtree-op-modify").className = 
            (!!this.mCurDTreeName ||
                (this.mCurDTreeName && this.mCurDTreeName[0] == '@' ||
                (this.mOpNames.length == 0)))? "disabled":"";
        document.getElementById("dtree-op-delete").className = 
            (!this.mCurDTreeName || 
                this.mOpNames.indexOf(this.mCurDTreeName) < 0)? "disabled":"";
        this.mBtnOp.style.display = "none";
    },

    getCurUpdateReport: function(eval_status) {
        if (this.mCurDTreeInfo == null && eval_status == "ok")
            return '';
        var ret = ['<div class="upd-note">'];
        if (eval_status == "fatal") {
            ret.push('<span class="bad">Conditions contain errors</span>');
        } else {
            if (eval_status == "runtime")
                ret.push('<span class="warn">Runtime problems</span>'); 
        }
        if (this.mCurDTreeInfo != null) {
            if (this.mCurDTreeInfo["upd-time"] != null) {
                ret.push('Updated at ' + 
                    timeRepr(this.mCurDTreeInfo["upd-time"]));
                if (this.mCurDTreeInfo["upd-from"] != sDSName) 
                    ret.push(' from ' + this.mCurDTreeInfo["upd-from"]);
            }
        }
        ret.push('</div>');
        return ret.join('\n');
    },
    
    checkSelection: function() {
        if (this.mCurOp == null)
            return;

        dtree_name = this.mInpName.value;
        q_all = this.mAllNames.indexOf(dtree_name) >= 0;
        q_op  = this.mOpNames.indexOf(dtree_name) >= 0;
        
        if (this.mCurOp == "modify") {
            this.mBtnOp.disabled = (!q_op) || dtree_name == this.mCurDTreeName;
            return;
        }
        if (this.mCurOp == "load") {
            this.mBtnOp.disabled = (!q_all) || dtree_name == this.mCurDTreeName;
            return;
        }
        
        if (this.mCurOp != "create") {
            return; /*assert false! */
        }
        
        q_ok = (q_all)? false: checkIdentifier(dtree_name);
        
        this.mInpName.className = (q_ok)? "": "bad";
        this.mBtnOp.disabled = !q_ok;
        
        if (this.mTimeH == null) 
            this.mTimeH = setInterval(function(){sDTreesH.checkSelection();}, 100);
    },
    
    dtreeExists: function(dtree_name) {
        return this.mAllNames.indexOf(dtree_name) >= 0;
    },
    
    select: function() {
        this.mInpName.value = this.mListName.value;
        this.checkSelection();
    },

    startLoad: function() {
        this.mCurOp = "load";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.fillSelNames(false, this.mAllNames, this.mCurDTreeName);
        this.mListName.disabled = false;
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
        this.mListName.disabled = false;
        this.mInpName.disabled = false;
        this.fillSelNames(true, this.mAllNames);
        this.mBtnOp.innerHTML = "Create";
        this.mBtnOp.style.display = "block";
        this.checkSelection();
        this.mComboName.style.display = "block";
    },

    startModify: function() {
        if (sDecisionTree.isEmpty() || 
            (this.mCurDTreeName && this.mCurDTreeName[0] == '@'))
            return;
        this.fillSelNames(false, this.mOpNames);
        this.mCurOp = "modify";
        this.mInpName.value = "";
        this.mInpName.style.visibility = "hidden";
        this.mListName.disabled = false;
        this.mBtnOp.innerHTML = "Modify";
        this.mBtnOp.style.display = "block";
        this.select();
        this.mComboName.style.display = "block";
    },

    deleteIt: function() {
        if (!this.mCurDTreeName || 
                this.mOpNames.indexOf(this.mCurDTreeName) < 0)
            return;
        sDecisionTree.setup(true, ["DTREE", "DELETE", this.mCurDTreeName]);
    },

    action: function() {
        dtree_name = this.mInpName.value;
        q_all = this.mAllNames.indexOf(dtree_name) >= 0;
        q_op = this.mOpNames.indexOf(dtree_name) >= 0;
        
        switch (this.mCurOp) {
            case "create":
                if (!q_all && checkIdentifier(dtree_name)) {
                    this._doUpdate(dtree_name);
                }
                break;
            case "modify":
                if (q_op && dtree_name != this.mCurDTreeName) {
                    this._doUpdate(dtree_name);
                }
                break;
            case "load":
                if (q_all && dtree_name != this.mCurDTreeName) {
                    sDecisionTree.setup(false, null, dtree_name);
                }
                break;
        }
    },
    
    _doUpdate: function(dtree_name) {
        ajaxCall("solutions", "ds=" + sDSName + "&entry=" + dtree_name,
            function(info) {sDTreesH.doUpdate(info, dtree_name);});
    },
    
    doUpdate: function(info, dtree_name) {
        if (info === null || info == "dtree") {
            sDecisionTree.setup(true, ["DTREE", "UPDATE", dtree_name]);
            return;
        }
        alert("Solution name duplication: " + info);
        this.mInpName.className = "bad";
        this.mBtnOp.disabled = true;
    },
    
    fillSelNames: function(with_empty, dtree_list, cur_value) {
        if (this.mListName == null || this.mAllNames == null)
            return;
        resetSelectInput(this.mListName, dtree_list, with_empty, cur_value);
    },
    
    getAllList: function() {
        return this.mAllNames;
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
    mCurWarnings: null,
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
        this.mCurWarnings = null;
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
        this.mButtonSave.disabled = same_cnt || this.mCurError; 
        err_msg = ""; err_class = "";
        if (this.mCurError)
            err_msg = this.mCurError;
        else if (this.mCurWarnings != null) {
            err_msg = this.mCurWarnings;
            err_class = "warn";
        }
        this.mSpanError.innerHTML = err_msg;
        this.mSpanError.setAttribute("class", err_class);
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
        this.mCurError = null;
        this.mCurWarnings = null;
        this.mErrorPos = null;
        this.mWaiting = true;
        ajaxCall("dtree_check", "ds=" + sDSName + "&code=" +
            encodeURIComponent(this.mCurContent), 
            function(info) {sCodeEditH._validation(info);});
    },
    
    _validation: function(info) {
        this.mCurContent = info["code"];
        this.mWaiting = false;
        this.mCurError = null;
        this.mCurWarnings = null;
        this.mErrorPos = null;
        if (info["error"]) {
            this.mCurError = "At line " + info["line"] + 
                " pos " + (info["pos"] + 1) + ": " +
                info["error"];
            this.mErrorPos = [info["line"], info["pos"]];
        } else if (info["warnings"]) {
            this.mCurWarnings = "Warning";
            if (info["warnings"].length > 1)
                this.mCurWarnings += "(+" + 
                    (info["warnings"].length - 1) + " more)";
            var w_info = info["warnings"][0];
            this.mCurWarnings += " at " + w_info["line"] + 
                "/" + (w_info["pos"] + 1) + ": " +
                w_info["error"];
            this.mErrorPos = [w_info["line"], w_info["pos"]];;
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

/*************************************/
/* DTree tracers                     */
/*************************************/
var sTraceDTreeH = {
    mSpanModTitle: null,
    mInputModVariant: null,
    mInputModTranscript: null,
    mInputModTranscript: null,
    mDivModParams: null,
    mDivModCtrl: null,
    mDivModProblems: null,
    mDivModStatus: null,
    mTaskId: null,
    mTimeH: null,
    mRunMode: null,
    
    init: function() {
        this.mSpanModTitle = document.getElementById("dtree-tracer-title");
        this.mInputModVariant = document.getElementById("dtree-tracer-variant");
        this.mInputModTranscript = document.getElementById("dtree-tracer-transcript");
        this.mDivModParams = document.getElementById("dtree-tracer-params");
        this.mDivModCtrl = document.getElementById("dtree-tracer-ctrl");
        this.mDivModParamTranscript = document.getElementById("dtree-tracer-transcript-input-div");

        this.mDivModProblems = document.getElementById("dtree-tracer-problems");
        this.mDivModStatus = document.getElementById("dtree-tracer-status");
        
        //"dtree-tracer-back"
        //"dtree-tracer-mod"
        //"dtree-tracer-top"
    },
    
    reportAll: function() {
        this.mRunMode = "All";
        this.mSpanModTitle.innerHTML = 'Tracing report for decision tree';
        this.mDivModParams.style.visibility = "hidden";
        this.mDivModCtrl.style.visibility = "hidden";
        this.mDivModProblems.innerHTML = "";
        this.mDivModStatus.innerHTML = "";
        
        sViewH.modalOn(document.getElementById("dtree-tracer-back"));
        args = sDecisionTree.makeArgs();
        ajaxCall("dtree_variants_report", args, function(info){sTraceDTreeH.setupTask(info);});
    },
    
    readyReportOne: function() {
        this.mRunMode = "One";
        this.mSpanModTitle.innerHTML = 'Trace variant in decision tree';
        this.mDivModParams.style.visibility = "visible";
        if (sDSKind == "ws")
            this.mDivModParamTranscript.style.visibility = "visible";
        else
            this.mDivModParamTranscript.style.visibility = "hidden";
        this.mDivModCtrl.style.visibility = "visible";
        this.mDivModProblems.innerHTML = "";
        this.mDivModStatus.innerHTML = "";
        sViewH.modalOn(document.getElementById("dtree-tracer-back"));
    },

    reportOne: function() {
        if (!this.mInputModVariant.value)
            return;
        args = sDecisionTree.makeArgs();
        args += "&variant=" + encodeURIComponent(this.mInputModVariant.value);
        if (sDSKind == "ws" && this.mInputModTranscript)
            args += "&transcript=" + encodeURIComponent(this.mInputModTranscript.value);
        ajaxCall("dtree_variant_trace", args, function(info){sTraceDTreeH.setupTask(info);});
    },
    
    setupTask: function(info) {
        this.mTaskId = info["task_id"];
        this.checkTask();
    },

    checkTask: function() {
        if (this.mTaskId == null)
            return;
        ajaxCall("job_status", "task=" + this.mTaskId,
            function(info) {
                sTraceDTreeH._checkTask(info);})
    },
    
    _checkTask: function(info) {
        if (info != null && info[0] == false) {
            this.mDivModStatus.innerHTML = info[1];
            if (this.mTimeH == null)
                this.mTimeH = setInterval(function() {sTraceDTreeH.checkTask()}, 3000);
            return;
        }
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        sViewH.blockModal(false);
        if (info == null) {
            this.mDivModStatus.innerHTML = "Task information lost";
        } else {
            if (info[0] == null) {
                this.mDivModStatus.innerHTML = info[1];
            } else {
                if (info[1]["error"])
                    this.mDivModProblems.innerHTML = info[1]["error"];
                else {
                    target_ref = "job_status?task=" + this.mTaskId;
                    this.mDivModStatus.innerHTML = 'Done: <a href="' + 
                        target_ref +'" target="blank">' + '>Open it</a>';
                }
            }
        }
    }
};

function traceReportAll() {
    sTraceDTreeH.reportAll();
}

function traceReportOne() {
    sTraceDTreeH.readyReportOne();
}

function startDTreeTrace() {
    sTraceDTreeH.reportOne();
}
/**************************************/
function arrangeControls() {
    document.getElementById("dtree-main").style.height = 
        Math.max(window.innerHeight - 55, 30) + "px";
    el_cond_mod = document.getElementById("cur-cond-mod");
    if (el_cond_mod.className == "enum") {
        cond_mod_height = el_cond_mod.offsetHeight;
        func_el= document.getElementById("cur-cond-func-param");
        if (func_el && func_el.style.display != "none") 
            cond_mod_height -= func_el.getBoundingClientRect().height;
        document.getElementById("wrap-cond-enum").style.height = 
            Math.max(10, cond_mod_height - 110) + "px";
    }
    sSubVRecH.arrangeControls();
    sOpEnumH.arrangeControls();
}

function onKey(key_event) {
    sSubVRecH.onKey(key_event);
}

function modifyDTree(target, op) {
    var instr = [target, op];
    if (target == "ATOM") {
        instr.push(sDecisionTree.getCurAtomLoc()); 
    } else if (target == "POINT") {
        instr.push(sDecisionTree.mCurPointNo);
    } else {
        console.log("Bad target for modify: " + target);
        return;
    }
    if (instr[2] == null)
        return;
    if (op != "DELETE") {
        instr.push(sOpCondH.getNewCondition());
        if (!instr[3]) 
            return;
    }
    sDecisionTree.setup(true, instr);
}

function versionSelect() {
    sVersionsH.selectVersion();
}

function editAtom(evt) {
    var atom_id = evt.target.id;
    idxs = atom_id.substring(7).split('-');
    sDecisionTree.atomEdit(parseInt(idxs[0]), parseInt(idxs[1]));
}

function dropAtom(evt) {
    var atom_id = evt.target.id;
    idxs = atom_id.substring(7).split('-');
    sDecisionTree.atomDrop(parseInt(idxs[0]), parseInt(idxs[1]));
}
