var sDSName = null;
var sCommonTitle = null;
var sCurRecNo = null;
var sCurRecID = null;
var sTabPortData = [false, null, null];
var sCurRandPortion = 1;
var sRecList = null;
var sDetailsList = null;
var sRecSamples = null;
var sViewRecNoSeq = null;
var sAppModeRq = null;

var sSubViewH = null;

function initWin(workspace_name, common_title, app_modes) {
    sAppModeRq = (app_modes)? ("&m=" + app_modes) : "";
    sDSName = workspace_name; 
    sCommonTitle = common_title;
    sUnitsH.init("stat", "statunits", "ws=" + sDSName, false);
    window.name = sCommonTitle + ":" + sDSName;
    document.getElementById("ws-name").innerHTML = sDSName;
    
    window.onkeydown = onKey;
    window.onclick   = onClick;
    window.onresize  = arrangeControls;
    document.getElementById("list-rand-portion").value = sCurRandPortion;

    if (sAppModeRq.toLowerCase().indexOf('r') >= 0) {
        document.getElementById("res-mode-check").style.visibility = "visible";
        document.getElementById("control-open").className = "drop res-mode";
    } else { 
        document.getElementById("res-mode-check").style.visibility = "hidden";
        document.getElementById("control-open").className = "drop";
    }
        
    initMonitor();
    checkWorkZone(null);
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
    relaxView();
}

function loadList(filter_name, zone_data) {
    sViewH.dropOff();
    ajaxCall("list", sConditionsH.getCondRqArgs(filter_name, zone_data), setupList);
}

function setupList(info) {
    if (info["workspace"] != sDSName)
        return;
    var rep = '<b>' + info["filtered"] + '</b>';
    if (info["total"] != info["filtered"]) 
        rep += "&nbsp;/&nbsp;" + info["total"];
    document.getElementById("ws-list-report").innerHTML = rep;
    rep = '<b>' + info["transcripts"][0] + '</b>';
    if (info["transcripts"][0] != info["transcripts"][1])
        rep += "&nbsp;/&nbsp;" + info["transcripts"][1];
    document.getElementById("ws-transcripts-report").innerHTML = rep;
    sRecSamples = info["list-mode"] == "samples";
    document.getElementById("ws-list-rand-info").style.visibility = 
        (sRecSamples)?"visible":"hidden";
    sRecList = info["records"];
    sDetailsList = info["details"];
    refreshRecList();
    arrangeControls();
}

function arrangeControls() {
    document.getElementById("top").style.height = (sRecSamples)? 80:60;
    document.getElementById("rec-list").style.height = window.innerHeight - 1 
        - ((sRecSamples)? 80:60);
    
    zone_mod_height = document.getElementById("zone-mod").getBoundingClientRect().height;
    document.getElementById("work-zone-area").style.height = zone_mod_height - 60;
    document.getElementById("work-zone-wrap-list").style.height = zone_mod_height - 125;
}

function refreshRecList() {
    if (sRecSamples) {
        idx_from = (sCurRandPortion - 1) * 20;
        idx_to = idx_from + 20;
    } else {
        idx_from = 0;
        idx_to = sRecList.length;
    }
    sViewRecNoSeq = [];
    var rep = [];
    for (idx = idx_from; idx < idx_to; idx++) {
        rec_id = sRecList[idx][0];
        label  = sRecList[idx][1];
        color  = sRecList[idx][2];
        marked = sRecList[idx][3];
        rec_no = idx - idx_from;
        class_name = 'rec-label ' + color;
        if (marked) 
            class_name += ' marked';
        sViewRecNoSeq.push(rec_id);
        rep.push('<div id="li--' + rec_id + '" class="' + class_name + 
            '" onclick="changeRec(' + rec_no + ');">' + label + '</div>');
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

function updateRecordMark(rec_id, rec_marked) {
    el = document.getElementById('li--' + rec_id);
    if (el) {
        class_seq = el.className.split(' ');
        if (rec_marked) {
            if (class_seq[2] == "marked")
                return
            class_seq.splice(2, 0, "marked");
        } else {
            if (class_seq.length == 1)
                return
            if (class_seq[2] == "marked")          
                class_seq.splice(2, 1);
        }
        el.className = class_seq.join(' ');
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
    window.frames['rec-frame1'].location.replace("rec?ws=" + sDSName + 
        sAppModeRq + "&rec=" + sCurRecID + "&port=1" + "&details=" + sDetailsList[sCurRecNo]);
    window.frames['rec-frame2'].location.replace("rec?ws=" + sDSName + 
        sAppModeRq + "&rec=" + sCurRecID + "&port=2" + "&details=" + sDetailsList[sCurRecNo]);
    updateTagNavigation();
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
}

function zoneModOn() {
    sViewH.modalOn(document.getElementById("zone-back"));
}

function rulesModOn() {
    setupRulesCtrl();
    sViewH.modalOn(document.getElementById("rules-back"));
}

function listRandPortion() {
    new_rand_p = (document.getElementById("list-rand-portion").value);
    if (sCurRandPortion != new_rand_p) {
        sCurRandPortion = new_rand_p;
        refreshRecList();
    }
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
function showExport() {
    relaxView();
    if (sRecList.length <= 300)
        res_content = 'Export ' + sRecList.length + ' variants?<br>' +
            '<button class="drop" onclick="doExport();">Export</button>' + 
            '&emsp;<button class="drop" onclick="relaxView();">Cancel</button>';
    else
        res_content = 'Too many variants for export: ' + 
            sRecList.length + ' > 300.<br>' +
            '<button class="drop" onclick="relaxView();">Cancel</button>';
    res_el = document.getElementById("export-result");
    res_el.innerHTML = res_content;
    sViewH.dropOn(res_el);
}

function doExport() {
    sViewH.dropOff();
    var args = sConditionsH.getCondRqArgs(sCurFilterName, sCurZoneData);
    ajaxCall("export", args, setupExport);
}

function setupExport(info) {
    res_el = document.getElementById("export-result");
    if (info["fname"]) {
        res_el.className = "drop";
        res_el.innerHTML = 'Exported ' + sRecList.length + ' variants<br>' +
        '<a href="' + info["fname"] + '" target="blank" ' + 'download>Download</a>';
    } else {
        res_el.className = "drop problems";
        res_el.innerHTML = 'Bad configuration';
    }
    sViewH.dropOn(res_el);
}

//=====================================
function switchResMode() {
    relaxView();
    var idx = sAppModeRq.toLowerCase().indexOf('r');
    if (idx >= 0) {
        app_mode = "";
    } else {
        app_mode = ((sAppModeRq)? sAppModeRq.substr(3):"") + "r";
    }
    initWin(sDSName, sCommonTitle, app_mode);
}

//=====================================
function onModalOff() {
}

