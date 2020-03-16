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

var sCurRecNo = null;
var sCurRecID = null;
var sTabPortData = [false, null, null];
var sRecList = null;
var sViewRecNoSeq = null;
var sViewMarks = null;

var sCurFilterName = null;
var sFltTimeDict = [];

var sCheckFltNamed   = null;
var sCheckFltCurrent = null;
var sSelectFltNamed  = null;
var sElFltCurState   = null;

function initWin(workspace_name, common_title, ws_pub_url) {
    sDSName = workspace_name; 
    sDSKind = "ws";
    sCommonTitle = common_title;
    sWsPubURL = ws_pub_url;
    sUnitsH.init("ds=" + sDSName, false);
    window.name = sCommonTitle + ":" + sDSName;
    document.getElementById("ds-name").innerHTML = sDSName;
    
    window.onkeydown = onKey;
    window.onclick   = onClick;
    window.onresize  = arrangeControls;

    sCheckFltNamed   = document.getElementById("flt-check-named");
    sCheckFltCurrent = document.getElementById("flt-check-current");
    sSelectFltNamed  = document.getElementById("flt-named-select");
    sElFltCurState   = document.getElementById("flt-current-state");

    sTagSupportH.init();        
    updateCurFilter("");
    sZoneH.init();
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
    relaxView();
}

function reloadList() {
    sViewH.popupOff();
    ajaxCall("ws_list", sConditionsH.getCondRqArgs(sCurFilterName, 
        sZoneH.getCurState(), sCheckFltCurrent.checked), setupList);
}

function setupList(info) {
    if (info["ds"] != sDSName)
        return;
    var rep = '<b>' + info["filtered-counts"][0] + '</b>';
    if (info["total-counts"][0] != info["filtered-counts"][0]) 
        rep += "&nbsp;/&nbsp;" + info["total-counts"][0];
    document.getElementById("ws-list-report").innerHTML = rep;
    rep = '<b>' + info["filtered-counts"][1] + '</b>';
    if (info["total-counts"][1] != info["filtered-counts"][1]) 
        rep += "&nbsp;/&nbsp;" + info["total-counts"][1];
    document.getElementById("ws-transcripts-report").innerHTML = rep;
    sRecList = info["records"];
    refreshRecList();
    arrangeControls();
    sTagSupportH.checkTagsState(true);
}

function arrangeControls() {
    if (sSamplesCtrl != null) {
        sSamplesCtrl.arrangeControls();
    }    
    document.getElementById("top").style.height = 60;
    document.getElementById("rec-list").style.height = window.innerHeight - 61;
    sZoneH.arrangeControls();
    sOpEnumH.arrangeControls();
}

function refreshRecList() {
    sViewRecNoSeq = [];
    var rep = [];
    for (rec_no = 0; rec_no < sRecList.length; rec_no++) {
        rinfo = sRecList[rec_no];
        class_name = 'rec-label ' + rinfo["cl"];
        if (sViewMarks && sViewMarks.indexOf(rec_no) >= 0)
            class_name += " marked";
        sViewRecNoSeq.push(rinfo["no"]);
        rep.push('<div id="li--' + rinfo["no"] + '" class="' + class_name + 
            '" onclick="changeRec(' + rec_no + ');">' + rinfo["lb"] + '</div>');
    }
    document.getElementById("rec-list").innerHTML = rep.join('\n');
    if (sViewRecNoSeq.length == 0) {
        window.frames['rec-frame1'].location.replace("norecords");
        window.frames['rec-frame2'].location.replace("norecords");
    } else {
        idx = sViewRecNoSeq.indexOf(sCurRecID);
        sCurRecNo = null;
        changeRec((idx >=0)? idx:0);
    }
}

function updateRecordMarks(rec_mark_seq) {
    if (!sViewMarks)
        sViewMarks = [];
    var idx;
    for(idx = 0; idx < rec_mark_seq.length; idx++) {
        var rec_id = rec_mark_seq[idx];
        if (sViewMarks.indexOf(rec_id) < 0)
            _updateRecordMark(rec_id, true);
    }
    for(idx = 0; idx < sViewMarks.length; idx++) {
        var rec_id = sViewMarks[idx];
        if (rec_mark_seq.indexOf(rec_id) < 0)
            _updateRecordMark(rec_id, false);
    }
    sViewMarks = rec_mark_seq;
}

