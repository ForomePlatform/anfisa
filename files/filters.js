/*
# Unit functions
#  - setup(): setup div inner html
#  - update(data): setup values of contols 
#  - check(): criterium is good/bad/none 
#  
#=====================
# IntValueUnit
# FloatValueUnit
#   * min / max
#   * count, count_undef
#   Criterium: cr_min, cr_max, keep_undef
# StatusUnit
# PresenceUnit
# MultiStatusUnit
#   Static: list of values
#   * [counts]
#   Criterium: (set of no), OR/AND
#=====================*/

var sCurFilter = [];
var sFilterHistory = [];
var sFilterRedoStack = [];
var sStatList = null;
var sStatUnitIdxs = null;
var sCurStatUnit = null;
var sCurCritNo = null;

var sOpMode = null;
var sOpNumericInfo = null;
var sOpEnumMode = null;
var sOpCriterium = null;
var sOpError = null;
var sOpAddIdx = null;
var sOpUpdateIdx = null;

var sDivStatList        = null;
var sDivCurCritNumeric  = null;
var sDivCurCritEnum     = null;
var sDivCurCritText     = null;
var sDivCritList        = null;

var sBtnAddCrit    = null;
var sBtnUpdateCrit = null; 
var sBtnDeleteCrit = null; 
var sBtnUndoCrit   = null; 
var sBtnRedoCrit   = null; 

var sSpanCurCritTitle       = null;
var sSpanCurCritMin         = null;
var sSpanCurCritMax         = null;
var sSpanCurCritSign        = null;
var sSpanCurCritUndefCount  = null;

var sSpanCurCritModOnly     = null;
var sSpanCurCritModAnd      = null;
var sSpanCurCritModNot      = null;

var sInputCurCritMin        = null;
var sInputCurCritMax        = null;
var sCheckCurCritUndef      = null;

var sCheckCurCritModOnly    = null;
var sCheckCurCritModAnd     = null;
var sCheckCurCritModNot     = null;

/*************************************/
function initFilters() {
    sDivStatList        = document.getElementById("stat-list");
    sDivCurCritNumeric  = document.getElementById("cur-crit-numeric");
    sDivCurCritEnum     = document.getElementById("cur-crit-enum");
    sDivCurCritText     = document.getElementById("filter-cur-crit-text");
    sDivCritList        = document.getElementById("crit-list");
    
    sBtnAddCrit    = document.getElementById("filter-add-crit"); 
    sBtnUpdateCrit = document.getElementById("filter-update-crit"); 
    sBtnDeleteCrit = document.getElementById("filter-delete-crit"); 
    sBtnUndoCrit   = document.getElementById("filter-undo-crit"); 
    sBtnRedoCrit   = document.getElementById("filter-redo-crit"); 
    
    sSpanCurCritTitle       = document.getElementById("crit-title");
    sSpanCurCritText        = document.getElementById("crit-text");
    sSpanCurCritError       = document.getElementById("crit-error");
    sSpanCurCritMin         = document.getElementById("crit-min");
    sSpanCurCritMax         = document.getElementById("crit-max");
    sSpanCurCritSign        = document.getElementById("crit-sign");
    sSpanCurCritUndefCount  = document.getElementById("crit-undef-count");

    sSpanCurCritModOnly     = document.getElementById("crit-mod-only-span");
    sSpanCurCritModAnd      = document.getElementById("crit-mod-and-span");
    sSpanCurCritModNot      = document.getElementById("crit-mod-not-span");
    
    sInputCurCritMin        = document.getElementById("crit-min-inp");
    sInputCurCritMax        = document.getElementById("crit-max-inp");
    sCheckCurCritUndef      = document.getElementById("crit-undef-check");

    sCheckCurCritModOnly    = document.getElementById("crit-mod-only");
    sCheckCurCritModAnd     = document.getElementById("crit-mod-and");
    sCheckCurCritModNot     = document.getElementById("crit-mod-not");
}

