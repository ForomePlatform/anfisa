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

var sDSName = null;
var sDSKind = null;
var sCommonTitle = null;
var sWsPubURL = null;

var sCohortList = null;
var sCohortViewModes = null;
var sActSamplesMode = false;

var sSamplesCtrl = null;
var sSubViewCurAspect = null;

var sViewAllTranscripts = [true];
/*************************************/
/* Utilities                         */
/*************************************/
function ajaxCall(rq_name, args, func_eval, error_msg, multipart_mode) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var info = JSON.parse(this.responseText);
                func_eval(info);
            } else {
                if (error_msg)
                    alert(error_msg);
            }
        }
    };
    xhttp.open("POST", rq_name, true);
    if (multipart_mode)
        xhttp.setRequestHeader("Accept", "multipart/form-data");
    else
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(args); 
}

/*************************************/
function checkIdentifier(filter_name) {
    return /^\S+$/u.test(filter_name) && 
        (filter_name[0].toLowerCase() != filter_name[0].toUpperCase());
}

/*************************************/
function isStrInt(x) {
    xx = parseInt(x);
    return !isNaN(xx) && xx.toString() == x;
}

function isStrFloat(x) {
    if (isStrInt(x)) 
        return true;
    xx = parseFloat(x);
    return !isNaN(xx) && xx.toString().indexOf('.') != -1;
}

/*************************************/
function toNumeric(tp, x) {
    if (tp == "int") {
        if (!isStrInt(x)) return null;
        return parseInt(x)
    }
    if (!isStrFloat(x)) return null;
    return parseFloat(x);
}

/*************************************/
function timeRepr(time_label) {
    var dt = new Date(time_label);
    return dt.toLocaleString("en-US").replace(/GMT.*/i, "");
}

/*************************************/
function sameData(obj1, obj2) {
    return JSON.stringify(obj1) == JSON.stringify(obj2);
}
/*************************************/
var symToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function _replaceCtrlSym(tag) {
    return symToReplace[tag] || tag;
}

function escapeText(str) {
    return str.replace(/[&<>]/g, _replaceCtrlSym);
}

/*************************************/
function normFloatLongTail(val, to_up) {
    var ret = val.toString();
    var vv = ret.split('.');
    if (vv.length < 2 || vv[1].length < 6)
        return ret
    if (to_up)
        return (val + .000005).toFixed(5);
    return val.toFixed(5);
}

/*************************************/
function softScroll(nd, upper_level) {
    if (nd == null) 
        return;
    var rect = nd.getBoundingClientRect();
    var parent_nd = nd.parentNode;
    if (upper_level)
        for (var j=0; j<upper_level; j++)
            parent_nd = parent_nd.parentNode;
    var rect_parent = parent_nd.getBoundingClientRect();
    if (rect.top - 10 < rect_parent.top ||
            rect.top + rect.height + 10 >  rect_parent.top + rect_parent.height) {
        nd.scrollIntoView(
            {behavior: 'auto', block: 'start'}); // inline: 'center'
    }
}

/*************************************/
function pushKey(the_list, the_key) {
    if (the_list.indexOf(the_key) < 0) {
        the_list.push(the_key);
    }
    return the_list;
}

function popKey(the_list, the_key) {
    while (true) {
        rm_idx = the_list.indexOf(the_key);
        if (rm_idx < 0)
            break;
        the_list.splice(rm_idx, 1);
    }
    return the_list;
}

function pushKeyToStr(the_str, the_key) {
    return pushKey(the_str.split(' '), the_key).join(' ');
}

function popKeyFromStr(the_str, the_key) {
    return popKey(the_str.split(' '), the_key).join(' ');
}

/*************************************/
function setupDSInfo(info) {
    if (info["doc"] === undefined) {
        document.getElementById("menu-doc").disabled = true;
    }
    if (info["cohorts"] && info["cohorts"].length > 0) {
        sCohortList = info["cohorts"];
        sCohortViewModes = [];
        for (idx = 0; idx < sCohortList.length; idx++) {
            sCohortViewModes[sCohortList[idx]] = true;
        }
    }
    sUnitClassesH.setup(info["unit-classes"]);
}

