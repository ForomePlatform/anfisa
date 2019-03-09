var sWorkspaceName = null;
var sTitlePrefix = null;
var sCurRecNo = null;
var sCurRecID = null;
var sTabPortData = [false, null, null];
var sCurRandPortion = 1;
var sRecList = null;
var sRecSamples = null;
var sViewRecNoSeq = null;
var sAppModes = null;
var sExportFormed = null;
var sWsDropShown = null;

var sNodeFilterBack  = null;
var sNodeZoneBack  = null;
var sNodeNoteBack = null;
var sNodeRulesBack = null;

function initWin(workspace_name, app_modes) {
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    sWorkspaceName = workspace_name; 
    window.name = sTitlePrefix + "/" + sWorkspaceName;
    sAppModes = app_modes;
    sNodeFilterBack  = document.getElementById("filter-back");
    sNodeZoneBack    = document.getElementById("zone-back");
    sNodeNoteBack    = document.getElementById("note-back");
    sNodeRulesBack = document.getElementById("rules-back");
    window.onkeydown = onKey;
    window.onclick   = onClick;
    document.getElementById("list-rand-portion").value = sCurRandPortion;

    if (sAppModes.toLowerCase().indexOf('r') >= 0) {
        document.getElementById("res-mode-check").style.visibility = "visible";
        document.getElementById("ws-control-open").className = "drop res-mode";
    } else { 
        document.getElementById("res-mode-check").style.visibility = "hidden";
        document.getElementById("ws-control-open").className = "drop";
    }
        
    initMonitor();
    initFilters();
    checkWorkZone(null);
    wsDropShow(false);
}

function loadList(filter_name, zone_data) {
    wsDropShow(false);
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupList(info);
        }
    };
    xhttp.open("POST", "list", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = formFilterRequestArgs(filter_name);
    if (zone_data)
        args += "&zone=" + encodeURIComponent(JSON.stringify(zone_data));
    xhttp.send(args); 
}

function setupList(info) {
    sWorkspaceName = info["workspace"]; 
    document.getElementById("ws-name").innerHTML = sWorkspaceName;
    document.title = sTitlePrefix + ": " + sWorkspaceName;
    var el = document.getElementById("list-report");
    var el_p = document.getElementById("list-rand-portion");
    var rep = "Records: <b>" + info["filtered"] + "<b>";
    if (info["total"] != info["filtered"]) 
        rep += "/" + info["total"];
    if (info["list-mode"] == "samples") {
        rep += " Samples:";
        el_p.style.visibility = "visible";
        sRecSamples = true;
    } else {
        el_p.style.visibility = "hidden";
        sRecSamples = false;
    }
    el.innerHTML = rep;
    sRecList = info["records"];
    refreshRecList();
    initExportForm();
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
    window.frames['rec-frame1'].location.replace(
        "rec?ws=" + sWorkspaceName + "&m=" + sAppModes + 
        "&rec=" + sCurRecID + "&port=1");
    window.frames['rec-frame2'].location.replace(
        "rec?ws=" + sWorkspaceName + "&m=" + sAppModes + 
        "&rec=" + sCurRecID + "&port=2");
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
    if (event_ms.target == sNodeFilterBack)
        filterModOff();
    if (event_ms.target == sNodeZoneBack)
        zoneModOff();
    if (event_ms.target == sNodeRulesBack)
        rulesModOff();
    if (event_ms.target == sNodeNoteBack)
        noteModOff();
    if (sWsDropShown && !event_ms.target.matches('.drop')) {
        wsDropShow(false);
    }
}

function softScroll(nd) {
    if (nd == null) 
        return;
    var rect = nd.getBoundingClientRect();
    var rect_parent = nd.parentNode.getBoundingClientRect();
    if (rect.top - 10 < rect_parent.top) {
        nd.scrollIntoView(
            {behavior: 'auto', block: 'start', inline: 'center'});
    }
    else if (rect.top + rect.height + 10 >  rect_parent.top + rect_parent.height) {
        nd.scrollIntoView(
            {behavior: 'auto', block: 'start', inline: 'center'});
    }
}