/*************************************/
function setupStatList(stat_list) {
    sStatList = stat_list;
    sStatUnitIdxs = {}
    var list_stat_rep = [];
    for (idx = 0; idx < stat_list.length; idx++) {
        unit_stat = stat_list[idx];
        unit_type = unit_stat[0];
        unit_name = unit_stat[1];
        sStatUnitIdxs[unit_name] = idx;
        list_stat_rep.push('<div id="stat--' + unit_name + '" class="stat-unit" ' +
          'onclick="selectStat(\'' + unit_name + '\');">');
        list_stat_rep.push('<span class="stat-unit-name">' + unit_name + '</span>');
        if (unit_type == "int" || unit_type == "float") {
            list_stat_rep.push('<br/>');
            val_min   = unit_stat[2];
            val_max   = unit_stat[3];
            count     = unit_stat[4];
            cnt_undef = unit_stat[5];
            if (count == 0) {
                list_stat_rep.push('<span class="stat-bad">No data</span>');
            } else {
                if (val_min == val_max) {
                    list_stat_rep.push('<span class="stat-ok">' + val_min + '</span>');
                } else {
                    list_stat_rep.push('<span class="stat-ok">' + val_min + ' =< ...<= ' +
                        val_max + ' </span>');
                }
                list_stat_rep.push('<span class="stat-count">' + count + ' records</span>');
                if (cnt_undef > 0) 
                    list_stat_rep.push('<span class="stat-undef-count">+' + cnt_undef + 
                        ' undefined</span>');
            }
        } else {
            var_list = unit_stat[2];
            list_stat_rep.push('<ul>');
            for (j = 0; j < Math.min(4, var_list.length); j++) {
                var_name = var_list[j][0];
                var_count = var_list[j][1];
                list_stat_rep.push('<li><b>' + var_name + '</b>: <span class="count">' +
                    var_count + ' records</span></li>');
            }
            list_stat_rep.push('</ul>');
            if (var_list.length > 4) {
                list_stat_rep.push('<p>...and ' + (var_list.length - 4) + ' more...</p>');
            }
        }
        list_stat_rep.push('</div>')
    }
    sDivStatList.innerHTML = list_stat_rep.join('\n');
    
    list_crit_rep = [];
    for (idx = 0; idx < sCurFilter.length; idx++) {
        crit = sCurFilter[idx];
        list_crit_rep.push('<div id="crit--' + idx + '" class="crit-descr" ' +
          'onclick="selectCrit(\'' + idx + '\');">');
        list_crit_rep.push('&bull;&emsp;' + getCritDescripton(crit, false));
        list_crit_rep.push('</div>')
    }
    sDivCritList.innerHTML = list_crit_rep.join('\n');
    
    sCurStatUnit = null;
    sCurCritNo = null;
    if (sCurFilter.length > 0) 
        selectCrit(sCurFilter.length - 1);
    else
        selectStat(stat_list[0][1]);
}

/*************************************/
function selectStat(stat_unit){
    if (sCurStatUnit == stat_unit) 
        return;
    var new_unit_el = document.getElementById("stat--" + stat_unit);
    if (new_unit_el == null) 
        return;
    if (sCurStatUnit != null) {
        var prev_el = document.getElementById("stat--" + sCurStatUnit);
        prev_el.className = prev_el.className.replace(" cur", "");
    }
    sCurStatUnit = stat_unit;
    new_unit_el.className = new_unit_el.className + " cur";
    if (sCurCritNo == null || sCurFilter[sCurCritNo][1] != sCurStatUnit)
        selectCrit(findCrit(sCurStatUnit));
    setupStatUnit();
}

/*************************************/
function selectCrit(crit_no){
    if (sCurCritNo == crit_no) 
        return;
    if (crit_no != null) {
        new_crit_el = document.getElementById("crit--" + crit_no);
        if (new_crit_el == null) 
            return;
    } else {
        new_crit_el = null;
    }
    if (sCurCritNo != null) {
        var prev_el = document.getElementById("crit--" + sCurCritNo);
        prev_el.className = prev_el.className.replace(" cur", "");
    }
    sCurCritNo = crit_no;
    if (new_crit_el != null) {
        new_crit_el.className = new_crit_el.className + " cur";
        selectStat(sCurFilter[crit_no][1]);
    }
}

/*************************************/
function findCrit(unit_name, mode) {
    for (idx = 0; idx < sCurFilter.length; idx++) {
        if (sCurFilter[idx][1] == unit_name) {
            if (mode == undefined || sCurFilter[idx][2] == mode)
                return idx;
        }
    }
    return null;
}

