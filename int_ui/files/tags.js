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

var sRecTags       = null;
var sTagOrder      = null;
var sCheckTags     = null;
var sCurTagIdx     = null;
var sTagNameOK     = null;
var sTagCntChanged = null;
var sTimeH         = null;
var sPrevTag       = null;
var sHasTags       = null;
var sTagsArgs      = null;
var sMasterCtrl    = null;

var sBtnNewTag    = null;
var sBtnSaveTag   = null;
var sBtnCancelTag = null;
var sBtnDeleteTag = null;
var sBtnClearTags = null;
var sInpTagName   = null;
var sInpTagValue  = null;
var sInpTagNameList = null;

function initTagsEnv(ws_name, rec_id, master_ctrl) {
    sBtnNewTag      = document.getElementById("tg-tag-new"); 
    sBtnCreateTag   = document.getElementById("tg-tag-create"); 
    sBtnSaveTag     = document.getElementById("tg-tag-save"); 
    sBtnCancelTag   = document.getElementById("tg-tag-cancel"); 
    sBtnDeleteTag   = document.getElementById("tg-tag-delete"); 
    sBtnClearTags   = document.getElementById("tg-tag-clear-all"); 
    sInpTagName     = document.getElementById("tg-tag-name"); 
    sInpTagValue    = document.getElementById("tg-tag-value-content");
    sInpTagNameList = document.getElementById("tg-tags-tag-list");
    sTagsArgs = "ds=" + ws_name +  "&rec=" + rec_id;
    sMasterCtrl = master_ctrl;
    loadTags(null);
}

function loadTags(tags_to_update) {
    var args = sTagsArgs;
    if (tags_to_update) 
        args += "&tags=" + encodeURIComponent(JSON.stringify(tags_to_update)); 
    ajaxCall("tags", args, setupTags);
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

    sCheckTags = info["check-tags"]
    var rep = [];
    for (j=0; j< sCheckTags.length; j++) {
        tag_name = sCheckTags[j];
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
        var tag_name = op_tags[j];
        if (sRecTags[tag_name] == undefined)
            continue
        if (tag_name == "_note") 
            tag_title = "_note...";
        else 
            tag_title = tag_name + ((sRecTags[tag_name])? '...':'');
        idx = sTagOrder.length;
        sTagOrder.push(tag_name);
        rep.push('<div id="tag--' + idx + '" class="tag-label" ' +
            'onclick="pickTag(' + idx + ');">' + tag_title + '</div>');
        sHasTags = true;
    }
    document.getElementById("tg-op-tags-list").innerHTML = rep.join('\n');
    if (sTagOrder.length > 0) {
        idx = sTagOrder.indexOf(sPrevTag);
        if (idx < 0 && sViewPort > 0)
            idx = sTagOrder.indexOf(sMasterCtrl.getCurTag());
        pickTag((idx >=0)? idx: 0);
    }
    
    updateTagsState();
    
    for (idx = sInpTagNameList.length - 1; idx > 0; idx--) {
        sInpTagNameList.remove(idx);
    }
    
    op_tags = info["op-tags"];
    for (idx = 0; idx < op_tags.length; idx++) {
        tag_name = op_tags[idx];
        if (tag_name == "_note")
            continue;
        if (sTagOrder.indexOf(tag_name) < 0) {
            var option = document.createElement('option');
            option.innerHTML = tag_name;
            option.value = tag_name;
            sInpTagNameList.append(option)
        }
    }
    var option = document.createElement('option');
    option.innerHTML = "_note";
    option.value = "_note";
    sInpTagNameList.append(option);
    sInpTagNameList.selectedIndex = -1;
    document.getElementById("tags-time").innerHTML = (info["upd-time"])?
        ('Updated: <span class="note-time">' + 
            timeRepr(info["upd-time"]) + '</span>') : '';
    sMasterCtrl.updateTagsInfo(info);
}

function updateTagsState() {
    sBtnClearTags.disabled  = (sViewPort < 1) || (!sHasTags);
    if (sCurTagIdx == null) {
        //sInpTagName.value = "";
        sInpTagValue.value = "";
    } else {
        tag_name = sTagOrder[sCurTagIdx];
        sInpTagName.value = tag_name;
        tag_val = sRecTags[tag_name];
        sInpTagValue.value = ((tag_val != undefined)? "" + tag_val:"").trim();
    }
    checkTagInputs();
}