function _updateRecordMark(rec_id, is_marked) {
    el = document.getElementById('li--' + rec_id);
    if (el) { 
        cls_val = el.className.replace(" marked", "");
        if (is_marked)
            el.className = cls_val + " marked";
        else
            el.className = cls_val;
    }        
}

function changeRec(rec_no) {
    if (sCurRecNo == rec_no) 
        return;
    var new_rec_el = document.getElementById("li--" + sViewRecNoSeq[rec_no]);
    if (new_rec_el == null) 
        return;
    if (sCurRecNo != null) {
        var prev_el = document.getElementById("li--" + sCurRecID);
        prev_el.className = prev_el.className.replace(" press", "");
    }
    sCurRecNo = rec_no;
    sCurRecID = sViewRecNoSeq[sCurRecNo];
    new_rec_el.className = new_rec_el.className + " press";
    softScroll(new_rec_el);
    window.frames['rec-frame1'].location.replace("rec?ds=" + sDSName +
        "&rec=" + sCurRecID + "&port=1" + 
        "&details=" + sRecList[sCurRecNo]["dt"]);
    window.frames['rec-frame2'].location.replace("rec?ds=" + sDSName + 
        "&rec=" + sCurRecID + "&port=2" + 
        "&details=" + sRecList[sCurRecNo]["dt"]);
    sTagSupportH.updateNavigation();
}

function onKey(event_key) {
    if (event_key.code == "ArrowUp" && sCurRecNo > 0)
        changeRec(sCurRecNo - 1);
    if (event_key.code == "ArrowDown") 
        changeRec(sCurRecNo + 1);
    if (event_key.code == "ArrowLeft") 
        tagNav(1);
    if (event_key.code == "ArrowRight") 
        tagNav(3);
}

function onClick(event_ms) {
    sViewH.onclick(event_ms);
}

function filterModOn() {
    clearFilterOpMode();
    sViewH.modalOn(document.getElementById("filter-back"));
    arrangeControls();
}

function zoneModOn() {
    sViewH.modalOn(document.getElementById("zone-back"));
}

//=====================================
function updateTabCfg() {
    document.getElementById("rec-frame1").style.display =
            sTabPortData[0]? "block": "none";
    if (sTabPortData[0] && sTabPortData[1] == sTabPortData[2]) {
        for (idx = 1; idx <3; idx++) {
            frame = window.frames['rec-frame' + idx];
            if (frame.sStarted) 
                frame.resetTabPort();
        }
    }
    for (idx = 1; idx <3; idx++) {
        frame = window.frames['rec-frame' + idx];
        if (frame.sStarted) 
            frame.updateCfg();
    }
}

//=====================================
function refreshCohorts() {
    for (idx = 1; idx < 3; idx++) {
        frame = window.frames['rec-frame' + idx];
        if (frame.sStarted) 
            frame.refreshCohorts();
    }
}

//=====================================
// Export
//=====================================
function getCurCount() {
    return sRecList.length;
}

function doExport() {
    sViewH.popupOff();
    ajaxCall("export", sConditionsH.getCondRqArgs(
        sCurFilterName, sZoneH.getCurState(), true), setupExport);
}

//=====================================
// Filters
//=====================================
function clearFilterOpMode() {
    sFiltersH.update();
    sViewH.popupOff();
}

function onFilterListChange() {
    var all_filters = sFiltersH.getAllList();
    for (idx = sSelectFltNamed.length - 1; idx > 0; idx--) {
        sSelectFltNamed.remove(idx);
    }
    for (idx = 0; idx < all_filters.length; idx++) {
        flt_name = all_filters[idx];
        var option = document.createElement('option');
        option.innerHTML = flt_name;
        option.value = flt_name;
        sSelectFltNamed.append(option)
    }
    sSelectFltNamed.selectedIndex = all_filters.indexOf(sCurFilterName) + 1;
    clearFilterOpMode();
}

