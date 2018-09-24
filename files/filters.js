var sCurFilterSeq = [];
var sFilterHistory = [];
var sFilterRedoStack = [];
var sBaseFilterName = "_current_";

var sStatList = null;
var sStatUnitIdxs = null;
var sCurStatUnit = null;
var sCurCondNo = null;

var sOpMode = null;
var sOpNumericInfo = null;
var sOpEnumList = null;
var sOpEnumModeInfo = null;
var sOpCondition = null;
var sOpError = null;
var sOpAddIdx = null;
var sOpUpdateIdx = null;

var sDivStatList        = null;
var sDivCurCondNumeric  = null;
var sDivCurCondEnum     = null;
var sDivCurCondText     = null;
var sDivCondList        = null;
var sDivOpEnumList      = null;

var sBtnAddCond    = null;
var sBtnUpdateCond = null; 
var sBtnDeleteCond = null; 
var sBtnUndoCond   = null; 
var sBtnRedoCond   = null; 

var sSpanCurCondTitle       = null;
var sSpanCurCondMin         = null;
var sSpanCurCondMax         = null;
var sSpanCurCondSign        = null;
var sSpanCurCondUndefCount  = null;

var sSpanCurCondModOnly     = null;
var sSpanCurCondModAnd      = null;
var sSpanCurCondModNot      = null;

var sInputCurCondMin        = null;
var sInputCurCondMax        = null;
var sCheckCurCondUndef      = null;

var sCheckCurCondModOnly    = null;
var sCheckCurCondModAnd     = null;
var sCheckCurCondModNot     = null;

/*************************************/
function initFilters() {
    sDivStatList        = document.getElementById("stat-list");
    sDivCurCondNumeric  = document.getElementById("cur-cond-numeric");
    sDivCurCondEnum     = document.getElementById("cur-cond-enum");
    sDivCurCondText     = document.getElementById("filter-cur-cond-text");
    sDivCondList        = document.getElementById("cond-list");
    sDivOpEnumList      = document.getElementById("op-enum-list");
    
    sBtnAddCond    = document.getElementById("filter-add-cond"); 
    sBtnUpdateCond = document.getElementById("filter-update-cond"); 
    sBtnDeleteCond = document.getElementById("filter-delete-cond"); 
    sBtnUndoCond   = document.getElementById("filter-undo-cond"); 
    sBtnRedoCond   = document.getElementById("filter-redo-cond"); 
    
    sSpanCurCondTitle       = document.getElementById("cond-title");
    sSpanCurCondText        = document.getElementById("cond-text");
    sSpanCurCondError       = document.getElementById("cond-error");
    sSpanCurCondMin         = document.getElementById("cond-min");
    sSpanCurCondMax         = document.getElementById("cond-max");
    sSpanCurCondSign        = document.getElementById("cond-sign");
    sSpanCurCondUndefCount  = document.getElementById("cond-undef-count");

    sSpanCurCondModOnly     = document.getElementById("cond-mode-only-span");
    sSpanCurCondModAnd      = document.getElementById("cond-mode-and-span");
    sSpanCurCondModNot      = document.getElementById("cond-mode-not-span");
    
    sInputCurCondMin        = document.getElementById("cond-min-inp");
    sInputCurCondMax        = document.getElementById("cond-max-inp");
    sCheckCurCondUndef      = document.getElementById("cond-undef-check");

    sCheckCurCondModOnly    = document.getElementById("cond-mode-only");
    sCheckCurCondModAnd     = document.getElementById("cond-mode-and");
    sCheckCurCondModNot     = document.getElementById("cond-mode-not");

    document.getElementById("cur-enum-zeros").checked = false;
    setCurEnumZeros(false);

    initConditions();
    loadStat();
}


function formFilterRequestArgs(filter_name, add_instr) {
    args = "ws=" + parent.window.sWorkspaceName + 
        "&m=" + encodeURIComponent(parent.window.sAppModes);
    if (filter_name == "_current_") 
        args += "&conditions=" + encodeURIComponent(JSON.stringify(sCurFilterSeq)); 
    else
        args += "&filter=" + encodeURIComponent(filter_name);
    if (add_instr)
        args += "&instr=" + encodeURIComponent(add_instr);
    return args;
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
    xhttp.send(formFilterRequestArgs(sBaseFilterName, add_instr)); 
}

