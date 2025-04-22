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

sCommonTitle = null;
sDSName = null;
sDocInfo = null;
sDocArray = null;
sCurDoc = null;

function initReportPage(ds_name, ds_kind, common_title){
    sDSName = ds_name;
    sDSKind = ds_kind;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName + ":DOC";
    ajaxCall("dsinfo", "ds=" + sDSName, setupDocList);
    window.onresize  = arrangeControls;
    document.getElementById("ds-name").innerHTML = sDSName;
    arrangeControls();
}

function arrangeControls() {
    document.getElementById("right").style.width = 
        Math.max(window.innerWidth - 255, 30);
    document.getElementById("doc-content").style.height = 
        Math.max(window.innerHeight - 70, 30) + "px";
}

function setupDocList(info) {
    sDocInfo = info;
    var doc_path = "dsdoc/" + sDSName + "/";
    sDocArray = [];
    var list_doc_rep = [];
    _fillDocFolder(sDocInfo["doc"][1], "", sDocArray, doc_path, list_doc_rep);
    for (var j = 0; j < sDocInfo["ancestors"].length; j++) {
        var base_name = sDocInfo["ancestors"][j][0];
        var base_doc = sDocInfo["ancestors"][j][1];
        if (base_doc == null)
            continue;
        var doc_title = "Base";
        if (j > 0) {
            doc_title = (j + 1 < sDocInfo["ancestors"].length)? 
                ("Base-" + (j+1)) : ("Root");
        }
        list_doc_rep.push('<div class="grp-ref"><span>' + 
            doc_title + ' ' + base_name + '</span>');
        _fillDocFolder(base_doc[1], doc_title + " ", 
            sDocArray, "dsdoc/" + base_name + "/", list_doc_rep);
        list_doc_rep.push('</div>');
    }
    document.getElementById("doc-list").innerHTML = list_doc_rep.join('\n');
    selectDoc(0);
}

function _fillDocFolder(doc_seq, prefix, doc_array, doc_path, list_doc_rep) {
    for (var idx = 0; idx < doc_seq.length; idx++) {
        doc_entry = doc_seq[idx];
        if (Array.isArray(doc_entry[1])) {
            list_doc_rep.push('<div class="grp-ref"><span>' + 
                doc_entry[0] + '</span>');
            _fillDocFolder(doc_entry[1], prefix, doc_array, doc_path, list_doc_rep);
            list_doc_rep.push('</div>');
            continue;
        }
        list_doc_rep.push('<div id="doc__' + sDocArray.length + 
            '" class="doc-ref" onclick="selectDoc(' + sDocArray.length + 
            ')">&#x2022;' + prefix + doc_entry[0] + '</div>');
        doc_array.push(doc_path + doc_entry[1]);
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
    document.getElementById("doc-title").innerHTML = cur_el.innerHTML.substring(1);
    window.frames["doc-content"].location.replace(sDocArray[sCurDoc]);
}
