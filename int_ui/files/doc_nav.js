sCommonTitle = null;
sDSName = null;
sDocInfo = null;
sDocArray = null;
sCurDoc = null;

function initReportPage(ds_name, common_title){
    sDSName = ds_name;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName + ":DOC";
    ajaxCall("dsinfo", "ds=" + sDSName, setupDocList);
    window.onresize  = arrangeControls;
    document.getElementById("ds-name").innerHTML = sDSName;
    arrangeControls();
}

function arrangeControls() {
    document.getElementById("right").style.width = 
        document.getElementById("all").style.width - 255;
    document.getElementById("doc-content").style.height = 
        document.getElementById("all").style.height - 55;
}

function setupDocList(info) {
    sDocInfo = info;
    var doc_path = "doc/" + sDSName + "/";
    sDocArray = [];
    var list_doc_rep = [];
    list_doc_rep.push('<div id="doc__0" class="doc-ref" onclick="selectDoc(0)">Info</div>');
    sDocArray.push(doc_path + "info.html");
    _fillExtraDoc(sDocInfo["doc"], doc_path, "", list_doc_rep);
    if (sDocInfo["doc-base"] != undefined) {
        var doc_base_path = "doc/" + sDocInfo["base"] + "/";
        list_doc_rep.push('<div class="grp-ref"><span>XL-base ' + 
            sDocInfo["base"] + '</span>');
        list_doc_rep.push('<div id="doc__' + sDocArray.length + 
            '" class="doc-ref" onclick="selectDoc(' + sDocArray.length + 
            ')">XL-base info</div>');
        sDocArray.push(doc_base_path + "info.html");
        _fillExtraDoc(sDocInfo["doc-base"], doc_base_path, "XL-base ", list_doc_rep);
        sDocArray.push('</div>');
    }
    document.getElementById("doc-list").innerHTML = list_doc_rep.join('\n');
    selectDoc(0);
}

function _fillExtraDoc(doc_seq, prefix, doc_path, list_doc_rep) {
    for (var idx = 0; idx < doc_seq.length; idx++) {
        doc_entry = doc_seq[idx];
        list_doc_rep.push('<div id="doc__"' + sDocArray.length + 
            ' class="doc-ref" onclick="selectDoc(' + sDocArray.length + 
            ')">' + prefix + doc_entry[0] + '</div>');
        sDocArray.push(doc_path + doc_entry[1]);
    }
}

function selectDoc(doc_no){
    if (doc_no == sCurDoc)
        return;
    if (sCurDoc != null) 
        document.getElementById("doc__" + sCurDoc).className = "doc-ref";
    sCurDoc = doc_no;
    cur_el = document.getElementById("doc__" + sCurDoc);
    cur_el.className = "doc-ref cur";
    document.getElementById("doc-title").innerHTML = cur_el.innerHTML;
    window.frames["doc-content"].location.replace(sDocArray[sCurDoc]);
}

function goDS() {
    goToPage((sDocInfo["kind"] == "ws")? "WS":"XL");
}

function onModalOff() {
}