var sTitlePrefix = null;
var sCurRecIdx = null;
var sCurRecTab = null;
var sCurDataSet = null;
var sCurRandPortion = 1;
var sRecList = null;
var sRecSamples = null;
var sViewRecNoSeq = null;

var sNodeModalBack    = null;

function initWin(data_set_name) {
    sTitlePrefix = window.document.title;
    sCurDataSet = data_set_name; 
    sNodeModalBack  = document.getElementById("modal-back");
    window.onkeydown = onKey;
    window.onclick   = onClick;
    document.getElementById("list-rand-portion").value = sCurRandPortion;
    loadList();
}

function loadList() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupList(info);
        }
    };
    xhttp.open("POST", "list", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("data=" + sCurDataSet + "&filter="+ 
        encodeURIComponent(JSON.stringify(sCurFilter))); 
}

function setupList(info) {
    sCurDataSet = info["data-set"]; 
    document.getElementById("data_set").value = sCurDataSet;
    window.document.title = sTitlePrefix + ": " + sCurDataSet;
    var el = document.getElementById("list-report");
    var el_p = document.getElementById("list-rand-portion");
    var rep = "Records: <b>" + info["filtered"] + "<b>";
    if (info["total"] != info["filtered"]) {
        rep += "/" + info["total"];
    }
    if (info["list-mode"] == "samples") {
        rep += "<br/>Samples:";
        el_p.style.visibility = "visible";
        sRecSamples = true;
    } else {
        el_p.style.visibility = "hidden";
        sRecSamples = false;
    }
    el.innerHTML = rep;
    sRecList = info["records"];
    refreshRecList();
    setupStatList(info["stats"]);
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
            ')";">' + sRecList[idx][1] + '</div>');
    }
    document.getElementById("rec-list").innerHTML = rep.join('\n');
    sCurRecIdx = null;
    if (sViewRecNoSeq.length == 0) 
        document.getElementById("record").src = "norecords";
    else 
        changeRec(0);
}

function changeRec(rec_idx) {
    if (sCurRecIdx == rec_idx) 
        return;
    var new_rec_el = document.getElementById("li--" + sViewRecNoSeq[rec_idx]);
    if (new_rec_el == null) 
        return;
    if (sCurRecIdx != null) {
        var prev_el = document.getElementById("li--" + sViewRecNoSeq[sCurRecIdx]);
        prev_el.className = prev_el.className.replace(" press", "");
    }
    sCurRecIdx = rec_idx;
    new_rec_el.className = new_rec_el.className + " press";
    softScroll(new_rec_el);
    document.getElementById("record").src = 
        "rec?data=" + sCurDataSet + "&rec=" + sViewRecNoSeq[sCurRecIdx];
}

function onKey(event_key) {
    if (event_key.code == "ArrowUp" && sCurRecIdx > 0)
        changeRec(sCurRecIdx - 1);
    if (event_key.code == "ArrowDown") 
        changeRec(sCurRecIdx + 1);
}

function onClick(event_ms) {
    if (event_ms.target == sNodeModalBack)
        filterModOff();
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

function filterModOn() {
    sNodeModalBack.style.display = "block";
}

function filterModOff() {
    sNodeModalBack.style.display = "none";
}

function changeDataSet() {
    new_data_set = document.getElementById("data_set").value;
    if (sCurDataSet != new_data_set) {
        sCurDataSet = new_data_set;
        loadList();
    }
}

function listRandPortion() {
    new_rand_p = (document.getElementById("list-rand-portion").value);
    if (sCurRandPortion != new_rand_p) {
        sCurRandPortion = new_rand_p;
        refreshRecList();
    }
}
//=====================================
