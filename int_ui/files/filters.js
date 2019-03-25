var sCurFilterSeq = [];
var sFilterHistory = [];
var sFilterRedoStack = [];
var sBaseFilterName = "_current_";
var sFilterCtx = null;

var sStatList = null;
var sStatUnitIdxs = null;
var sCurStatUnit = null;
var sCurCondNo = null;
var sCurZygName = null;

var sOpMode = null;
var sOpEnumList = null;
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
    
    sOpNumH.init();
    sOpEnumH.init();

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
    if (sFilterCtx != null)
        args += "&ctx=" + encodeURIComponent(JSON.stringify(sFilterCtx));

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
        if (unit_type == "zygosity") 
            sZygosityH.setup(unit_stat, list_stat_rep);
        else {
            if (unit_type == "int" || unit_type == "float") {
                val_min   = unit_stat[2];
                val_max   = unit_stat[3];
                count     = unit_stat[4];
                cnt_undef = unit_stat[5];
                if (count == 0) {
                    list_stat_rep.push(
                        '<span class="stat-bad">Out of choice</span>');
                } else {
                    if (val_min == val_max) {
                        list_stat_rep.push('<span class="stat-ok">' + 
                            val_min + '</span>');
                    } else {
                        list_stat_rep.push('<span class="stat-ok">' + 
                            val_min + ' =< ...<= ' + val_max + ' </span>');
                    }
                    list_stat_rep.push(': <span class="stat-count">' + count + 
                        ' records</span>');
                    if (cnt_undef > 0) 
                        list_stat_rep.push(
                            '<span class="stat-undef-count">+' + 
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
                        list_stat_rep.push(
                            '<p><span class="stat-comment">...and ' + 
                            list_count + ' variants more...</span></p>');
                    }
                } else {
                    list_stat_rep.push(
                        '<span class="stat-bad">Out of choice</span>');
                }
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
    sCurZygName = null;
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
    sCurZygName = sZygosityH.checkUnitTitle(stat_unit);
    new_unit_el.className = new_unit_el.className + " cur";
    if (sCurCondNo == null || sCurFilterSeq[sCurCondNo][1] != sCurStatUnit)
        selectCond(findCond(sCurStatUnit));
    setupStatUnit();
}

/*************************************/
function updateZygUnit(zyg_name) {
    if (sCurZygName != null) {
        sCurZygName = zyg_name;
        selectStat(sCurStatUnit, true);
    }
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
        sZygosityH.onSelectCondition(sCurFilterSeq[cond_no]);
        selectStat(sCurFilterSeq[sCurCondNo][1], true);
    }
}

/*************************************/
function setupStatUnit() {
    sOpMode = null;
    sOpCondition = null;
    sOpEnumList = null;
    sOpError = null;
    sOpAddIdx = null;
    sOpUpdateIdx = null;
    updateOpCondText();
    
    title_el = document.getElementById("cond-title");
    if (sCurStatUnit == null) {
        title_el.innerHTML = "";
        updateCurCondCtrl();
        return;
    } 
    title_el.innerHTML = (sCurZygName == null)? sCurStatUnit: sCurZygName;
    unit_stat = sStatList[sStatUnitIdxs[sCurStatUnit]];
    unit_type = unit_stat[0];
    if (unit_type == "int" || unit_type == "float") {
        sOpMode = "numeric";
        sOpNumH.updateUnit(unit_stat);
    } else {
        sOpMode = "enum";
        sOpEnumH.updateUnit(unit_stat);
    }
    if (sCurCondNo != null) {
        setupConditionValues(sCurFilterSeq[sCurCondNo]);
    }
    updateCurCondCtrl();
}

function setupConditionValues(cond) {
    if (cond[1] != sCurStatUnit)
        return;
    sOpUpdateIdx = sCurCondNo;
    if (cond[0] == "numeric") 
        sOpNumH.updateCondition(cond);
    else
        sOpEnumH.updateCondition(cond);
}

