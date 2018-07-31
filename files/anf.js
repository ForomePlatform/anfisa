var sCurRecId = null;
var sCurRecTab = null;

function changeRec(data_set, rec_id) {
    if (sCurRecId != null) {
        document.getElementById("li--" + sCurRecId).className = "";
    }
    sCurRecId = rec_id;
    document.getElementById("li--" + sCurRecId).className = "press";
    document.getElementById("record").src = 
        "rec?data=" + data_set + "&rec=" + sCurRecId;
}