/*************************************/
function setupStatList(info) {
    sStatList = info["stat-list"];
    sBaseFilterName = info["filter"];
    sStatUnitIdxs = {}
    if (sCurFilterSeq == null) 
        sCurFilterSeq = info["conditions"];
    _checkNamedFilters(info["pre-filters"], info["op-filters"]);
    var list_stat_rep = [];
    var group_title = false;
    for (idx = 0; idx < sStatList.length; idx++) {
        unit_stat = sStatList[idx];
        unit_type = unit_stat[0];
        unit_names = unit_stat[1];
        unit_name = unit_names["name"];
        if (group_title != unit_names["vgroup"] || unit_names["vgroup"] == null) {
            if (group_title != false) {
                list_stat_rep.push('</div>');
            }
            group_title = unit_names["vgroup"];
            list_stat_rep.push('<div class="stat-group">');
            if (group_title != null) {
                list_stat_rep.push('<div class="stat-group-title">' + 
                    group_title + '</div>');
            }
        }
        sStatUnitIdxs[unit_name] = idx;
        list_stat_rep.push('<div id="stat--' + unit_name + '" class="stat-unit" ' +
          'onclick="selectStat(\'' + unit_name + '\');">');
        list_stat_rep.push('<div class="wide"><span class="stat-unit-name">' +
            unit_name + '</span>');
        if (unit_names["title"])
            list_stat_rep.push('<span class="stat-unit-title">' + 
                unit_names["title"] + '</span>');
        list_stat_rep.push('</div>')
        if (unit_name == "Rules") {
            list_stat_rep.push(
                '<span id="flt-run-rules" title="Rules evaluation setup" ' +
                ' onclick="rulesModOn();">&#9874;</span>')
        }
        if (unit_type == "int" || unit_type == "float") {
            val_min   = unit_stat[2];
            val_max   = unit_stat[3];
            count     = unit_stat[4];
            cnt_undef = unit_stat[5];
            if (count == 0) {
                list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
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
            list_count = 0;
            for (j = 0; j < var_list.length; j++) {
                if (var_list[j][1] > 0)
                    list_count++;
            }
            if (list_count > 0) {
                list_stat_rep.push('<ul>');
                view_count = (list_count > 6)? 3: list_count; 
                for (j = 0; j < var_list.length && view_count > 0; j++) {
                    var_name = var_list[j][0];
                    var_count = var_list[j][1];
                    if (var_count == 0)
                        continue;
                    view_count -= 1;
                    list_count --;
                    list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                        '<span class="stat-count">' +
                        var_count + ' records</span></li>');
                }
                list_stat_rep.push('</ul>');
                if (list_count > 0) {
                    list_stat_rep.push('<p><span class="stat-comment">...and ' + 
                        list_count + ' variants more...</span></p>');
                }
            } else {
                list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
            }
        }
        list_stat_rep.push('</div>')
    }
    if (group_title != false) {
        list_stat_rep.push('</div>')
    }
    sDivStatList.innerHTML = list_stat_rep.join('\n');
    
    list_cond_rep = [];
    for (idx = 0; idx < sCurFilterSeq.length; idx++) {
        cond = sCurFilterSeq[idx];
        list_cond_rep.push('<div id="cond--' + idx + '" class="cond-descr" ' +
          'onclick="selectCond(\'' + idx + '\');">');
        list_cond_rep.push('&bull;&emsp;' + getCondDescripton(cond, false));
        list_cond_rep.push('</div>')
    }
    sDivCondList.innerHTML = list_cond_rep.join('\n');
    
    sCurStatUnit = null;
    sCurCondNo = null;
    if (sCurFilterSeq.length > 0) 
        selectCond(sCurFilterSeq.length - 1);
    else
        selectStat(sStatList[0][1]["name"]);
    prepareFilterOperations();
}