function updateCurCondCtrl() {
    sDivCurCondNumeric.style.display = (sOpMode == "numeric")? "block":"none";
    sDivCurCondEnum.style.display    = (sOpMode == "enum")? "block":"none";

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
    sOpNumH.checkControls();
    cond_data = sOpNumH.getConditionData();
    sOpCondition = (cond_data == null)? null:
        ["numeric", sCurStatUnit].concat(cond_data);
    sOpError = sOpNumH.getMessage();
    if (sOpCondition != null) {
        if (sOpUpdateIdx == null)
            sOpUpdateIdx = findCond(sCurStatUnit);
        if (sOpUpdateIdx == null)
            sOpAddIdx = sCurFilterSeq.length;
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

/**************************************/
var sOpEnumH = {
    mVariants: null,
    mOperationMode: null,
    mDivVarList: null,
    mSpecCtrl: null,
    mStatusMode: null,

    init: function() {
        this.mDivVarList = document.getElementById("op-enum-list");
    },
    
    getCondType: function() {
        if (this.mSpecCtrl != null)
            return this.mSpecCtrl.getCondType();
        return "enum";
    },
    
    suspend: function() {
        this.mVariants = null;
        this.mOperationMode = null;
        this.careControls();
    },

    updateUnit: function(unit_stat) {
        if (unit_stat[0] == "zygosity") {
            this.mSpecCtrl = sZygosityH;
            this.mVariants = sZygosityH.getVariants(unit_stat);
            this.mOperationMode = null;
            this.mStatusMode = null;
        } else {
            this.mVariants = unit_stat[2];
            this.mOperationMode = 0;
            this.mStatusMode = (unit_stat[0] == "status");
            this.mSpecCtrl = null;
        }
        
        list_val_rep = [];
        has_zero = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            var_count = this.mVariants[j][1];
            has_zero |= (var_count == 0);
            list_val_rep.push('<div class="enum-val' + 
                ((var_count==0)? " zero":"") +'">' +
                '<input id="elcheck--' + j + '" type="checkbox" ' + 
                'onchange="sOpEnumH.checkControls();"/>&emsp;' + var_name + 
                '<span class="enum-cnt">(' + var_count + ')</span></div>');
        }
        this.mDivVarList.innerHTML = list_val_rep.join('\n');
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero)? "block":"none";            
        this.careEnumZeros(false);
        this.checkControls();
    },
    
    updateCondition: function(cond) {
        if (this.mSpecCtrl != null) {
            this.mSpecCtrl = sZygosityH;
            var_list = this.mSpecCtrl.getCondVarList(cond);
            op_mode = this.mSpecCtrl.getCondOpMode(cond);
        } else {
            var_list = cond[3];
            op_mode = cond[2];
        }
        if (this.mOperationMode != null)
            this.mOperationMode = ["", "AND", "ONLY", "NOT"].indexOf(op_mode);
        needs_zeros = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            if (var_list.indexOf(var_name) < 0)
                continue;
            needs_zeros |= (this.mVariants[j][1] == 0);
            document.getElementById("elcheck--" + j).checked = true;
        }
        this.careEnumZeros(needs_zeros);
        this.careControls();
    },
    
    careControls: function() {
        document.getElementById("cur-cond-enum").style.display = 
            (this.mVariants == null)? "none":"block";
        for (idx = 1; idx < 4; idx++) {
            vmode = ["or", "and", "only", "not"][idx];
            document.getElementById("cond-mode-" + vmode + "-span").
                style.visibility = (this.mOperationMode == null ||
                    (this.mStatusMode && idx != 3))? "hidden":"visible";
            document.getElementById("cond-mode-" + vmode).checked =
                (idx == this.mOperationMode);
        }
    },

    careEnumZeros: function(opt) {
        var check_enum_z = document.getElementById("cur-enum-zeros");
        if (opt == undefined) {
            show_zeros = check_enum_z.checked;
        } else {
            show_zeros = opt;
            check_enum_z.checked = show_zeros;
        }
        this.mDivVarList.className = (show_zeros)? "":"no-zeros";
    },
    
    checkControls: function(opt) {
        if (this.mVariants == null) 
            return;
        this.careControls();
        condition = null;
        message = null;
        if (opt != undefined && this.mOperationMode != null) {
            if (this.mOperationMode == opt)
                this.mOperationMode = 0;
            else
                this.mOperationMode = opt;
            
        }
        sel_names = [];
        for (j=0; j < this.mVariants.length; j++) {
            if (document.getElementById("elcheck--" + j).checked)
                sel_names.push(this.mVariants[j][0]);
        }
        op_mode = "";
        if (this.mOperationMode != null)
            op_mode = ["", "AND", "ONLY", "NOT"][this.mOperationMode];
        
        condition_data = null;
        if (sel_names.length > 0) {
            condition = ["enum", sCurStatUnit, op_mode, sel_names];
        }

        message = "";
        if (this.mSpecCtrl != null) {
            condition = this.mSpecCtrl.transCondition(condition);
            message = this.mSpecCtrl.checkError();
        }
        this.careControls();
        sOpCondition = condition;
        sOpError = this.mMessage;
        sOpAddIdx = (sOpCondition != null)? sCurFilterSeq.length : null;
        if (sOpCondition != null) {
            if (sOpUpdateIdx == null)
                sOpUpdateIdx = findCond(sCurStatUnit);
        }
        updateOpCondText();
        updateCurCondCtrl();
    },

    getConditionData: function() {
        return this.mConditionData;
    },
    
    getMessage: function() {
        return this.mMessage;
    }
};

