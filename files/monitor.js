var sCurTag = null;
var sCurFilterName = null;
var sTagRecList = null;
var sNavSheet = null;
var sAllFilters = [];
var sCurZoneData = null;

var sCheckFltNamed   = null;
var sCheckFltCurrent = null;
var sSelectFltNamed  = null;
var sElFltCurState   = null;
var sCheckZoneCur    = null;
var sElZoneCurState  = null;

var sSelectCurTag    = null;
var sElCurTagNav     = null;
var sElCurTagCount   = null;
var sSeqElNavigation = null;
var sSeqElNavCount   = null;

function initMonitor() {
    sCheckFltNamed   = document.getElementById("flt-check-named");
    sCheckFltCurrent = document.getElementById("flt-check-current");
    sSelectFltNamed  = document.getElementById("flt-named-select");
    sElFltCurState   = document.getElementById("flt-current-state");
    sCheckZoneCur    = document.getElementById("zone-check");
    sElZoneCurState  = document.getElementById("zone-descr");
    
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
    updateCurFilter("");
    updateCurZone();
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
    checkTagsIntVersion(info["tags-version"]);
    sSelectCurTag.selectedIndex = tag_list.indexOf(sCurTag) + 1;
    sTagRecList = info["records"];
    updateTagNavigation();
}

function updateTagNavigation() {
    if (sCurRecID == null || sRecList == null) {
        sElCurTagNav.style.visibility = "hidden";
        sElCurTagCount.innerHTML = "";
        return;
    }
    if (sRecSamples && sCurTag) {
        sElCurTagNav.style.visibility = "hidden";
        sElCurTagCount.innerHTML = 'In total: <b>' + sTagRecList.length + '</b>';
        return;
    }
    if (!sCurTag) {
        sElCurTagNav.style.visibility = "hidden";
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
        if (rec_no == sCurRecID) {
            sNavSheet[2] = 0;
            cnt[1] = 1;
            k = 3;
            continue;
        }
        if (rec_no < sCurRecID) {
            if (k == 0) {
                sNavSheet[0] = j;
                k = 1;
            } else {
                sNavSheet[1] = j;
            }
            cnt[0]++;
        } else {
            if (k <= 3) {
                sNavSheet[3] = j;
                k = 4;
            } else {
                sNavSheet[4] = j;
            }
            cnt[2]++;            
        }
    }
    if (cnt[0] == 1) {
        sNavSheet[1] = sNavSheet[0];
        sNavSheet[0] = -1;
    }
    if (cnt[2] == 1 && sNavSheet[4] >= 0) {
        sNavSheet[3] = sNavSheet[4];
        sNavSheet[4] = -1;
    }
    cnt_tag = cnt[0] + cnt[1] + cnt[2];
    rep_cnt = [];
    rep_cnt.push(((cnt_tag == sTagRecList.length))? "In total:":"In filter:");
    sElCurTagNav.style.visibility = (cnt_tag > 0)? "visible": "hidden";
    if (cnt_tag > 0) {
        rep_cnt.push((cnt[0] + 1) + "/<b>" + cnt_tag + "</b>");
    } else {
        rep_cnt.push("<b>" + cnt_tag + "</b>");
    }
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

function setupNamedFilters(all_filters) {
    clearFilterOpMode();
    if (all_filters.length == sAllFilters.length) {
        q_same = true;
        for (idx = 0; idx < all_filters.length; idx++) {
            if (all_filters[idx] != sAllFilters[idx]) {
                q_same = false;
                break;
            }
        }
        if (q_same)
            return;
    }
    sAllFilters = all_filters;
    for (idx = sSelectFltNamed.length - 1; idx > 0; idx--) {
        sSelectFltNamed.remove(idx);
    }
    for (idx = 0; idx < sAllFilters.length; idx++) {
        flt_name = sAllFilters[idx];
        var option = document.createElement('option');
        option.innerHTML = flt_name;
        option.value = flt_name;
        sSelectFltNamed.append(option)
    }
    sSelectFltNamed.selectedIndex = sAllFilters.indexOf(sCurFilterName) + 1;
    checkFiltersAllFilters();
}

function checkTabNavigation(tag_name) {
    if (sCurTag && (tag_name == sCurTag || tag_name == null)) {
        loadTagSelection(sCurTag);
    }
}

function checkCurFilters(mode_filter) {
    if (mode_filter == 0) {
        updateCurFilter((sCheckFltNamed.checked)?sSelectFltNamed.value:"");
    } else {
        updateCurFilter((sCheckFltCurrent.checked)? "_current_":"");
    }
}

function pickNamedFilter() {
    updateCurFilter(sSelectFltNamed.value);
}

function updateCurFilter(filter_name, force_it) {
    if (!force_it && filter_name == sCurFilterName)
        return;
    sCurFilterName = filter_name;
    cur_flt_problems = checkCurConditionsProblem();
    if (filter_name == "_current_" && cur_flt_problems)
        filter_name = "";
    loadList(sCurFilterName, sCurZoneData);
    sSelectFltNamed.selectedIndex = sAllFilters.indexOf(sCurFilterName) + 1;
    if (cur_flt_problems) {
        sElFltCurState.innerHTML = cur_flt_problems;
        sElFltCurState.className = "problems";
        sCheckFltCurrent.disabled = true;
        sCheckFltCurrent.checked = false;
    } else {
        sElFltCurState.innerHTML = sCurFilterSeq.length + " condition" +
            ((sCurFilterSeq.length>1)? "s":"");
        sElFltCurState.className = "";
        sCheckFltCurrent.disabled = false;
        sCheckFltCurrent.checked = (sCurFilterName == "_current_");
    } 
    sCheckFltNamed.checked = (sCurFilterName != "_current_");
}

function updateCurZone(mode_on){
    cur_zone_problem = checkCurZoneProblem();
    prev_zone_data = sCurZoneData;
    document.getElementById("zone-cur-title").innerHTML = 
        (sWorkZoneTitle)? sWorkZoneTitle:"";
    if (cur_zone_problem) {
        sElZoneCurState.innerHTML = cur_zone_problem;
        sElZoneCurState.className = "problems";
        sCheckZoneCur.disabled = true;
        sCurZoneData = null;
    } else {
        sElZoneCurState.innerHTML = sWorkZoneDescr;
        sElZoneCurState.className = "";
        sCheckZoneCur.disabled = false;
        sCheckZoneCur.checked = (mode_on)? true:false;
        sCurZoneData = (mode_on)? sWorkZoneData: null;
    }
    if (prev_zone_data != sCurZoneData)
        loadList(sCurFilterName, sCurZoneData);
}

function checkCurZone() {
    updateCurZone(sCheckZoneCur.checked);
}