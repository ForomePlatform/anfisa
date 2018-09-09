var sCurFilterSeq = [];
var sFilterHistory = [];
var sFilterRedoStack = [];
var sBaseFilterName = "_current_";

var sStatList = null;
var sStatUnitIdxs = null;
var sCurStatUnit = null;
var sCurCritNo = null;

var sOpMode = null;
var sOpNumericInfo = null;
var sOpEnumList = null;
var sOpEnumModeInfo = null;
var sOpCriterium = null;
var sOpError = null;
var sOpAddIdx = null;
var sOpUpdateIdx = null;

var sDivStatList        = null;
var sDivCurCritNumeric  = null;
var sDivCurCritEnum     = null;
var sDivCurCritText     = null;
var sDivCritList        = null;
var sDivOpEnumList      = null;

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
    sDivOpEnumList      = document.getElementById("op-enum-list");
    
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

    sSpanCurCritModOnly     = document.getElementById("crit-mode-only-span");
    sSpanCurCritModAnd      = document.getElementById("crit-mode-and-span");
    sSpanCurCritModNot      = document.getElementById("crit-mode-not-span");
    
    sInputCurCritMin        = document.getElementById("crit-min-inp");
    sInputCurCritMax        = document.getElementById("crit-max-inp");
    sCheckCurCritUndef      = document.getElementById("crit-undef-check");

    sCheckCurCritModOnly    = document.getElementById("crit-mode-only");
    sCheckCurCritModAnd     = document.getElementById("crit-mode-and");
    sCheckCurCritModNot     = document.getElementById("crit-mode-not");
    initCriteria();
    loadStat();
}

function loadStat(add_instr){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupStatList(info);
        }
    };
    xhttp.open("POST", "stat", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    args = "ws=" + parent.window.sWorkspaceName + 
        "&m=" + encodeURIComponent(parent.window.sAppModes) + 
        "&filter=" + encodeURIComponent(sBaseFilterName);
    if (sBaseFilterName == "_current_") 
        args += "&criteria=" + encodeURIComponent(JSON.stringify(sCurFilterSeq)); 
    if (add_instr)
        args += "&instr=" + encodeURIComponent(add_instr);
    xhttp.send(args); 
}

/*************************************/
function setupStatList(info) {
    sStatList = info["stat-list"];
    sBaseFilterName = info["filter"];
    sStatUnitIdxs = {}
    if (sCurFilterSeq == null) 
        sCurFilterSeq = info["criteria"];
    _checkNamedFilters(info["all-filters"]);
    var list_stat_rep = [];
    for (idx = 0; idx < sStatList.length; idx++) {
        unit_stat = sStatList[idx];
        unit_type = unit_stat[0];
        unit_name = unit_stat[1];
        sStatUnitIdxs[unit_name] = idx;
        list_stat_rep.push('<div id="stat--' + unit_name + '" class="stat-unit" ' +
          'onclick="selectStat(\'' + unit_name + '\');">');
        list_stat_rep.push('<span class="stat-unit-name">' + unit_name + '</span>');
        if (unit_name == "hot") {
            list_stat_rep.push('<span id="run-hot-eval" title="Hot evaluations" ' +
                ' onclick="hotEvalModOn();">&#9874;</span>')
        }
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
                    list_stat_rep.push('<span class="stat-ok">' + val_min + 
                        ' =< ...<= ' + val_max + ' </span>');
                }
                list_stat_rep.push(': <span class="stat-count">' + count + 
                    ' records</span>');
                if (cnt_undef > 0) 
                    list_stat_rep.push('<span class="stat-undef-count">+' + 
                        cnt_undef + ' undefined</span>');
            }
        } else {
            var_list = unit_stat[2];
            list_stat_rep.push('<ul>');
            for (j = 0; j < Math.min(4, var_list.length); j++) {
                var_name = var_list[j][0];
                var_count = var_list[j][1];
                list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                    '<span class="stat-count">' +
                    var_count + ' records</span></li>');
            }
            list_stat_rep.push('</ul>');
            if (var_list.length > 4) {
                list_stat_rep.push('<p><span class="stat-comment">...and ' + (var_list.length - 4) + ' variants more...</span></p>');
            }
        }
        list_stat_rep.push('</div>')
    }
    sDivStatList.innerHTML = list_stat_rep.join('\n');
    
    list_crit_rep = [];
    for (idx = 0; idx < sCurFilterSeq.length; idx++) {
        crit = sCurFilterSeq[idx];
        list_crit_rep.push('<div id="crit--' + idx + '" class="crit-descr" ' +
          'onclick="selectCrit(\'' + idx + '\');">');
        list_crit_rep.push('&bull;&emsp;' + getCritDescripton(crit, false));
        list_crit_rep.push('</div>')
    }
    sDivCritList.innerHTML = list_crit_rep.join('\n');
    
    sCurStatUnit = null;
    sCurCritNo = null;
    if (sCurFilterSeq.length > 0) 
        selectCrit(sCurFilterSeq.length - 1);
    else
        selectStat(sStatList[0][1]);
    updateFilterOpMode();
}