function _checkNamedFilters(pre_filters, op_filters) {
    var all_filters = pre_filters.concat(op_filters);
    setupNamedFilters(pre_filters, all_filters);
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
function selectStat(stat_unit, force_it){
    if (sCurStatUnit == stat_unit && !force_it) 
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
    if (sCurCondNo == null || sCurFilterSeq[sCurCondNo][1] != sCurStatUnit)
        selectCond(findCond(sCurStatUnit));
    setupStatUnit();
}

/*************************************/
function selectCond(cond_no){
    if (sCurCondNo == cond_no) 
        return;
    if (cond_no != null) {
        new_cond_el = document.getElementById("cond--" + cond_no);
        if (new_cond_el == null) 
            return;
    } else {
        new_cond_el = null;
    }
    if (sCurCondNo != null) {
        var prev_el = document.getElementById("cond--" + sCurCondNo);
        prev_el.className = prev_el.className.replace(" cur", "");
    }
    sCurCondNo = cond_no;
    if (new_cond_el != null) {
        new_cond_el.className = new_cond_el.className + " cur";
        selectStat(sCurFilterSeq[sCurCondNo][1], true);
    }
}

/*************************************/
function setupStatUnit() {
    sOpMode = null;
    sOpEnumModeInfo = null;
    sOpNumericInfo = null;
    sOpCondition = null;
    sOpEnumList = null;
    sOpError = null;
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    updateOpCondText();
    if (sCurStatUnit == null) {
        sSpanCurCondTitle.innerHTML = "";
        updateCurCondCtrl();
        return;
    } 
    sSpanCurCondTitle.innerHTML = sCurStatUnit;
    unit_stat = sStatList[sStatUnitIdxs[sCurStatUnit]];
    unit_type = unit_stat[0];
    if (unit_type == "int" || unit_type == "float") {
        sOpMode = "numeric";
        val_min   = unit_stat[2];
        val_max   = unit_stat[3];
        count     = unit_stat[4];
        cnt_undef = unit_stat[5];
        
        if (val_min == val_max) 
            sOpNumericInfo = [-1, cnt_undef, val_min, val_max, 
                null, null, unit_type, false];
        else
            sOpNumericInfo = [0, cnt_undef, val_min, val_max, 
                val_min,  (cnt_undef > 0)? true : null, unit_type, false];
        
        sSpanCurCondMin.innerHTML = val_min;
        sSpanCurCondMax.innerHTML = val_max;
        sSpanCurCondSign.innerHTML = (val_min == val_max)? "=":"&le;";
        sInputCurCondMin.value = val_min;
        sInputCurCondMax.value = val_max;
        
        sCheckCurCondUndef.checked = (cnt_undef > 0)
        sSpanCurCondUndefCount.innerHTML = (cnt_undef > 0)?
            ("undefined:" + cnt_undef) : "";        
    } else {
        sOpMode = "enum";
        if (unit_type != "status") {
            sOpEnumModeInfo = [false, false, false];
        }
        sOpEnumList = unit_stat[2];
        list_val_rep = [];
        has_zero = false;
        for (j = 0; j < sOpEnumList.length; j++) {
            var_name = sOpEnumList[j][0];
            var_count = sOpEnumList[j][1];
            has_zero |= (var_count == 0);
            list_val_rep.push('<div class="enum-val' + 
                ((var_count==0)? " zero":"") +'">' +
                '<input id="elcheck--' + j + '" type="checkbox" ' + 
                'onchange="checkCurCond(\'enum-el\');"/>&emsp;' + var_name + 
                '<span class="enum-cnt">(' + var_count + ')</span></div>');
        }
        sDivOpEnumList.innerHTML = list_val_rep.join('\n');
        sCheckCurCondModAnd.checked = false;
        sCheckCurCondModOnly.checked = false;
        sCheckCurCondModNot.checked = false;
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero)? "block":"none";
    }
    if (sCurCondNo != null) {
        setupConitionValues(sCurFilterSeq[sCurCondNo]);
    }
    updateCurCondCtrl();
}