function checkTagInputs() {    
    var tag_name = sInpTagName.value.trim();
    pickTag(sTagOrder.indexOf(tag_name));
    if (sCurTagIdx == null) {
        sTagNameOK = tag_name && tag_name.length > 0 && 
            (tag_name == "_note" || 
                (tag_name.indexOf('_') < 0 && 
                tag_name[0].toLowerCase() != tag_name[0].toUpperCase())) &&
            sCheckTags.indexOf(tag_name) < 0;
        sTagCntChanged = !!(sInpTagValue.value.trim());
    } else {
        sTagNameOK = true;
        sTagCntChanged = (sInpTagValue.value.trim() != 
            ("" + sRecTags[tag_name]).trim());            
    }
    sInpTagName.className = (sTagNameOK == false)? "bad": "";
    sInpTagName.disabled  = (sViewPort < 1);
    sInpTagValue.disabled = (sViewPort < 1) || !sTagNameOK;
    sInpTagNameList.disabled = (sViewPort < 1);
    
    sBtnNewTag.disabled     = (sViewPort < 1) || !sTagNameOK || (sCurTagIdx != null);
    sBtnSaveTag.disabled    = (sViewPort < 1) || !(sTagNameOK && 
        (sCurTagIdx != null) && sTagCntChanged);
    sBtnCancelTag.disabled  = (sViewPort < 1) || (!sTagCntChanged) || 
        (sCurTagIdx == null);
    sBtnDeleteTag.disabled  = (sViewPort < 1) || (sCurTagIdx == null);
        
    if (sTimeH == null) 
        sTimeH = setInterval(checkTagInputs, 200);
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
    if (sCurTagIdx == null && sTagNameOK) {
        tagEnvSave(true);
    }
    if (sCurTagIdx != null) {
        dropCurTag();
        updateTagsState();
    }
}

function tagEnvSave(force_it) {
    if (sViewPort < 1)
        return;
    if (!force_it) {
        checkTagInputs();
        if (!sTagNameOK)
            return;
    }
    tags_to_update = sRecTags;
    tags_to_update[sInpTagName.value] = sInpTagValue.value.trim();
    sPrevTag = sInpTagName.value;
    loadTags(tags_to_update);
    sMasterCtrl.updateNavigation(sPrevTag);
}

function tagEnvCancel() {
    if (sViewPort < 1)
        return;
    updateTagsState();
}

function tagEnvDelete() {
    if (sViewPort < 1)
        return;
    checkTagInputs();
    if (sCurTagIdx != null) {
        tag_name = sTagOrder[sCurTagIdx];
        tags_to_update = sRecTags;
        delete tags_to_update[tag_name];
        sPrevTag = null;
        sCurTagIdx = null;
        loadTags(tags_to_update);
        sMasterCtrl.updateNavigation(tag_name);
    }
}

function tagEnvClearAll() {
    if (sViewPort < 1)
        return;
    if (sHasTags) {
        sPrevTag = null;
        sCurTagIdx = null;
        loadTags({});
        sMasterCtrl.updateNavigation(null);       
    }
}

function pickTag(idx) {
    if (idx < 0) {
        idx = null;
    }
    if (idx != sCurTagIdx) {
        dropCurTag();
        sCurTagIdx = idx;
        if (sCurTagIdx != null) {
            el = document.getElementById("tag--" + sCurTagIdx);
            el.className = el.className + " cur";
        }
        updateTagsState();
    }
}

function tagEnvTagSel() {
    pickTag(-1);
    sInpTagName.value = sInpTagNameList.value;
    checkTagInputs();
}

function checkTagCheck(tag_name) {
    sRecTags[tag_name] = document.getElementById("check-tag--" + tag_name).checked;
    tagEnvSave(true);
}

//=====================================
function timeRepr(time_label) {
    var dt = new Date(time_label);
    return dt.toLocaleString("en-US").replace(/GMT.*/i, "");
}