function _checkNamedFilters(all_filters) {
    setupNamedFilters(all_filters);
    for (idx = 0; idx < sFilterHistory.length; idx++) {
        hinfo = sFilterHistory[idx];
        if (hinfo[0] != "_current_" && all_filters.indexOf(hinfo[0]) < 0)
            hinfo[0] = "_current_";
    }
    for (idx = 0; idx < sFilterRedoStack.length; idx++) {
        hinfo = sFilterRedoStack[idx];
        if (hinfo[0] != "_current_" && all_filters.indexOf(hinfo[0]) < 0)
            hinfo[0] = "_current_";
    }
    if (sBaseFilterName != "_current_" && 
            all_filters.indexOf(sBaseFilterName) < 0)
        sBaseFilterName = "_current_";
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
    if (sCurCritNo == null || sCurFilterSeq[sCurCritNo][1] != sCurStatUnit)
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
        selectStat(sCurFilterSeq[crit_no][1]);
    }
}

/*************************************/
function setupStatUnit() {
    sOpMode = null;
    sOpEnumModeInfo = null;
    sOpNumericInfo = null;
    sOpCriterium = null;
    sOpEnumList = null;
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
                (cnt_undef > 0)? true : null, unit_type];
        
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
        if (unit_type != "status") {
            sOpEnumModeInfo = [false, false, false];
        }
        sOpEnumList = unit_stat[2];
        list_val_rep = [];
        for (j = 0; j < sOpEnumList.length; j++) {
            var_name = sOpEnumList[j][0];
            var_count = sOpEnumList[j][1];
            if (var_count == 0)
                continue;
            list_val_rep.push('<div class="enum-val">' +
                '<input id="elcheck--' + j + '" type="checkbox" ' + 
                'onchange="checkCurCrit(\'enum-el\');"/>&emsp;' + var_name + 
                '<span class="enum-cnt">(' + var_count + ')</span></div>');
        }
        sDivOpEnumList.innerHTML = list_val_rep.join('\n');
        sCheckCurCritModAnd.checked = false;
        sCheckCurCritModOnly.checked = false;
        sCheckCurCritModNot.checked = false;
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

    sSpanCurCritModAnd.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[0] != null)? "visible":"hidden";
    sSpanCurCritModOnly.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[1] != null)? "visible":"hidden";
    sSpanCurCritModNot.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[2] != null)? "visible":"hidden";
        
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
            if (sOpNumericInfo[0] == 0) {
                checkNumericOpMin();
            } else if (sOpNumericInfo[0] == 1) {
                checkNumericOpMax();
            }
            break;
        case "mode-and":
            if (!checkEnumOpMode(0))
                return;
            break;
        case "mode-only":
            if (!checkEnumOpMode(1))
                return;
            break;
        case "mode-not":
            if (!checkEnumOpMode(2))
                return;
            break;
        case "enum-el":
            break;
        default:
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
                if (sOpNumericInfo[2] != sOpNumericInfo[4]) {
                    sOpCriterium = ["numeric", sCurStatUnit, 0, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                } else {
                    if (sOpNumericInfo[1] > 0 && !sOpNumericInfo[5]) {
                        sOpCriterium = ["numeric", sCurStatUnit, -1, null, false];
                    }
                }
                break;
            case 1:
                if (sOpNumericInfo[3] != sOpNumericInfo[4]) {
                    sOpCriterium = ["numeric", sCurStatUnit, 1, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                } else {
                    if (sOpNumericInfo[1] > 0 && !sOpNumericInfo[5]) {
                        sOpCriterium = ["numeric", sCurStatUnit, -1, null, false];
                    }
                }
                break;
        }
    }
    if (sOpEnumList != null) {
        sOpAddIdx = null;
        sOpUpdateIdx = null;
        enum_mode = "";
        if (sOpEnumModeInfo != null) {
            for (mode_idx = 0; mode_idx < 3; mode_idx++) {
                if (sOpEnumModeInfo[mode_idx]) {
                    enum_mode = ["AND", "ONLY", "NOT"][mode_idx];
                    break;
                }
            }
        }
        sOpUpdateIdx = findCrit(sCurStatUnit, enum_mode);
        if (sOpUpdateIdx == null) 
            sOpUpdateIdx = findCrit(sCurStatUnit);
        selectCrit(sOpUpdateIdx);
        
        sel_names = [];
        for (j=0; j < sOpEnumList.length; j++) {
            if (document.getElementById("elcheck--" + j).checked)
                sel_names.push(sOpEnumList[j][0]);
        }
        if (sel_names.length > 0) {
            sOpAddIdx = (sOpUpdateIdx == null)? sCurFilterSeq.length:sOpUpdateIdx + 1;
            sOpCriterium = ["enum", sCurStatUnit, enum_mode, sel_names];
        } else {
            sOpUpdateIdx = null;
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
                sOpAddIdx = (idx == null)? sCurFilterSeq.length:idx + 1;
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
                sOpAddIdx = (idx == null)? sCurFilterSeq.length:idx + 1;
            }
        } else {
            selectCrit(sOpUpdateIdx);
        }
    }
}

function checkEnumOpMode(mode_idx) {
    if (sOpEnumModeInfo == null || sOpEnumModeInfo[mode_idx] == null)
        return false;
    if (sOpEnumModeInfo[0] != null) {
        sOpEnumModeInfo[0] = (mode_idx == 0);
        sCheckCurCritModAnd.checked = (mode_idx == 0);
    }
    if (sOpEnumModeInfo[1] != null) {
        sOpEnumModeInfo[1] = (mode_idx == 1);
        sCheckCurCritModOnly.checked = (mode_idx == 1);
    }
    if (sOpEnumModeInfo[2] != null) {
        sOpEnumModeInfo[2] = (mode_idx == 2);
        sCheckCurCritModNot.checked = (mode_idx == 2);
    }
    return true;
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