/**************************************/
var sZygosityH = {
    mFamily: null,
    mProblemIdxs: null,
    mUnitName: null,
    mDefaultIdxs: null,
    mZStat: null,
    mZEmpty: null,
    
    setup: function(unit_stat, list_stat_rep) {
        this.mUnitName = unit_stat[1]["name"];
        this.mFamily = unit_stat[1]["family"];
        this.mDefaultIdxs = unit_stat[1]["affected"];
        this.mProblemIdxs = unit_stat[2];
        this.mZStat = unit_stat[3] ;
        if (this.mProblemIdxs == null)
            this.mProblemIdxs = [];
        list_stat_rep.push('<div class="zyg-wrap"><div class="zyg-family">');
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            q_checked = (this.mProblemIdxs.indexOf(idx)>=0)? " checked":"";
            list_stat_rep.push('<div class="zyg-fam-member">' + 
                '<input type="checkbox" id="zyg_fam_m__' + idx + '" ' + q_checked + 
                ' onchange="sZygosityH.checkMember(' + idx + ');" />' +
                this.mFamily[idx] + '</div>');
        }
        if (this.mDefaultIdxs.length > 0) {
            reset_dis = (this.mDefaultIdxs.join(',') == this.mProblemIdxs.join(','))?
                'disabled="true"':'';
            list_stat_rep.push('<button id="zyg_fam_reset" ' +
                'title="Reset affected group" ' + reset_dis + 
                ' onclick="sZygosityH.resetGrp()">Reset</button>');
        }
        list_stat_rep.push('</div><div id="zyg-stat">');
        this._reportStat(list_stat_rep);
        list_stat_rep.push('</div></div>');
        sFilterCtx = {"problem_group": this.mProblemIdxs.slice()}
    },
    
    getCondType: function() {
        return "zygosity";
    },
    
    getVariants: function(unit_stat) {
        return (this.mZStat == null)? []:this.mZStat;
    },
    
    transCondition: function(condition) {
        if (condition == null || this.mZStat == mull || this.mZEmpty)
            return null;
        ret = condition_data.slice();
        ret[0] = "zygosity";
        ret.splice(2, 0, this.mProblemIdxs.slice());
        return ret;
    },
    
    checkError: function() {
        if (this.mZStat == null)
            return " Determine problem group";
        if (this.mZEmpty)
            return "Out of choice";
        return "";
    },
    
    getUnitTitle: function(problem_group) {
        if (problem_group == undefined)
            problem_group = this.mProblemIdxs;
        return this.mUnitName + '({' + problem_group.join(',') + '})';        
    },
    
    checkUnitTitle: function(unit_name) {
        if (unit_name != this.mUnitName)
            return null;
        return this.getUnitTitle();
    },
    
    getCondOpMode: function(condition_data) {
        return condition_data[3];
    },
    
    getCondVarList: function(condition_data) {
        return condition_data[4];
    },
    
    onSelectCondition: function(condition_data) {
        if (condition_data[1] != this.mUnitName)
            return;
        if (this.mProblemIdxs.join(",") != condition_data[2].join(",")) {
            this.mProblemIdxs = condition_data[2];
            this._reselectFamily();
        }
    },
    
    _reselectFamily: function() {
        for (var m_idx = 0; m_idx < this.mFamily.length; m_idx++)
            document.getElementById("zyg_fam_m__" + m_idx).checked =
                (this.mProblemIdxs.indexOf(m_idx) >= 0);
        this.refreshContext();
    },
    
    _reportStat: function(list_stat_rep) {
        this.mZEmpty = true;
        if (this.mZStat == null) {
            list_stat_rep.push('<span class="stat-bad">Determine problem group</span>');
        } else {
            list_count = 0;
            for (j = 0; j < this.mZStat.length; j++) {
                if (this.mZStat[j][1] > 0)
                    list_count++;
            }
            if (list_count > 0) {
                list_stat_rep.push('<ul>');
                for (j = 0; j < this.mZStat.length; j++) {
                    var_name = this.mZStat[j][0];
                    var_count = this.mZStat[j][1];
                    if (var_count == 0)
                        continue;
                    this.mZEmpty = false;
                    list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                        '<span class="stat-count">' +
                        var_count + ' records</span></li>');
                }
            } else {
                list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
            }
        }
    },
    
    resetGrp: function() {
        if (this.mDefaultIdxs != this.mProblemIdxs) {
            this.mProblemIdxs = this.mDefaultIdxs;
            this._reselectFamily();
            return;
        }
    },
    
    checkMember: function(m_idx) {
        m_checked = document.getElementById("zyg_fam_m__" + m_idx).checked;
        if (m_checked && this.mProblemIdxs.indexOf(m_idx) < 0) {
            this.mProblemIdxs.push(m_idx);
            this.mProblemIdxs.sort();
            this.refreshContext();
            return;
        } 
        if (!m_checked) {
            pos = this.mProblemIdxs.indexOf(m_idx);
            if (pos >= 0) {
                this.mProblemIdxs.splice(pos, 1);
                this.refreshContext();
            }
        }
    },
    
    refreshContext: function() {
        if (this.mDefaultIdxs.length > 0)
            document.getElementById("zyg_fam_reset").disabled = 
                (this.mDefaultIdxs.join(',') == this.mProblemIdxs.join(','));
        sFilterCtx = {"problem_group": this.mProblemIdxs.slice()};
        args = "ws=" + parent.window.sWorkspaceName + "&unit=" + 
            this.mUnitName + "&conditions=" +
            encodeURIComponent(JSON.stringify(sCurFilterSeq)) +
            "&ctx=" + encodeURIComponent(JSON.stringify(sFilterCtx));

        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var info = JSON.parse(this.responseText);
                sZygosityH._refresh(info);
            }
        };
        xhttp.open("POST", "statunit", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send(args);
    },
    
    _refresh: function(info) {
        this.mZStat = info[3];
        rep_list = [];
        this._reportStat(rep_list);
        document.getElementById("zyg-stat").innerHTML = rep_list.join('\n');
        updateZygUnit(this.getUnitTitle());
    }
};

/*************************************/
function updateOpCondText() {
    document.getElementById("cond-text").innerHTML = 
        (sOpAddIdx != null || sOpUpdateIdx != null)?
            getCondDescripton(sOpCondition, true) : "";
    el_message = document.getElementById("cond-message");
    el_message.innerHTML = (sOpError != null)? sOpError:"";
    el_message.className = (sOpCondition == null)? "bad":"message";
}
