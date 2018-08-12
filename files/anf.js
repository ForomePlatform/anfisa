var sCurRecNo = null;
var sCurRecTab = null;
var sCurDataSet = null;

var sNodeModalBack    = null;
var sNodeFilterMod    = null;
var sNodeOpenFilter   = null;
var sNodeCloseFilter = null;

function initWin(data_set_name) {
    sCurDataSet = data_set_name; 
    sNodeModalBack  = document.getElementById("modal-back");
    sNodeFilterMod  = document.getElementById("filter-mod");
    sNodeOpenFilter = document.getElementById("open-filter");
    sNodeCloseFilter = document.getElementById("close-filter");
    window.onkeydown = onKey;
    window.onclick   = onClick;
    changeRec(0);
}

function changeRec(rec_no) {
    if (sCurRecNo == rec_no) 
        return;
    var new_rec_el = document.getElementById("li--" + rec_no);
    if (new_rec_el == null) 
        return;
    if (sCurRecNo != null) {
        var prev_el = document.getElementById("li--" + sCurRecNo);
        prev_el.className = prev_el.className.replace(" press", "");
    }
    sCurRecNo = rec_no;
    new_rec_el.className = new_rec_el.className + " press";
    softScroll(new_rec_el);
    document.getElementById("record").src = 
        "rec?data=" + sCurDataSet + "&rec=" + sCurRecNo;
}

function onKey(event_key) {
    if (event_key.code == "ArrowUp" && sCurRecNo > 0)
        changeRec(sCurRecNo - 1);
    if (event_key.code == "ArrowDown") 
        changeRec(sCurRecNo + 1);
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
    sel = document.getElementById("data_set");
    new_data_set = sel.options[sel.selectedIndex].text;
    if (sCurDataSet != new_data_set)
        window.location = "?data=" + new_data_set;
}

//=====================================
