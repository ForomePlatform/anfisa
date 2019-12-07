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
var sCohortViewCheck = null;

var sSamplesCtrl = null;
var sSubViewCurAspect = null;

/*************************************/
/* Utilities                         */
/*************************************/
function ajaxCall(rq_name, args, func_eval) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            func_eval(info);
        }
    };
    xhttp.open("POST", rq_name, true);
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
            {behavior: 'auto', block: 'start', inline: 'center'});
    }
}

/*************************************/
function setupDSInfo(info) {
    if (info["doc"] == undefined) {
        menu_el = document.getElementById("menu-doc");
        menu_el.className = "drop ctrl-menu-disabled";
        menu_el.onclick = "";
    }
    if (info["cohorts"]) {
        sCohortList = info["cohorts"];
        sCohortViewCheck = [];
        for (idx = 0; idx < sCohortList.length; idx++) {
            sCohortViewCheck[sCohortList[idx]] = true;
        }
    }
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
    if (page_mode == "TREE") {
        window.open("dtree?ds=" + ds_name, sCommonTitle + ":" + ds_name + ":TREE");
        return;
    }
    if (page_mode == "DOC") {
        window.open("doc_nav?ds=" + ds_name, sCommonTitle + ":" + ds_name + ':DOC');        
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
    mShowToDrop: null,
    mDropCtrls: [],
    mModalCtrls: [],
    mBlock: false,
    
    addToDrop: function(ctrl) {
        this.mDropCtrls.push(ctrl);
    },

    dropOn: function(ctrl) {
        if (this.mDropCtrls.indexOf(ctrl) < 0)
            this.mDropCtrls.push(ctrl);
        if (ctrl.style.display == "block") {
            this.dropOff();
        } else {
            this.dropOff();
            ctrl.style.display = "block";
            this.mShowToDrop = true;
        }
    },
    
    dropOff: function() {
        this.mShowToDrop = false;
        for (idx = 0; idx < this.mDropCtrls.length; idx++) {
            this.mDropCtrls[idx].style.display = "none";
        }
        arrangeControls();
    },
    
    modalOn: function(ctrl, disp_mode) {
        this.mBlock = false;
        if (this.mModalCtrls.indexOf(ctrl) < 0)
            this.mModalCtrls.push(ctrl);
        this.modalOff();
        ctrl.style.display = (disp_mode)? disp_mode: "block";
    },
    
    modalOff: function() {
        if (this.mBlock)
            return;
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            this.mModalCtrls[idx].style.display = "none";
        }
        onModalOff();
        arrangeControls();
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
        if (this.mShowToDrop && !event_ms.target.matches('.drop')) {
            this.dropOff();
        }
    }
};

function relaxView() {
    sViewH.modalOff();
    sViewH.dropOff();
}

/*************************************/
function openControlMenu() {
    sViewH.dropOn(document.getElementById("control-menu"));
}

/*************************************/
function setupDSControls() {
    window.onclick = function(event_ms) {sViewH.onclick(event_ms);}
    sViewH.addToDrop(document.getElementById("control-menu"));
    sOpNumH.init();
    sOpEnumH.init();
    if (sDSKind == "xl")
        sCreateWsH.init();
    sSubVRecH.init();
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
}