/*************************************/
function goHome() {
    relaxView();
    window.open('dir', sCommonTitle + ':DIR');
}

function goToPage(page_mode, ds_name) {
    relaxView();
    if (!ds_name)
        ds_name = sDSName;
    if (!page_mode)
        page_mode = sDSKind.toUpperCase();
    if (page_mode == "XL") {
        window.open("xl_flt?ds=" + ds_name, sCommonTitle + ":" + ds_name);
        return;
    }
    if (page_mode == "WS") {
        window.open("ws?ds=" + ds_name, sCommonTitle + ":" + ds_name);
        return;
    }
    if (page_mode == "DTREE") {
        window.open("dtree?ds=" + ds_name, sCommonTitle + ":" + ds_name + ":DTREE");
        return;
    }
    if (page_mode == "DOC") {
        window.open("doc_nav?ds=" + ds_name, sCommonTitle + ":" + ds_name + ':DOC');        
        return;
    }
    if (page_mode == "SUBDIR") {
        window.open("subdir?ds=" + ds_name, sCommonTitle + ":" + ds_name + ':SUBDIR');        
        return;
    }
    console.log("BAD PAGE MODE: " +  page_mode);
}

/*************************************/
/* Notes                             */
/*************************************/
function openNote() {
    relaxView();
    loadNote();
    sViewH.modalOn(document.getElementById("note-back"));
}

function saveNote() {
    relaxView();
    loadNote(document.getElementById("note-content").value);
    sViewH.modalOff();
}

function loadNote(content) {
    args = "ds=" + sDSName;
    if (content) 
        args += "&note=" + encodeURIComponent(content);        
    ajaxCall("dsinfo", args, function(info) {
        document.getElementById("note-ds-name").innerHTML = info["name"];
        document.getElementById("note-content").value = info["note"];
        document.getElementById("note-time").innerHTML = 
            (info["date-note"] == null)? "" : "Modified at " + timeRepr(info["date-note"]);
    });
}

/*************************************/
/* Top control                       */
/*************************************/
var sViewH = {
    mPopupMode: null,
    mPopupCtrls: [],
    mModalCtrls: [],
    mNotifyCtrls: [],
    mBlock: false,
    
    addNotifier: function(ctrl) {
        this.mNotifyCtrls.push(ctrl);
    },
    
    popupOn: function(ctrl) {
        if (this.mPopupCtrls.indexOf(ctrl) < 0)
            this.mPopupCtrls.push(ctrl);
        this.popupOff();
        if (ctrl.style.display != "block") {
            ctrl.style.display = "block";
            this.mPopupMode = true;
        }
    },
    
    popupOff: function() {
        this.mPopupMode = false;
        for (idx = 0; idx < this.mPopupCtrls.length; idx++) {
            this.mPopupCtrls[idx].style.display = "none";
        }
        arrangeControls();
    },
    
    modalOn: function(ctrl, disp_mode) {
        this.mBlock = false;
        if (this.mModalCtrls.indexOf(ctrl) < 0)
            this.mModalCtrls.push(ctrl);
        this.modalOff(true);
        ctrl.style.display = (disp_mode)? disp_mode: "block";
    },
    
    modalOff: function(no_notify) {
        if (this.mBlock)
            return;
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            this.mModalCtrls[idx].style.display = "none";
        }
        arrangeControls();
        if (! no_notify) {
            for (idx = 0; idx < this.mNotifyCtrls.length; idx++) {
                this.mNotifyCtrls[idx].onModalOff();
            }
        }
    },
    
    blockModal: function(mode) {
        this.mBlock = mode;
        document.body.className = (mode)? "wait":"";
    },
    
    onclick: function(event_ms) {
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            if (event_ms.target == this.mModalCtrls[idx]) 
                this.modalOff();
        }
        if (this.mPopupMode && !event_ms.target.matches('.popup')) {
            this.popupOff();
        }
    }
};

function relaxView() {
    sViewH.modalOff();
    sViewH.popupOff();
}

/*************************************/
function setupDSControls() {
    window.onclick = function(event_ms) {sViewH.onclick(event_ms);}
    sOpNumH.init();
    sOpEnumH.init();
    sCreateWsH.init();
    sSubVRecH.init();
    sUnitClassesH.init();
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
}