function setupConitionValues(cond) {
    if (cond[1] != sCurStatUnit)
        return;
    if (cond[0] == "enum") {
        if (cond[2] && sOpEnumModeInfo != null) {
            mode = ["AND", "ONLY", "NOT"].indexOf(cond[2]);
            sOpEnumModeInfo[mode] = true;
            document.getElementById("cond-mode-" + 
                ["and", "only", "not"][mode]).checked = true;
        }
        var_list = cond[3];
        needs_zeros = false;
        for (j = 0; j < sOpEnumList.length; j++) {
            var_name = sOpEnumList[j][0];
            if (var_list.indexOf(var_name) < 0)
                continue;
            needs_zeros |= (sOpEnumList[j][1] == 0);
            document.getElementById("elcheck--" + j).checked = true;
        }
        if (needs_zeros)
            setCurEnumZeros(true);
    } else {
        sOpNumericInfo[0] = cond[2];
        sOpNumericInfo[5] = cond[3];
        sOpNumericInfo[6] = cond[4];
        sOpNumericInfo[7] = true;
        if (sOpNumericInfo[0] == 0) {
            sInputCurCondMin.value = sOpNumericInfo[5];
        } else {
            sInputCurCondMax.value = sOpNumericInfo[5];
        }
        sSpanCurCondSign.innerHTML = "&le;";
        if (sOpNumericInfo[6] != null) {
            sCheckCurCondUndef.checked = sOpNumericInfo[6];
            sSpanCurCondUndefCount.innerHTML = "undefined:" + cnt_undef;
        }
    }
}

