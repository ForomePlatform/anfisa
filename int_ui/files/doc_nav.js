sCommonTitle = null;
sDSName = null;
sDocListInfo = null;
sDocArray = null;
sCurDoc = null;

function initReportPage(ds_name, common_title){
    sDSName = ds_name;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName + ":DOC";
    ajaxCall("dsinfo", "ds=" + sDSName, setupDocList);
    window.onresize  = arrangeControls;
    arrangeControls();
}

function arrangeControls() {
    document.getElementById("right").style.width = 
        document.getElementById("all").style.width - 155;
    document.getElementById("doc-content").style.height = 
        document.getElementById("all").style.height - 55;
}


function setupDocList(info) {
    sDocListInfo = info["doc"];
    var doc_path = "../doc/" + sDSName + "/";
    sDocArray = [];
    var list_doc_rep = [];
    sDocArray.push(doc_path + "info.html");
    list_doc_rep.push('<div id="doc__0" class="doc-ref" onclick="selectDoc(0)">Info</div>');
    for (idx = 0; idx < sDocListInfo.length; idx++) {
    }
    document.getElementById("doc-list").innerHTML = list_doc_rep.join('\n');
    selectDoc(0);
}

function selectDoc(doc_no){
    if (doc_no == sCurDoc)
        return;
    if (sCurDoc != null) 
        document.getElementById("doc__" + sCurDoc).className = "doc-ref";
    sCurDoc = doc_no;
    cur_el = document.getElementById("doc__" + sCurDoc);
    cur_el.className = "doc-ref cur";
    document.getElementById("doc-title").innerHTML = sDSName + ": " + cur_el.innerHTML;
    window.frames["doc-content"].location.replace(sDocArray[sCurDoc]);
}