var sTagsInfo      = null;
var sTagOrder      = null;
var sCurTagIdx     = null;
var sTagNameOK     = null;
var sTagCntMode    = null;
var sTagCntChanged = null;
var sTimeH         = null;
var sPrevTag       = null;

var sBtnNewTag    = null;
var sBtnSaveTag   = null;
var sBtnCancelTag = null;
var sBtnDeleteTag = null;
var sInpTagName   = null;
var sInpTagValue  = null;

function initTagsEnv() {
    sBtnNewTag      = document.getElementById("tg-tag-new"); 
    sBtnCreateTag   = document.getElementById("tg-tag-create"); 
    sBtnSaveTag     = document.getElementById("tg-tag-save"); 
    sBtnCancelTag   = document.getElementById("tg-tag-cancel"); 
    sBtnDeleteTag   = document.getElementById("tg-tag-delete"); 
    sInpTagName     = document.getElementById("tg-tag-name"); 
    sInpTagValue    = document.getElementById("tg-tag-value-content");
    loadTags(null);
}

function loadTags(tags_to_update){
    if (parent.window.sCurRecNo == null)
        return;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupTags(info);
        }
    };
    xhttp.open("POST", "tags", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + parent.window.sWorkspaceName + 
        "&m=" + encodeURIComponent(parent.window.sAppModes) + 
        "&rec=" + parent.window.sCurRecNo;
    if (tags_to_update) 
        args += "&tags=" + encodeURIComponent(JSON.stringify(tags_to_update)); 
    xhttp.send(args); 
}

function setupTags(info) {
    sTagsInfo  = info;
    sCurTagIdx = null;
    
    var el = document.getElementById("tg-filters-list");
    if (sTagsInfo["filters"]) {
        el.innerHTML = sTagsInfo["filters"].join(' ');
        el.className = "";
    } else {
        el.innerHTML = "none";
        el.className = "empty";
    }

    sTagOrder = [];
    for(var tag in info["tags"]) {
        sTagOrder.push(tag);
    }
    sTagOrder.sort();
    var rep = [];
    for (idx = 0; idx < sTagOrder.length; idx++) {
        rep.push('<div id="tag--' + idx + '" class="tag-label" ' +
            'onclick="pickTag(' + idx + ');">' + sTagOrder[idx] + '</div>');
    }
    document.getElementById("tg-tags-list").innerHTML = rep.join('\n');
    if (sTagOrder.length > 0) {
        idx = sTagOrder.indexOf(sPrevTag);
        pickTag((idx >=0)? idx: 0);
    }
    
    updateTagsState(true);
}

function updateTagsState(set_content) {
    if (set_content) {
        if (sCurTagIdx == null) {
            sInpTagName.value = "";
            sInpTagValue.value = "";
            sTagNameOK = false;
            sTagCntMode = true;
            sTagCntChanged = false;
        } else {
            tag_name = sTagOrder[sCurTagIdx];
            sInpTagName.value = tag_name;
            sInpTagValue.value = sTagsInfo["tags"][tag_name].trim();
            sTagNameOK = true;
            sTagCntMode = true;
            sTagCntChanged = false;
        }
    }
    checkInputs();
}

function checkInputs() {    
    if (sCurTagIdx == null) {
        tag_name = sInpTagName.value.trim();
        sTagNameOK = /^[A-Za-z_]+$/i.test(tag_name) && tag_name[0] != '_'
            && sTagOrder.indexOf(tag_name) < 0;
        sTagCntChanged = !!(sInpTagValue.value.trim());
        
    } else {
        sTagNameOK = true;
        if (sTagCntMode) {
            tag_name = sTagOrder[sCurTagIdx];
            sTagCntChanged = (sInpTagValue.value.trim() != 
                sTagsInfo["tags"][tag_name].trim());            
        } else {
            sTagCntChanged = false;
        }
    }
    sInpTagName.className = (sTagNameOK == false)? "bad": "";
    sInpTagName.disabled  = sCurTagIdx != null;
    sInpTagValue.disabled = !sTagCntMode;
    
    sBtnNewTag.disabled     = (sCurTagIdx == null);
    sBtnSaveTag.disabled    = !(sTagCntMode && sTagNameOK && 
        (sCurTagIdx == null || sTagCntChanged));
    sBtnCancelTag.disabled  = (!sTagCntChanged) || 
        (sCurTagIdx != null || sInpTagName.value.trim() != "");
    sBtnDeleteTag.disabled  = (sCurTagIdx == null);
    
    if (sTagCntMode) {
        if (sTimeH == null) 
            sTimeH = setInterval(checkInputs, 200);
    } else {
        if (sTimeH != null) {
            clearInterval(sTimeH);
            sTimeH = null;
        }
    }
}

function dropCurTag() {
    if (sCurTagIdx != null) {
        el = document.getElementById("tag--" + sCurTagIdx);
        el.className = el.className.replace(" cur", "");
    }
    sCurTagIdx = null;
}

function tagEnvNew() {
    if (sCurTagIdx != null) {
        dropCurTag();
        updateTagsState(true);
    }
}

function tagEnvSave() {
    checkInputs();
    if (sTagCntMode && sTagNameOK) {
        tags_to_update = sTagsInfo["tags"];
        tags_to_update[sInpTagName.value] = sInpTagValue.value.trim();
        sPrevTag = sInpTagName.value;
        loadTags(tags_to_update);
    }
}

function tagEnvCancel() {
    updateTagsState(true);
}

function tagEnvDelete() {
    checkInputs();
    if (sCurTagIdx != null) {
        tag_name = sTagOrder[sCurTagIdx];
        tags_to_update = sTagsInfo["tags"];
        delete tags_to_update[tag_name];
        sPrevTag = null;
        sCurTagIdx = null;
        loadTags(tags_to_update);
    }
}

function pickTag(idx) {
    if (idx != sCurTagIdx) {
        dropCurTag();
        sCurTagIdx = idx;
        el = document.getElementById("tag--" + sCurTagIdx);
        el.className = el.className + " cur";
        updateTagsState(true);
    }
}