function updateCurCondCtrl() {
    sDivCurCondNumeric.style.display = (sOpMode == "numeric")? "block":"none";
    sDivCurCondEnum.style.display    = (sOpMode == "enum")? "block":"none";

    sInputCurCondMin.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[0] == 0)? "visible":"hidden";
    sInputCurCondMax.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[0] == 1)? "visible":"hidden";
    sCheckCurCondUndef.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[1] > 0)? "visible":"hidden";
    sSpanCurCondUndefCount.style.visibility = 
        (sOpNumericInfo && sOpNumericInfo[1] > 0)? "visible":"hidden";

    sSpanCurCondModAnd.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[0] != null)? "visible":"hidden";
    sSpanCurCondModOnly.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[1] != null)? "visible":"hidden";
    sSpanCurCondModNot.style.visibility = 
        (sOpEnumModeInfo && sOpEnumModeInfo[2] != null)? "visible":"hidden";
        
    sBtnAddCond.disabled  = (sOpAddIdx == null);
    sBtnUpdateCond.disabled  = (sOpUpdateIdx == null); 
    sBtnDeleteCond.disabled = (sCurCondNo == null);
    sBtnUndoCond.disabled = (sFilterHistory.length == 0);
    sBtnRedoCond.disabled = (sFilterRedoStack.length == 0);
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
function checkCurCond(option) {
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
            if (sOpNumericInfo == null || sOpNumericInfo[6] == null)
                return;
            sOpNumericInfo[5] = !sOpNumericInfo[5];
            sCheckCurCondUndef.checked = sOpNumericInfo[5];
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
        sOpCondition = null;
        switch (sOpNumericInfo[0]) {
            case -1:
                if (sOpNumericInfo[1] > 0 && sOpNumericInfo[5]) {
                    sOpCondition = ["numeric", sCurStatUnit, -1, null, true];
                }
                break;
            case 0:
                if (sOpNumericInfo[4] != null && (sOpNumericInfo[7] ||
                        (sOpNumericInfo[2] != sOpNumericInfo[4]))) {
                    sOpCondition = ["numeric", sCurStatUnit, 0, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                } else {
                    if (sOpNumericInfo[1] > 0 && !sOpNumericInfo[5]) {
                        sOpCondition = ["numeric", sCurStatUnit, -1, null, false];
                    }
                }
                break;
            case 1:
                if (sOpNumericInfo[4] != null && (sOpNumericInfo[7] ||
                    (sOpNumericInfo[3] != sOpNumericInfo[4]))) {
                    sOpCondition = ["numeric", sCurStatUnit, 1, sOpNumericInfo[4],
                        sOpNumericInfo[5]];
                } else {
                    if (sOpNumericInfo[1] > 0 && !sOpNumericInfo[5]) {
                        sOpCondition = ["numeric", sCurStatUnit, -1, null, false];
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
        sOpUpdateIdx = findCond(sCurStatUnit, enum_mode);
        if (sOpUpdateIdx == null) 
            sOpUpdateIdx = findCond(sCurStatUnit);
        selectCond(sOpUpdateIdx);
        
        sel_names = [];
        for (j=0; j < sOpEnumList.length; j++) {
            if (document.getElementById("elcheck--" + j).checked)
                sel_names.push(sOpEnumList[j][0]);
        }
        if (sel_names.length > 0) {
            sOpAddIdx = (sOpUpdateIdx == null)? sCurFilterSeq.length:sOpUpdateIdx + 1;
            sOpCondition = ["enum", sCurStatUnit, enum_mode, sel_names];
        } else {
            sOpUpdateIdx = null;
        }
    }
    updateOpCondText();
    updateCurCondCtrl();
}

function checkNumericOpMin() {
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    sOpError = null;
    val = toNumeric(sOpNumericInfo[6], sInputCurCondMin.value);
    if (val == null) {
        sOpError = "Bad numeric value";
        sInputCurCondMin.className = "num-inp bad";
    } else {
        sOpNumericInfo[4] = val;
        sOpUpdateIdx = findCond(sCurStatUnit, 0);
        if (val < sOpNumericInfo[2]) {
            sInputCurCondMin.className = "num-inp bad";
            if (!sOpNumericInfo[7])
                sOpError = "Lower bound is above minimal value";
        } else {
            sInputCurCondMin.className = "num-inp";
        }
        if (sOpUpdateIdx == null) {
            if (sOpError == null) {
                idx = findCond(sCurStatUnit);
                sOpAddIdx = (idx == null)? sCurFilterSeq.length:idx + 1;
            }
        } 
    }
}

function checkNumericOpMax() {
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    sOpError = null;
    val = toNumeric(sOpNumericInfo[6], sInputCurCondMax.value);
    if (val == null) {
        sOpError = "Bad numeric value";
        sInputCurCondMax.className = "num-inp bad";
    } else {
        sOpNumericInfo[4] = val;
        sOpUpdateIdx = findCond(sCurStatUnit, 1);
        if (val > sOpNumericInfo[3]) {
            sInputCurCondMax.className = "num-inp bad";
            if (!sOpNumericInfo[7])
                sOpError = "Upper bound is below maximum value";
        } else {
            sInputCurCondMax.className = "num-inp";
        }
        if (sOpUpdateIdx == null) {
            if (sOpError == null) {
                idx = findCond(sCurStatUnit);
                sOpAddIdx = (idx == null)? sCurFilterSeq.length:idx + 1;
            }
        } else {
            selectCond(sOpUpdateIdx);
        }
    }
}

function checkEnumOpMode(mode_idx) {
    if (sOpEnumModeInfo == null || sOpEnumModeInfo[mode_idx] == null)
        return false;
    if (sOpEnumModeInfo[0] != null) {
        sOpEnumModeInfo[0] = (mode_idx == 0);
        sCheckCurCondModAnd.checked = (mode_idx == 0);
    }
    if (sOpEnumModeInfo[1] != null) {
        sOpEnumModeInfo[1] = (mode_idx == 1);
        sCheckCurCondModOnly.checked = (mode_idx == 1);
    }
    if (sOpEnumModeInfo[2] != null) {
        sOpEnumModeInfo[2] = (mode_idx == 2);
        sCheckCurCondModNot.checked = (mode_idx == 2);
    }
    return true;
}

function updateOpCondText() {
    if (sOpAddIdx != null || sOpUpdateIdx != null) 
        sSpanCurCondText.innerHTML = getCondDescripton(sOpCondition, true);
    else
        sSpanCurCondText.innerHTML = "";
    if (sOpError != null)
        sSpanCurCondError.innerHTML = sOpError;
    else
        sSpanCurCondError.innerHTML = "";
}


function setCurEnumZeros(value) {
    document.getElementById("cur-enum-zeros").checked = value;
    checkCurEnumZeros();
}

function checkCurEnumZeros() {
    sDivOpEnumList.className = 
        (document.getElementById("cur-enum-zeros").checked)? "":"no-zeros";
}