function pickNamedFilter() {
    updateCurFilter(sSelectFltNamed.value);
}

function checkCurFilters(mode_filter) {
    if (mode_filter == 0) {
        updateCurFilter((sCheckFltNamed.checked)?sSelectFltNamed.value:"");
    } else {
        updateCurFilter((sCheckFltCurrent.checked)? "":null);
    }
}

function updateCurFilter(filter_name, force_it) {
    if (!force_it && filter_name == sCurFilterName)
        return;
    cur_flt_status = sConditionsH.report();
    sCurFilterName = filter_name;
    sSelectFltNamed.selectedIndex = sFiltersH.getAllList().indexOf(sCurFilterName) + 1;
    if (cur_flt_status) {
        sElFltCurState.innerHTML = cur_flt_status;
        sElFltCurState.className = "status";
        sCheckFltCurrent.disabled = true;
        sCheckFltCurrent.checked = false;
    } else {
        cond_len = sConditionsH.getCondCount();
        sElFltCurState.innerHTML = cond_len + " condition" + ((cond_len>1)? "s":"");
        sElFltCurState.className = "";
        sCheckFltCurrent.disabled = false;
        sCheckFltCurrent.checked = (!sCurFilterName);
    } 
    sCheckFltNamed.checked = !!sCurFilterName;
    reloadList();
}

