var sCurFilterSeq = [];
var sFilterHistory = [];
var sFilterRedoStack = [];
var sBaseFilterName = "_current_";

var sStatList = null;
var sStatUnitIdxs = null;
var sCurStatUnit = null;
var sCurCondNo = null;

var sOpMode = null;
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
var sSpanCurCondModOnly     = null;
var sSpanCurCondModAnd      = null;
var sSpanCurCondModNot      = null;

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

    sSpanCurCondModOnly     = document.getElementById("cond-mode-only-span");
    sSpanCurCondModAnd      = document.getElementById("cond-mode-and-span");
    sSpanCurCondModNot      = document.getElementById("cond-mode-not-span");
    
    sCheckCurCondModOnly    = document.getElementById("cond-mode-only");
    sCheckCurCondModAnd     = document.getElementById("cond-mode-and");
    sCheckCurCondModNot     = document.getElementById("cond-mode-not");

    sOpNumH.init();
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
        args += "&" + add_instr[0] + "=" + encodeURIComponent(add_instr[1]);
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
    sBaseFilterName = info["cur-filter"];
    sStatUnitIdxs = {}
    if (sCurFilterSeq == null) 
        sCurFilterSeq = info["conditions"];
    _checkNamedFilters(info["filter-list"]);
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

function _checkNamedFilters(filter_list) {
    var all_filters = setupNamedFilters(filter_list);
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
        sOpNumH.updateUnit(unit_stat);
    } else {
        sOpMode = "enum";
        if (unit_type == "status") {
            sOpEnumModeInfo = [null, null, false];
        } else {
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
        setupConditionValues(sCurFilterSeq[sCurCondNo]);
    }
    updateCurCondCtrl();
}

