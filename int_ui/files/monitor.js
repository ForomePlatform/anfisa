var sCurTag = null;
var sCurFilterName = null;
var sTagRecList = null;
var sNavSheet = null;
var sFltTimeDict = [];
var sCurZoneData = null;

var sCheckFltNamed   = null;
var sCheckFltCurrent = null;
var sSelectFltNamed  = null;
var sElFltCurState   = null;
var sCheckZoneCur    = null;
var sElZoneCurState  = null;
var sTagsIntVersion  = null;

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
    var args = "ws=" + parent.window.sDSName;
    if (tag_name) 
        args += "&tag=" + tag_name;
    ajaxCall("tag_select", args, setupTagSelection);
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
    sTagsIntVersion = info["tags-version"];
    checkZoneTagsIntVersion(sTagsIntVersion);
    sSelectCurTag.selectedIndex = tag_list.indexOf(sCurTag) + 1;
    sTagRecList = info["records"];
    updateTagNavigation();
}

function checkTagsIntVersion(tags_int_version) {
    if (tags_int_version != sTagsIntVersion) {
        loadTagSelection(sCurTag);
    }
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
        rep_cnt.push((Math.min(cnt[0] + 1, cnt_tag)) + "/<b>" + cnt_tag + "</b>");
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

function clearFilterOpMode() {
    sFiltersH.update();
    sViewH.dropOff();
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

function checkTabNavigation(tag_name) {
    if (sCurTag && (tag_name == sCurTag || tag_name == null)) {
        loadTagSelection(sCurTag);
    }
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
    loadList(sCurFilterName, sCurZoneData);
    sSelectFltNamed.selectedIndex = sFiltersH.getAllList().indexOf(sCurFilterName) + 1;
    if (cur_flt_status) {
        sElFltCurState.innerHTML = cur_flt_status;
        sElFltCurState.className = "status";
        sCheckFltCurrent.disabled = true;
        sCheckFltCurrent.checked = false;
    } else {
        cond_len = sConditionsH.getSeqLength();
        sElFltCurState.innerHTML = cond_len + " condition" + ((cond_len>1)? "s":"");
        sElFltCurState.className = "";
        sCheckFltCurrent.disabled = false;
        sCheckFltCurrent.checked = (sCurFilterName == "");
    } 
    sCheckFltNamed.checked = !!sCurFilterName;
}

function updateCurZone(mode_on){
    cur_zone_status = checkCurZoneStatus();
    prev_zone_data = sCurZoneData;
    document.getElementById("zone-cur-title").innerHTML = 
        (sWorkZoneTitle)? sWorkZoneTitle:"";
    if (cur_zone_status) {
        sElZoneCurState.innerHTML = cur_zone_status;
        sElZoneCurState.className = "status";
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


