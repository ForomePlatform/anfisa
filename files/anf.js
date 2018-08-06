var sCurRecNo = null;
var sCurRecTab = null;
var sCurDataSet = null;

function changeRec(rec_no) {
    if (sCurRecNo == rec_no) 
        return;
    new_rec_el = document.getElementById("li--" + rec_no);
    if (new_rec_el == null) 
        return;
    if (sCurRecNo != null) 
        document.getElementById("li--" + sCurRecNo).className = "";
    sCurRecNo = rec_no;
    new_rec_el.className = "press";
    softScroll(new_rec_el);
    document.getElementById("record").src = 
        "rec?data=" + sCurDataSet + "&rec=" + sCurRecNo;
    document.getElementsByClassName("top-left")[0].scrollIntoView(true);
}

function onkey(event_key) {
    if (event_key.code == "ArrowUp" && sCurRecNo > 0) {
        changeRec(sCurRecNo - 1);
    }
    if (event_key.code == "ArrowDown") {
        changeRec(sCurRecNo + 1);
    }
}

function softScroll(nd) {
    if (nd != null) {
        var rect = nd.getBoundingClientRect();
        var rect_parent = nd.parentNode.getBoundingClientRect();
        if (rect.top + rect.height < rect_parent.top + 50) {
            nd.scrollIntoView(true);
        }  else if (rect.top + 50 >  rect_parent.top + rect_parent.height) {
            nd.scrollIntoView(false);
        }
    }
}