function setupConditionValues(cond) {
    if (cond[1] != sCurStatUnit)
        return;
    if (cond[0] == "enum") {
        if (cond[2] && sOpEnumModeInfo != null) {
            mode = ["AND", "ONLY", "NOT"].indexOf(cond[2]);
            if (mode >= 0 && sOpEnumModeInfo[mode] != null) {
                sOpEnumModeInfo[mode] = true;
                document.getElementById("cond-mode-" + 
                    ["and", "only", "not"][mode]).checked = true;
            }
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
        sOpNumH.updateCondition(cond)
    }
}

function updateCurCondCtrl() {
    sDivCurCondNumeric.style.display = (sOpMode == "numeric")? "block":"none";
    sDivCurCondEnum.style.display    = (sOpMode == "enum")? "block":"none";

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
function checkOpNum() {
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    sOpNumH.checkControls();
    cond_data = sOpNumH.getConditionData();
    sOpCondition = (cond_data == null)? null:
        ["numeric", sCurStatUnit].concat(cond_data);
    sOpError = sOpNumH.getMessage();
    if (sOpCondition != null) {
        sOpUpdateIdx = findCond(sCurStatUnit);
        if (sOpUpdateIdx == null)
            sOpAddIdx = sCurFilterSeq.length;
    }
    updateOpCondText();
    updateCurCondCtrl();
}

function checkCurCond(option) {
    switch(option) {
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

/**************************************/
var sOpNumH = {
    mInfo: null,
    mInputMin: null,
    mInputMax: null,
    mCheckUndef: null,
    mSpanUndefCount: null,
    mConditionData: null,
    mMessage: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
        this.mCheckUndef = document.getElementById("cond-undef-check")
        this.mSpanUndefCount = document.getElementById("cond-undef-count");
    },
    
    getCondType: function() {
        return "numeric";
    },

    suspend: function() {
        this.mInfo = null;
        this.mConditionData = null;
        this.mMessage = null;
        this.careControls();
    },
    
    updateUnit: function(unit_stat) {
        this.mInfo = {
            cur_bounds: [null, null],
            fix_bounds: null,
            with_undef: null,
            unit_type:  unit_stat[0],
            val_min:    unit_stat[2],
            val_max:    unit_stat[3],
            count:      unit_stat[4],
            cnt_undef:  unit_stat[5]}
        if (this.mInfo.cnt_undef > 0) 
            this.mInfo.with_undef = false;
        this.mConditionData = null;
        this.mMessage = null;
        
        document.getElementById("cond-min").innerHTML = this.mInfo.val_min;
        document.getElementById("cond-max").innerHTML = this.mInfo.val_max;
        document.getElementById("cond-sign").innerHTML = 
            (this.mInfo.val_min == this.mInfo.val_max)? "=":"&le;";
        this.mInputMin.value = "";
        this.mInputMax.value = "";
        this.mCheckUndef.checked = false;
        this.mSpanUndefCount.innerHTML = (this.mInfo.cnt_undef > 0)?
            ("undefined:" + this.mInfo.cnt_undef) : "";
    },

    updateCondition: function(cond) {
        this.mInfo.fixed_bounds = [cond[2][0], cond[2][1]];
        this.mInfo.cur_bounds   = [cond[2][0], cond[2][1]];
        this.mInfo.with_undef   = cond[3];
        this.mInputMin.value = (this.mInfo.cur_bounds[0] != null)?
            this.mInfo.cur_bounds[0] : "";
        this.mInputMax.value = (this.mInfo.cur_bounds[1] != null)?
            this.mInfo.cur_bounds[1] : "";
        document.getElementById("cond-sign").innerHTML = "&le;";
        if (this.mInfo.with_undef != null) {
            this.mCheckUndef.checked = this.mInfo.with_undef;
            this.mSpanUndefCount.innerHTML = "undefined:" + this.mInfo.cnt_undef;
        }
    },

    careControls: function() {
        document.getElementById("cur-cond-numeric").style.display = 
            (this.mInfo == null)? "none":"block";
        this.mCheckUndef.style.visibility = 
            (this.mInfo && this.mInfo.cnt_undef > 0)? "visible":"hidden";
        this.mSpanUndefCount.style.visibility = 
            (this.mInfo && this.mInfo.cnt_undef > 0)? "visible":"hidden";
    },

    checkControls: function() {
        if (this.mInfo == null) 
            return;
        this.mConditionData = null;
        this.mMessage = null;
        if (this.mInputMin.value.trim() == "") {
            this.mInfo.cur_bounds[0] = null;
            this.mInputMin.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMin.value)
            this.mInputMin.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                this.mMessage = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[0] = val;
            }
        }
        if (this.mInputMax.value.trim() == "") {
            this.mInfo.cur_bounds[1] = null;
            this.mInputMax.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value)
            this.mInputMax.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                this.mMessage = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[1] = val;
            }
        }
        if (this.mInfo.with_undef != null) {
            this.mInfo.with_undef = this.mCheckUndef.checked;
        }
        if (this.mMessage == null) {
            if (this.mInfo.cur_bounds[0] == null && 
                    this.mInfo.cur_bounds[1] == null && 
                    !this.mInfo.with_undef)
                this.mMessage = "";            
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[0] > this.mInfo.val_max)
                this.mMessage = "Lower bound is above maximum value";
            if (this.mInfo.cur_bounds[1] != null && 
                    this.mInfo.cur_bounds[1] < this.mInfo.val_min)
                this.mMessage = "Upper bound is below minimum value";
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[1] != null && 
                    this.mInfo.cur_bounds[0] > this.mInfo.cur_bounds[1])
                this.mMessage = "Bounds are mixed up";
        }
        if (this.mMessage == null) {
            this.mConditionData = [this.mInfo.cur_bounds, this.with_undef]
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[0] < this.mInfo.val_min &&
                    (this.mInfo.fix_bounds == null || 
                    this.mInfo.fix_bounds[0] != this.mInfo.cur_bounds[0]))
                this.mMessage = "Lower bound is below minimal value";
            if (this.mInfo.cur_bounds[1] != null && 
                    this.mInfo.cur_bounds[1] > this.mInfo.val_max &&
                    (this.mInfo.fix_bounds == null || 
                    this.mInfo.fix_bounds[1] != this.mInfo.cur_bounds[1]))
                this.mMessage = "Upper bound is above maximal value";
        }
        this.careControls();
    },
    
    getConditionData: function() {
        return this.mConditionData;
    },
    
    getMessage: function() {
        return this.mMessage;
    }
};

function checkEnumOpMode(mode_idx) {
    if (sOpEnumModeInfo == null || sOpEnumModeInfo[mode_idx] == null)
        return false;
    if (sOpEnumModeInfo[mode_idx])
        mode_idx = -1;
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
    document.getElementById("cond-text").innerHTML = 
        (sOpAddIdx != null || sOpUpdateIdx != null)?
            getCondDescripton(sOpCondition, true) : "";
    el_message = document.getElementById("cond-message");
    el_message.innerHTML = (sOpError != null)? sOpError:"";
    el_message.className = (sOpCondition == null)? "bad":"message";
}

function setCurEnumZeros(value) {
    document.getElementById("cur-enum-zeros").checked = value;
    checkCurEnumZeros();
}

function checkCurEnumZeros() {
    sDivOpEnumList.className = 
        (document.getElementById("cur-enum-zeros").checked)? "":"no-zeros";
}
