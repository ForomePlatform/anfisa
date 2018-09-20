var sRecTags      = null;
var sTagOrder      = null;
var sCurTagIdx     = null;
var sTagNameOK     = null;
var sTagCntMode    = null;
var sTagCntChanged = null;
var sTimeH         = null;
var sPrevTag       = null;
var sHasTags       = null;

var sBtnNewTag    = null;
var sBtnSaveTag   = null;
var sBtnCancelTag = null;
var sBtnDeleteTag = null;
var sBtnUndoTag   = null;
var sBtnRedoTag   = null;
var sBtnClearTags = null;
var sInpTagName   = null;
var sInpTagValue  = null;
var sInpTagNameList = null;

function initTagsEnv() {
    sBtnNewTag      = document.getElementById("tg-tag-new"); 
    sBtnCreateTag   = document.getElementById("tg-tag-create"); 
    sBtnSaveTag     = document.getElementById("tg-tag-save"); 
    sBtnCancelTag   = document.getElementById("tg-tag-cancel"); 
    sBtnDeleteTag   = document.getElementById("tg-tag-delete"); 
    sBtnUndoTag     = document.getElementById("tg-tag-undo"); 
    sBtnRedoTag     = document.getElementById("tg-tag-redo"); 
    sBtnClearTags   = document.getElementById("tg-tag-clear-all"); 
    sInpTagName     = document.getElementById("tg-tag-name"); 
    sInpTagValue    = document.getElementById("tg-tag-value-content");
    sInpTagNameList = document.getElementById("tg-tags-tag-list");
    loadTags(null);
}

function loadTags(tags_to_update){
    if (sViewPort > 0) {
        if (parent.window.sCurRecID == null)
            return;
        ws_name = parent.window.sWorkspaceName;
        rec_id = parent.window.sCurRecID;
        app_modes = parent.window.sAppModes;
    } else {
        ws_name = sAloneWS;
        rec_id = sAloneRecID;
        app_modes = "";
    }
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupTags(info);
        }
    };
    xhttp.open("POST", "tags", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + ws_name +  "&m=" + encodeURIComponent(app_modes) + 
        "&rec=" + rec_id;
    if (tags_to_update) 
        args += "&tags=" + encodeURIComponent(JSON.stringify(tags_to_update)); 
    xhttp.send(args); 
}

function setupTags(info) {
    sRecTags  = info["rec-tags"];
    sCurTagIdx = null;
    sHasTags   = false;
    
    var el = document.getElementById("tg-filters-list");
    if (info["filters"]) {
        el.innerHTML = info["filters"].join(' ');
        el.className = "";
    } else {
        el.innerHTML = "none";
        el.className = "empty";
    }

    check_tags = info["check-tags"]
    var rep = [];
    for (j=0; j< check_tags.length; j++) {
        tag_name = check_tags[j];
        rep.push('<div class="tag-check"><input id="check-tag--' + tag_name + '" ' +
            ((sRecTags[tag_name])?"checked ":"") + 
            'type="checkbox" onclick="checkTagCheck(\'' + tag_name + '\');"/>&nbsp;' +
            tag_name + '</div>');
        sHasTags |= !!sRecTags[tag_name];
    }
    document.getElementById("tg-check-tags-list").innerHTML = rep.join('\n');
    
    op_tags = info["op-tags"];
    sTagOrder = [];
    rep = [];
    for (j = 0; j < op_tags.length; j++) {
        tag_name = op_tags[j];
        if (!sRecTags[tag_name])
            continue
        idx = sTagOrder.length;
        sTagOrder.push(tag_name);
        rep.push('<div id="tag--' + idx + '" class="tag-label" ' +
            'onclick="pickTag(' + idx + ');">' + tag_name + '</div>');
        sHasTags = true;
    }
    document.getElementById("tg-op-tags-list").innerHTML = rep.join('\n');
    if (sTagOrder.length > 0) {
        idx = sTagOrder.indexOf(sPrevTag);
        if (idx < 0 && sViewPort > 0)
            idx = sTagOrder.indexOf(window.parent.sCurTag);
        pickTag((idx >=0)? idx: 0);
    }
    
    sBtnUndoTag.disabled = (sViewPort < 1) || !info["can_undo"];
    sBtnRedoTag.disabled = (sViewPort < 1) || !info["can_redo"];

    updateTagsState(true);
    
    for (idx = sInpTagNameList.length - 1; idx > 0; idx--) {
        sInpTagNameList.remove(idx);
    }
    
    op_tags = info["op-tags"];
    for (idx = 0; idx < op_tags.length; idx++) {
        tag_name = op_tags[idx];
        if (sTagOrder.indexOf(tag_name) < 0) {
            var option = document.createElement('option');
            option.innerHTML = tag_name;
            option.value = tag_name;
            sInpTagNameList.append(option)
        }
    }
    sInpTagNameList.selectedIndex = 0;
    if (info["marker"]) {
        parent.window.updateRecordMark(info["marker"][0], info["marker"][1])
    }
}