/*************************************/
function setupStatUnit() {
    sOpMode = null;
    sOpNumericInfo = null;
    sOpCriterium = null;
    sOpError = null;
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    updateOpCritText();
    if (sCurStatUnit == null) {
        sSpanCurCritTitle.innerHTML = "";
        updateCurCritCtrl();
        return;
    } 
    sSpanCurCritTitle.innerHTML = sCurStatUnit;
    unit_stat = sStatList[sStatUnitIdxs[sCurStatUnit]];
    unit_type = unit_stat[0];
    if (unit_type == "int" || unit_type == "float") {
        sOpMode = "numeric";
        val_min   = unit_stat[2];
        val_max   = unit_stat[3];
        count     = unit_stat[4];
        cnt_undef = unit_stat[5];
        
        if (val_min == val_max) 
            sOpNumericInfo = [-1, cnt_undef];
        else
            sOpNumericInfo = [0, cnt_undef, val_min, val_max, val_min, 
                cnt_undef > 0, unit_type];
        
        sSpanCurCritMin.innerHTML = val_min;
        sSpanCurCritMax.innerHTML = val_max;
        sSpanCurCritSign.innerHTML = (val_min == val_max)? "=":"<";
        sInputCurCritMin.value = val_min;
        sInputCurCritMax.value = val_max;
        
        sCheckCurCritUndef.checked = (cnt_undef > 0)
        sSpanCurCritUndefCount.innerHTML = (cnt_undef > 0)?
            ("undefined:" + cnt_undef) : "";        
    } else {
        sOpMode = "enum";
    }
    updateCurCritCtrl();
}

function updateCurCritCtrl() {
    sDivCurCritNumeric.style.display = (sOpMode == "numeric")? "block":"none";
    sDivCurCritEnum.style.display    = (sOpMode == "enum")? "block":"none";

    sInputCurCritMin.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[0] == 0)? "visible":"hidden";
    sInputCurCritMax.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[0] == 1)? "visible":"hidden";
    sCheckCurCritUndef.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[1] > 0)? "visible":"hidden";
    sSpanCurCritUndefCount.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[1] > 0)? "visible":"hidden";
        
    sBtnAddCrit.disabled  = (sOpAddIdx == null);
    sBtnUpdateCrit.disabled  = (sOpUpdateIdx == null); 
    sBtnDeleteCrit.disabled = (sCurCritNo == null);
    sBtnUndoCrit.disabled = (sFilterHistory.length == 0);
    sBtnRedoCrit.disabled = (sFilterRedoStack.length == 0);
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

function toNumeric(tp, x) {
    if (tp == "int") {
        if (!isStrInt(x)) return null;
        return parseInt(x)
    }
    if (!isStrFloat(x)) return null;
    return parseFloat(x);
}