//=====================================
// Tags
//=====================================
sTagSupportH = {
    mCurTag: null,
    mTagRecList: null,
    mNavSheet: null,
    mTagsState: null,
    mSelCurTag: null,
    mElTagNav: null,
    mElTagCount: null,
    mSeqElNav: null,
    mElNavCounts: null,

    init: function() {
        this.mSelCurTag    = document.getElementById("cur-tag");
        this.mElTagNav     = document.getElementById("cur-tag-nav");
        this.mElTagCount   = document.getElementById("cur-tag-count");
        this.mSeqElNav   = [
            document.getElementById("cur-tag-nav-first"),
            document.getElementById("cur-tag-nav-prev"),
            document.getElementById("cur-tag-here"),
            document.getElementById("cur-tag-nav-next"),
            document.getElementById("cur-tag-nav-last")];
        this.mElNavCounts = [
            document.getElementById("cur-tag-count-prev"),
            document.getElementById("cur-tag-count-next")]
        this.loadSelection(null);
    },
    
    loadSelection: function(tag_name) {
        var args = "ds=" + parent.window.sDSName;
        if (tag_name) 
            args += "&tag=" + tag_name;
        ajaxCall("tag_select", args, 
            function(info) {sTagSupportH._loadSelection(info)});
    },

    _loadSelection: function(info) {
        this.mCurTag = (info["tag"])? info["tag"]: null;
        for (idx = this.mSelCurTag.length - 1; idx > 0; idx--) {
            this.mSelCurTag.remove(idx);
        }
        tag_list = info["tag-list"];
        for (idx = 0; idx < tag_list.length; idx++) {
            tag_name = tag_list[idx];
            var option = document.createElement('option');
            option.innerHTML = tag_name;
            option.value = tag_name;
            this.mSelCurTag.append(option)
        }
        this.mSelCurTag.selectedIndex = tag_list.indexOf(this.mCurTag) + 1;
        this.mTagRecList = (this.mCurTag)? info["tag-rec-list"]:null;

        if (this.mTagsState != info["tags-state"]) {
            this.mTagsState = info["tags-state"];
            updateRecordMarks(info["tags-rec-list"]);
        }
        this.updateNavigation();
    },

    pickTag: function() {
        if (this.mSelCurTag.value != this.mCurTag) {
            this.loadSelection(this.mSelCurTag.value);
        }
    },

    navigate: function(mode) {
        if (this.mNavSheet!= null && this.mNavSheet[mode] >= 0)
            return this.mNavSheet[mode];
        return null;
    },

    checkTagsState: function(tags_state) {
        if (tags_state != this.mTagsState || tags_state == true) {
            this.loadSelection(this.mCurTag);
        }
    },

    checkNavigation: function(tag_name) {
        if (this.mCurTag && (tag_name == this.mCurTag || tag_name == null)) {
            this.loadSelection(this.mCurTag);
        }
    },
    
    updateNavigation: function() {
        if (sCurRecID == null || sRecList == null) {
            this.mElTagNav.style.visibility = "hidden";
            this.mElTagCount.innerHTML = "";
            return;
        }
        if (!this.mCurTag) {
            this.mElTagNav.style.visibility = "hidden";
            this.mElTagCount.innerHTML = "";
            return;
        }
        this.mNavSheet = [-1, -1, -1, -1, -1];
        cnt = [0, 0, 0];
        j = 0; k = 0;
        for (idx = 0; idx < this.mTagRecList.length; idx++) {
            rec_no = this.mTagRecList[idx];
            while (j < sRecList.length && sRecList[j]["no"] < rec_no) {
                j++;
            }
            if (j >= sRecList.length)
                break;
            if (sRecList[j]["no"] != rec_no)
                continue;
            if (rec_no == sCurRecID) {
                this.mNavSheet[2] = 0;
                cnt[1] = 1;
                k = 3;
                continue;
            }
            if (rec_no < sCurRecID) {
                if (k == 0) {
                    this.mNavSheet[0] = j;
                    k = 1;
                } else {
                    this.mNavSheet[1] = j;
                }
                cnt[0]++;
            } else {
                if (k <= 3) {
                    this.mNavSheet[3] = j;
                    k = 4;
                } else {
                    this.mNavSheet[4] = j;
                }
                cnt[2]++;            
            }
        }
        if (cnt[0] == 1) {
            this.mNavSheet[1] = this.mNavSheet[0];
            this.mNavSheet[0] = -1;
        }
        if (cnt[2] == 1 && this.mNavSheet[4] >= 0) {
            this.mNavSheet[3] = this.mNavSheet[4];
            this.mNavSheet[4] = -1;
        }
        cnt_tag = cnt[0] + cnt[1] + cnt[2];
        rep_cnt = [];
        rep_cnt.push(((cnt_tag == this.mTagRecList.length))? "In total:":"In filter:");
        this.mElTagNav.style.visibility = (cnt_tag > 0)? "visible": "hidden";
        if (cnt_tag > 0) {
            rep_cnt.push((Math.min(cnt[0] + 1, cnt_tag)) + "/<b>" + cnt_tag + "</b>");
        } else {
            rep_cnt.push("<b>" + cnt_tag + "</b>");
        }
        if (cnt_tag != this.mTagRecList.length)
            rep_cnt.push("Total: " + this.mTagRecList.length);
        this.mElTagCount.innerHTML = rep_cnt.join(" ");
        
        for (j=0; j < 5; j++) {
            this.mSeqElNav[j].className = 
                (this.mNavSheet[j] >= 0)? "tags-nav":"tags-nav-disable";
        }
        for (j=0; j < 2; j++) {
            this.mElNavCounts[j].innerHTML = "" + cnt[2*j];
        }
    }
};


//=====================================
function tabReport() {
    if (sCurRecNo == null)
        return;
    var seq_rec_no = [];
    for (idx = sCurRecNo; idx < sViewRecNoSeq.length; idx++) {
        seq_rec_no.push(sViewRecNoSeq[idx]);
        if (seq_rec_no.length >= 10)
            break;
    }
    window.open("tab_report?ds=" + sDSName + "&schema=demo&seq=" + 
        encodeURIComponent(JSON.stringify(seq_rec_no)));
}

//=====================================
function pickTag() {
    sTagSupportH.pickTag();
}

function tagNav(mode) {
    var rec_no = sTagSupportH.navigate(mode);
    if (rec_no != null)
        changeRec(rec_no);
}

function checkTagsState(tags_state) {
    sTagSupportH.checkTagsState(tags_state);
    sZoneH.checkTagsState(tags_state);
}

function checkTabNavigation(tag_name) {
    sTagSupportH.checkNavigation(tag_name);
}
