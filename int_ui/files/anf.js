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

function initWin(workspace_name, common_title) {
    sDSName = workspace_name; 
    sDSKind = "ws";
    sCommonTitle = common_title;
    sUnitsH.init("ds=" + sDSName, false);
    window.name = sCommonTitle + ":" + sDSName;
    document.getElementById("ds-name").innerHTML = sDSName;
    
    window.onkeydown = onKey;
    window.onclick   = onClick;
    window.onresize  = arrangeControls;

    initMonitor();
    checkWorkZone(null);
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
    relaxView();
}

function loadList(filter_name, zone_data, use_conditions) {
    sViewH.dropOff();
    ajaxCall("list", sConditionsH.getCondRqArgs(
        filter_name, zone_data, use_conditions), setupList);
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
    sRecList = info["records"];
    refreshRecList();
    arrangeControls();
}

function arrangeControls() {
    if (sSamplesCtrl != null) {
        sSamplesCtrl.arrangeControls();
        return;
    }
    
    document.getElementById("top").style.height = 60;
    document.getElementById("rec-list").style.height = window.innerHeight - 61;
    
    zone_mod_height = document.getElementById("zone-mod").getBoundingClientRect().height;
    document.getElementById("work-zone-area").style.height = zone_mod_height - 60;
    document.getElementById("work-zone-wrap-list").style.height = zone_mod_height - 125;
}

function refreshRecList() {
    sViewRecNoSeq = [];
    var rep = [];
    for (rec_no = 0; rec_no < sRecList.length; rec_no++) {
        rec_id = sRecList[rec_no][0];
        label  = sRecList[rec_no][1];
        color  = sRecList[rec_no][2];
        marked = sRecList[rec_no][3];
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
    window.frames['rec-frame1'].location.replace("rec?ds=" + sDSName + 
        "&rec=" + sCurRecID + "&port=1" + "&details=" + sRecList[sCurRecNo][4]);
    window.frames['rec-frame2'].location.replace("rec?ds=" + sDSName + 
        "&rec=" + sCurRecID + "&port=2" + "&details=" + sRecList[sCurRecNo][4]);
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

function refreshCohorts() {
    for (idx = 1; idx < 3; idx++) {
        frame = window.frames['rec-frame' + idx];
        if (frame.sStarted) 
            frame.refreshCohorts();
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
    var args = sConditionsH.getCondRqArgs(sCurFilterName, sCurZoneData, true);
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
function onModalOff() {
}