function updateTagsState(set_content) {
    sBtnClearTags.disabled  = (sViewPort < 1) || (!sHasTags);
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
            sInpTagValue.value = ("" + sRecTags[tag_name]).trim();
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
        sTagNameOK = /^[A-Za-z0-9_\-]+$/i.test(tag_name) && tag_name[0] != '_'
            && sTagOrder.indexOf(tag_name) < 0;
        sTagCntChanged = !!(sInpTagValue.value.trim());
        
    } else {
        sTagNameOK = true;
        if (sTagCntMode) {
            tag_name = sTagOrder[sCurTagIdx];
            sTagCntChanged = (sInpTagValue.value.trim() != 
                ("" + sRecTags[tag_name]).trim());            
        } else {
            sTagCntChanged = false;
        }
    }
    sInpTagName.className = (sTagNameOK == false)? "bad": "";
    sInpTagName.disabled  = (sViewPort < 1) || sCurTagIdx != null;
    sInpTagValue.disabled = (sViewPort < 1) || !sTagCntMode;
    sInpTagNameList.disabled = (sViewPort < 1) || (sCurTagIdx != null);
    
    sBtnNewTag.disabled     = (sViewPort < 1) || (sCurTagIdx == null);
    sBtnSaveTag.disabled    = (sViewPort < 1) || !(sTagCntMode && sTagNameOK && 
        (sCurTagIdx == null || sTagCntChanged));
    sBtnCancelTag.disabled  = (sViewPort < 1) || (!sTagCntChanged) || 
        (sCurTagIdx != null || sInpTagName.value.trim() != "");
    sBtnDeleteTag.disabled  = (sViewPort < 1) || (sCurTagIdx == null);
        
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
    if (sViewPort < 1)
        return;
    if (sCurTagIdx != null) {
        dropCurTag();
        updateTagsState(true);
    }
}

function tagEnvSave(force_it) {
    if (sViewPort < 1)
        return;
    if (!force_it) {
        checkInputs();
        if (!(sTagCntMode && sTagNameOK))
            return;
    }
    tags_to_update = sRecTags;
    tags_to_update[sInpTagName.value] = sInpTagValue.value.trim();
    sPrevTag = sInpTagName.value;
    loadTags(tags_to_update);
    window.parent.checkTabNavigation(sPrevTag);
}

function tagEnvCancel() {
    if (sViewPort < 1)
        return;
    updateTagsState(true);
}

function tagEnvDelete() {
    if (sViewPort < 1)
        return;
    checkInputs();
    if (sCurTagIdx != null) {
        tag_name = sTagOrder[sCurTagIdx];
        tags_to_update = sRecTags;
        delete tags_to_update[tag_name];
        sPrevTag = null;
        sCurTagIdx = null;
        loadTags(tags_to_update);
        window.parent.checkTabNavigation(tag_name);
    }
}

function tagEnvClearAll() {
    if (sViewPort < 1)
        return;
    if (sHasTags) {
        sPrevTag = null;
        sCurTagIdx = null;
        loadTags({});
        window.parent.checkTabNavigation(null);       
    }
}

function tagEnvUndo() {
    if (sViewPort < 1)
        return;
    if (!sBtnUndoTag.disabled) {
        sPrevTag = (sCurTagIdx != null)? sTagOrder[sCurTagIdx] :  null;
        sCurTagIdx = null;
        loadTags("UNDO");
        window.parent.checkTabNavigation(null);
    }
}

function tagEnvRedo() {
    if (sViewPort < 1)
        return;
    if (!sBtnRedoTag.disabled) {
        sPrevTag = (sCurTagIdx != null)? sTagOrder[sCurTagIdx] :  null;
        sCurTagIdx = null;
        loadTags("REDO");
        window.parent.checkTabNavigation(null);
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

function tagEnvTagSel() {
    if (sCurTagIdx == null) {
        sInpTagName.value = sInpTagNameList.value;
    }
}

function checkTagCheck(tag_name) {
    sRecTags[tag_name] = document.getElementById("check-tag--" + tag_name).checked;
    tagEnvSave(true);
}