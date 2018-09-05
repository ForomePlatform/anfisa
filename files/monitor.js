var sCurTag = null;
var sCurFilter = null;
var sTagRecList = null;
var sNavSheet = null;

var sCheckFltNamed   = null;
var sCheckFltCurrent = null;
var sSelectFltNamed  = null;
var sElFltCurState   = null;

var sSelectCurTag    = null;
var sElCurTagNav     = null;
var sElCurTagCount   = null;
var sSeqElNavigation = null;
var sSeqElNavCount   = null;

function initMonitor() {
    sCheckFltNamed   = document.getElementById("flt-named");
    sCheckFltCurrent = document.getElementById("flt-check-current");
    sSelectFltNamed  = document.getElementById("flt-named-select");
    sElFltCurState   = document.getElementById("flt-current-state");
    
    sSelectCurTag    = document.getElementById("cur-tag");
    sElCurTagNav     = document.getElementById("cur-tag-nav");
    sElCurTagCount   = document.getElementById("cur-tag-count");
    sSeqElNavigation   = [
        document.getElementById("cur-tag-nav-first"),
        document.getElementById("cur-tag-nav-prev"),
        document.getElementById("cur-tag-here"),
        document.getElementById("cur-tag-nav-next"),
        document.getElementById("cur-tag-nav-last")];
    sSeqElNavCount = [
        document.getElementById("cur-tag-count-prev"),
        document.getElementById("cur-tag-count-next")]
    loadNamedFilters();
    loadTagSelection(null);
}

function pickTag() {
    if (sSelectCurTag.value != sCurTag) {
        loadTagSelection(sSelectCurTag.value);
    }
}

function tagNav(mode) {
    if (sNavSheet!= null && sNavSheet[mode] >= 0)
        changeRec(sNavSheet[mode]);
}

function loadTagSelection(tag_name) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupTagSelection(info);
        }
    };
    xhttp.open("POST", "tag_select", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + parent.window.sWorkspaceName;
    if (tag_name) 
        args += "&tag=" + tag_name;
    xhttp.send(args); 
}

function setupTagSelection(info) {
    sCurTag = info["tag"];
    for (idx = sSelectCurTag.length - 1; idx > 0; idx--) {
        sSelectCurTag.remove(idx);
    }
    tag_list = info["tag-list"];
    for (idx = 0; idx < tag_list.length; idx++) {
        tag_name = tag_list[idx];
        var option = document.createElement('option');
        option.innerHTML = tag_name;
        option.value = tag_name;
        sSelectCurTag.append(option)
    }
    sSelectCurTag.selectedIndex = tag_list.indexOf(sCurTag) + 1;
    sTagRecList = info["records"];
    updateTagNavigation();
}

function updateTagNavigation() {
    if (sCurRecNo == null || sRecList == null) {
        sElCurTagNav.style.visibility = "hidden";
        sElCurTagCount.innerHTML = "";
        return;
    }
    
    sElCurTagNav.style.visibility = (sCurTag)? "visible" : "hidden";
    if (!sCurTag) {
        sElCurTagCount.innerHTML = "";
        return;
    }
    
    sNavSheet = [-1, -1, -1, -1, -1];
    cnt = [0, 0, 0];
    j = 0; k = 0;
    for (idx = 0; idx < sTagRecList.length; idx++) {
        rec_no = sTagRecList[idx];
        while (j < sRecList.length && sRecList[j][0] < rec_no) {
            j++;
        }
        if (j >= sRecList.length)
            break;
        if (sRecList[j][0] != rec_no)
            continue;
        if (rec_no == sCurRecNo) {
            sNavSheet[2] = 0;
            cnt[1] = 1;
            k = 3;
            continue;
        }
        if (rec_no < sCurRecNo) {
            if (k == 0) {
                sNavSheet[0] = rec_no;
                k = 1;
            } else {
                sNavSheet[1] = rec_no;
            }
            cnt[0]++;
        } else {
            if (k == 3) {
                sNavSheet[3] = rec_no;
                k = 4;
            } else {
                sNavSheet[4] = rec_no;
            }
            cnt[2]++;            
        }
    }
    cnt_tag = cnt[0] + cnt[1] + cnt[2];
    rep_cnt = [];
    rep_cnt.push(((cnt_tag == sTagRecList.length))? "In total:":"In filter:");
    rep_cnt.push((cnt[0] + 1) + "/<b>" + cnt_tag + "</b>");
    if (cnt_tag != sTagRecList.length)
        rep_cnt.push("Total: " + sTagRecList.length);
    sElCurTagCount.innerHTML = rep_cnt.join(" ");
    
    for (j=0; j < 5; j++) {
        sSeqElNavigation[j].className = 
            (sNavSheet[j] >= 0)? "tags-nav":"tags-nav-disable";
    }
    for (j=0; j < 2; j++) {
        sSeqElNavCount[j].innerHTML = "" + cnt[2*j];
    }
}

function loadNamedFilters() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupNamedFilters(info);
        }
    };
    xhttp.open("POST", "filter_names", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + parent.window.sWorkspaceName + 
        "&m=" + encodeURIComponent(parent.window.sAppModes);
    xhttp.send(args); 
}

function setupNamedFilters(info) {
    for (idx = sSelectFltNamed.length - 1; idx > 0; idx--) {
        sSelectFltNamed.remove(idx);
    }
    filters = info["filters"];
    for (idx = 0; idx < filters.length; idx++) {
        flt_name = filters[idx];
        var option = document.createElement('option');
        option.innerHTML = flt_name;
        option.value = flt_name;
        sSelectFltNamed.append(option)
    }
    sSelectFltNamed.selectedIndex = 0;
}

function checkTabNavigation(tag_name) {
    if (sCurTag && (tag_name == sCurTag || tag_name == null)) {
        loadTagSelection(sCurTag);
    }
}

function checkCurFilters(mode_cur_filter) {
}

function pickNamedFilter() {
}

