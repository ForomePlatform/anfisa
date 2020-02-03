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

var sCommonTitle = null;
var sWsExtUrl = null;
var sDSName = null;
var sDSList = null;
var sDSDict = null;
var sCurIdx = null;

function setup(common_title, ws_ext_url) {
    sCommonTitle = common_title;
    sWsExtUrl = ws_ext_url;
    if (sDSName != null)
        window.name = sCommonTitle + ":" + sDSName + ":SUBDIR";
    else
        window.name = sCommonTitle + ":DIR";
    ajaxCall("dirinfo", "", setupDirData);
}

function setupSubDir(common_title, ws_ext_url, ds_name) {
    sDSName = ds_name;
    setup(common_title, ws_ext_url);
}

function setupDirData(info) {
    sDSList = info["ds-list"];
    sDSDict = info["ds-dict"];
    sCurIdx = null;
    document.getElementById("app-version").innerHTML = info["version"];
    document.getElementById("ds-info").innerHTML = "";
    var rep_seq = [];
    var idx_from = 0;
    var idx_to = sDSList.length;
    if (sDSName) {
        idx_from = sDSDict[sDSName]["v-idx"];
        idx_to = sDSDict[sDSName]["v-idx-to"];
    }
    var idx_cur = null;
    for (idx = idx_from; idx < idx_to; idx++) {
        ds_name = sDSList[idx];
        ds_info = sDSDict[ds_name];
        rep_seq.push('<div id="_ds_entry' + idx + '" ');
        if (ds_info["kind"]) {
            rep_seq.push('class="list-ds-entry" onclick="selectDS(' + 
                idx + ')">');
            if (idx_cur == null)
                idx_cur = idx;
        }
        else
            rep_seq.push('class="list-ds-empty-entry">');
        if (ds_info["v-level"] > 0) {
            spaces = [];
            for (j = 0; j < ds_info["v-level"]; j++)
                spaces.push('&emsp;');
            spaces.push('&#x25cb;&nbsp;')
            rep_seq.push(spaces.join(''));
        } else {
            if (!sDSName) 
                rep_seq.push(
                    '<span class="ds-ref" onclick="goToPage(\'SUBDIR\', \'' + 
                    ds_name + 
                    '\')" title="To sub-directory dataset page">&#x1f5c0;</span>&emsp;');
        }
        rep_seq.push(ds_name + '</div>');
    }
    arrangeControls();
    document.getElementById("dir-list").innerHTML = rep_seq.join('\n');
    selectDS(idx_cur);
}

function selectDS(ds_idx) {
    if (ds_idx == sCurIdx) 
        return;
    if (sCurIdx != null) {
        div_el = document.getElementById("_ds_entry" + sCurIdx);
        div_el.className = div_el.className.split(' ')[0];
    }
    sCurIdx = ds_idx;
    div_el = document.getElementById("_ds_entry" + sCurIdx);
    div_el.className = div_el.className.split(' ')[0] + ' cur';
    ds_info = sDSDict[sDSList[sCurIdx]];
    var rep_seq = ['<div id="ds-cur">'];
    if (ds_info["kind"] == "ws") {
        if (sWsExtUrl)
            rep_seq.push('<a class="ext-ref" href="' + sWsExtUrl + 
                '?ds=' + ds_info["name"] + '" target="_blank" ' +
                'title="To front end">&#x23f5;</a>')
        rep_seq.push(reprRef(ds_info["name"], "WS"));
    } else {
        rep_seq.push(reprRef(ds_info["name"], "XL"));
    }
    rep_seq.push('<span class="ref-zone">');
    if (ds_info["doc"] != undefined) 
        rep_seq.push(reprRef(ds_info["name"], "DOC", "[doc]"));
    rep_seq.push(reprRef(ds_info["name"], "DTREE", "[tree]"));
    rep_seq.push('<span></div>');
    if (ds_info["note"]) {
        rep_seq.push('<div class="ds-note">');
        rep_seq.push('<p class="comment">Note:');
        if (ds_info["date-note"] != null)
            rep_seq.push('<span class="note-date">' +  
                "Modified at " + timeRepr(ds_info["date-note"]) + '</span>');
        rep_seq.push('</p><p class="the-note">' + 
            ds_info["note"].replace('\n', '<br>') + '</p></div>');
    }
    document.getElementById("ds-info").innerHTML = rep_seq.join('\n');
}

function reprRef(ds_name, mode, label) {
    ret = '<span class="ds-ref" onclick="goToPage(\'' + mode + '\', \'' + 
        ds_name + '\')">' + ((label)? label: ds_name) + '</span>';
    return ret;
}

function reprRefSubDir(ds_name) {
    ret = '<span class="ds-ref" onclick="goToPage(\'SUBDIR\', \'' + 
        ds_name + '\')" title="To sub-directory dataset page">&#x25b7;</span>'
    return ret;
}


function onModalOff() {
}

function arrangeControls() {
    document.getElementById("dir-main").style.height = window.innerHeight - 60;
}