/*************************************/
function checkCurCrit(option) {
    switch(option) {
        case "min":
            if (sOpNumericInfo == null || sOpNumericInfo[0] != 0)
                return;
            checkNumericOpMin();
            break;
        case "max":
            if (sOpNumericInfo == null || sOpNumericInfo[0] != 1)
                return;
            checkNumericOpMax();
            break;
        case "sign":
            if (sOpNumericInfo == null || sOpNumericInfo[0] < 0)
                return;
            if (sOpNumericInfo[0] == 0) {
                sOpNumericInfo[0] = 1;
                checkNumericOpMax();
            } else {
                sOpNumericInfo[0] = 0;
                checkNumericOpMin();
            }
            break;
        case "undef": 
            if (sOpNumericInfo == null || sOpNumericInfo[1] == 0)
                return;
            sOpNumericInfo[5] = !sOpNumericInfo[5];
            sCheckCurCritUndef.checked = sOpNumericInfo[5];
            break;
        case "mode-and":
        case "mode-only":
        case "mode-not":
            return;
    }
    if (sOpNumericInfo != null) {
        sOpCriterium = null;
        switch (sOpNumericInfo[0]) {
            case -1:
                if (sOpNumericInfo[1] > 0 && sOpNumericInfo[5]) {
                    sOpCriterium = ["numeric", sCurStatUnit, -1, null, true];
                }
                break;
            case 0:
                if ((sOpNumericInfo[2] != sOpNumericInfo[4] || sOpNumericInfo[5])) {
                    sOpCriterium = ["numeric", sCurStatUnit, 0, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                }
                break;
            case 1:
                if ((sOpNumericInfo[3] != sOpNumericInfo[4] || sOpNumericInfo[5])) {
                    sOpCriterium = ["numeric", sCurStatUnit, 1, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                }
                break;
        }
    }
    updateOpCritText();
    updateCurCritCtrl();
}

function checkNumericOpMin() {
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    sOpError = null;
    val = toNumeric(sOpNumericInfo[6], sInputCurCritMin.value);
    if (val == null) {
        sOpError = "Bad numeric value";
    } else {
        sOpNumericInfo[4] = val;
        sOpUpdateIdx = findCrit(sCurStatUnit, 0);
        if (sOpUpdateIdx == null) {
            if (val < sOpNumericInfo[2]) {
                sOpError = "Lower bound is above minimal value";
            } else {
                idx = findCrit(sCurStatUnit);
                sOpAddIdx = (idx == null)? sCurFilter.length:idx + 1;
            }
        } else {
            selectCrit(sOpUpdateIdx);
        }
    }
}

function checkNumericOpMax() {
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    sOpError = null;
    val = toNumeric(sOpNumericInfo[6], sInputCurCritMax.value);
    if (val == null) {
        sOpError = "Bad numeric value";
    } else {
        sOpNumericInfo[4] = val;
        sOpUpdateIdx = findCrit(sCurStatUnit, 1);
        if (sOpUpdateIdx == null) {
            if (val < sOpNumericInfo[2]) {
                sOpError = "Upper bound is below maximum value";
            } else {
                idx = findCrit(sCurStatUnit);
                sOpAddIdx = (idx == null)? sCurFilter.length:idx + 1;
            }
        } else {
            selectCrit(sOpUpdateIdx);
        }
    }
}
function getCritDescripton(crit, short_form) {
    if (crit != null && crit[0] == "numeric") {
        rep_crit = [sOpCriterium[1]];
        switch (crit[2]) {
            case 0:
                rep_crit.push("> " + crit[3]);
                break
            case 1:
                rep_crit.push("< " + crit[3]);
                break
        }
        if (crit[4]) 
            rep_crit.push("with undef");
        return rep_crit.join(" ");
    }
    return ""
}

function updateOpCritText() {
    if (sOpAddIdx != null || sOpUpdateIdx != null) 
        sSpanCurCritText.innerHTML = getCritDescripton(sOpCriterium, true);
    else
        sSpanCurCritText.innerHTML = "";
    if (sOpError != null)
        sSpanCurCritError.innerHTML = sOpError;
    else
        sSpanCurCritError.innerHTML = "";
}

/*************************************/
function filterAddCrit() {
    if (sOpCriterium != null && sOpAddIdx != null) {
        sFilterHistory.push(sCurFilter);
        sCurFilter = sCurFilter.slice();
        sCurFilter.splice(sOpAddIdx, 0, sOpCriterium);
        sFilterRedoStack = [];
        filterModOff();
        loadList();
    }
}

function filterUpdateCrit() {
    if (sOpCriterium != null && sOpUpdateIdx != null) {
        sFilterHistory.push(sCurFilter);
        sCurFilter = sCurFilter.slice();
        sCurFilter[sOpUpdateIdx] = sOpCriterium;
        sFilterRedoStack = [];
        filterModOff();
        loadList();
    }
}

function filterDeleteCrit() {
    if (sCurCritNo != null) {
        sFilterHistory.push(sCurFilter);
        sCurFilter = sCurFilter.slice();
        sCurFilter.splice(sCurCritNo, 1);
        sFilterRedoStack = [];
        filterModOff();
        loadList();
    }
}

function filterUndoCrit() {
    if (sFilterHistory.length > 0) {
        sFilterRedoStack.push(sCurFilter);
        sCurFilter = sFilterHistory.pop();
        filterModOff();
        loadList();
    }        
}

function filterRedoCrit() {
    if (sFilterRedoStack.length > 0) {
        sFilterHistory.push(sCurFilter);
        sCurFilter = sFilterRedoStack.pop();
        filterModOff();
        loadList();
    }            
}

/*************************************/
