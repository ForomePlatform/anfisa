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
var sWsActShown = null;

var sNodeFilterBack  = null;
var sNodeZoneBack  = null;
var sNodeHotEvalBack = null;

function initWin(workspace_name, app_modes) {
    sTitlePrefix = window.document.title;
    sWorkspaceName = workspace_name; 
    sAppModes = app_modes;
    sNodeFilterBack  = document.getElementById("filter-back");
    sNodeZoneBack    = document.getElementById("zone-back");
    sNodeHotEvalBack = document.getElementById("hot-eval-back");
    window.onkeydown = onKey;
    window.onclick   = onClick;
    document.getElementById("list-rand-portion").value = sCurRandPortion;
    initMonitor();
    initFilters();
    checkWorkZone(null);
    wsActShow(false);
}

function loadList(filter_name, zone_data) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupList(info);
        }
    };
    xhttp.open("POST", "list", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + sWorkspaceName + "&m=" + encodeURIComponent(sAppModes);
    if (filter_name)
        args += "&filter=" + encodeURIComponent(filter_name);
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
        rec_no = sRecList[idx][0];
        sViewRecNoSeq.push(rec_no);
        rep.push('<div id="li--' + rec_no + '" class="rec-label ' +
            sRecList[idx][2] + '" onclick="changeRec(' + (idx - idx_from) + 
            ');">' + sRecList[idx][1] + '</div>');
    }
    document.getElementById("rec-list").innerHTML = rep.join('\n');
    if (sViewRecNoSeq.length == 0) {
        window.frames['rec-frame1'].location.replace("norecords");
        window.frames['rec-frame2'].location.replace("norecords");
    } else {
        idx = sViewRecNoSeq.indexOf(sCurRecNo);
        sCurRecNo = null;
        changeRec((idx >=0)? idx:0);
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
    if (event_ms.target == sNodeHotEvalBack)
        hotEvalModOff();
    if (sWsActShown && !event_ms.target.matches('.dropbtn')) {
        wsActShow(false);
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
    sNodeHotEvalBack.style.display = 
        (cur_mode_node == sNodeHotEvalBack)? "block":"none";
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

function hotEvalModOn() {
    setupHotEvalCtrl();
    _showModal(sNodeHotEvalBack);
}

function hotEvalModOff() {
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
function wsActShow(mode) {
    if (mode == undefined)
       sWsActShown = !sWsActShown;
    else
        sWsActShown = mode;
    document.getElementById("ws-dropdown-menu").className = (sWsActShown)? 
        "dropdown-content show":"dropdown-content";
}

function doWsExport() {
    alert("Export will be implemented soon");
}