function _showModal(cur_mode_node) {
    sNodeFilterBack.style.display = 
        (cur_mode_node == sNodeFilterBack)? "block":"none";
    sNodeZoneBack.style.display    = 
        (cur_mode_node == sNodeZoneBack)? "block":"none";
    sNodeNoteBack.style.display = 
        (cur_mode_node == sNodeNoteBack)? "block":"none";
    sNodeRulesBack.style.display = 
        (cur_mode_node == sNodeRulesBack)? "block":"none";
}

function filterModOn() {
    clearFilterOpMode();
    _showModal(sNodeFilterBack);
}

function filterModOff() {
    clearFilterOpMode();
    _showModal(null);
}

function zoneModOn() {
    _showModal(sNodeZoneBack);
}

function zoneModOff() {
    _showModal(null);
}

function noteModOff() {
    _showModal(null);
}

function rulesModOn() {
    setupRulesCtrl();
    _showModal(sNodeRulesBack);
}

function rulesModOff() {
    _showModal(null);
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
function initExportForm() {
    wsDropShow(false);
    if (sRecList.length <= 300)
        res_content = 'Export ' + sRecList.length + ' records?<br>' +
            '<button class="drop" onclick="doExport();">Export</button>' + 
            '&emsp;<button class="drop" onclick="wsDropShow(false);">Cancel</button>';
    else
        res_content = 'Too many records for export: ' + 
            sRecList.length + ' > 300.<br>' +
            '<button class="drop" onclick="wsDropShow(false);">Cancel</button>';
    document.getElementById("ws-export-result").innerHTML = res_content;
    sExportFormed = false;
}


function openControlMenu() {
    wsDropShow();
    if (sWsDropShown)
        document.getElementById("ws-control-menu").style.display = 
            (sWsDropShown)? "block":"none";
}

function showExport() {
    wsDropShow(false);
    document.getElementById("ws-export-result").style.display = "block";
    wsDropShow(true);
}

function goHome() {
    wsDropShow(false);
    window.open('dir', sTitlePrefix + ':dir');
}

function openNote() {
    wsDropShow(false);
    loadNote();
    _showModal(sNodeNoteBack);
}

function saveNote() {
    wsDropShow(false);
    loadNote(document.getElementById("note-content").value);
    noteModOff();
}

function switchResMode() {
    wsDropShow();
    var idx = sAppModes.toLowerCase().indexOf('r');
    if ( idx >= 0) {
        app_modes = sAppModes.substr(0, idx) + sAppModes.substr(idx + 1);
    } else {
        app_modes = sAppModes + 'r';
    }
    initWin(sWorkspaceName, app_modes);
}

function setupExport(info) {
    res_el = document.getElementById("ws-export-result");
    if (info["fname"]) {
        res_el.className = "drop";
        res_el.innerHTML = 'Exported ' + sRecList.length + ' records<br>' +
        '<a href="' + info["fname"] + '" target="blank" ' + 'download>Download</a>';
    } else {
        res_el.className = "drop problems";
        res_el.innerHTML = 'Bad configuration';
    }
    sExportFormed = true;
    wsDropShow(true);
}

function loadNote(content) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupNote(info);
        }
    };
    xhttp.open("POST", "wsnote", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + sWorkspaceName;
    if (content)
        args += "&note=" + encodeURIComponent(content);
    xhttp.send(args); 
}

function setupNote(info) {
    document.getElementById("note-ws-name").innerHTML = info["name"];
    document.getElementById("note-content").value = info["note"];
    document.getElementById("note-time").innerHTML = 
        (info["time"] == null)? "" : "Modified at " + timeRepr(info["time"]);
}

//=====================================
function wsDropShow(mode) {
    if (mode == undefined)
       sWsDropShown = !sWsDropShown;
    else
        sWsDropShown = mode;
    if (!sWsDropShown) {
        document.getElementById("ws-control-menu").style.display = "none";
        document.getElementById("ws-export-result").style.display = "none";
        document.getElementById("filters-op-list").style.display = "none";
    }
}

//=====================================
function timeRepr(time_label) {
    var dt = new Date(time_label);
    return dt.toLocaleString("en-US").replace(/GMT.*/i, "");
}
