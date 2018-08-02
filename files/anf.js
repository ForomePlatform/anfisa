var sCurRecNo = null;
var sCurRecTab = null;

function changeRec(data_set, rec_no) {
    if (sCurRecNo != null) {
        document.getElementById("li--" + sCurRecNo).className = "";
    }
    sCurRecNo = rec_no;
    document.getElementById("li--" + sCurRecNo).className = "press";
    document.getElementById("record").src = 
        "rec?data=" + data_set + "&rec=" + sCurRecNo;
}
