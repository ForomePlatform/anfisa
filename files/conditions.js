var sFiltersOpMode = false;
var sFiltersTimeH  = null;

var sBtnFilters_Switch = null;
var sInpFilters_Name   = null;
var sSelFilters_Name   = null;
var sComboFilters_Name   = null;
var sBtnFilters_Load   = null;
var sBtnFilters_Create = null;
var sBtnFilters_Modify = null;
var sBtnFilters_Delete = null;

function initConditions() {
    sBtnFilters_Switch = document.getElementById("filter-filters-on");
    sInpFilters_Name   = document.getElementById("filter-name-filter");
    sSelFilters_Name   = document.getElementById("filter-name-filter-list");
    sComboFilters_Name = document.getElementById("filter-name-combo");
    sBtnFilters_Load   = document.getElementById("filter-load-flt");
    sBtnFilters_Create = document.getElementById("filter-create-flt");
    sBtnFilters_Modify = document.getElementById("filter-modify-flt");
    sBtnFilters_Delete = document.getElementById("filter-delete-flt");
    checkFiltersAllFilters();
}

function checkFiltersAllFilters() {
    if (sSelFilters_Name == null || sAllFilters == null)
        return;
    for (idx = sSelFilters_Name.length - 1; idx > 0; idx--) {
        sSelFilters_Name.remove(idx);
    }
    for (idx = 0; idx < sAllFilters.length; idx++) {
        flt_name = sAllFilters[idx];
        var option = document.createElement('option');
        option.innerHTML = flt_name;
        option.value = flt_name;
        sSelFilters_Name.append(option)
    }
}

/*************************************/
function checkCurConditionsProblem() {
    if (!sCurFilterSeq || sCurFilterSeq.length == 0)
        return "no conditions";
    if (sBaseFilterName != "_current_")
        return sBaseFilterName + " in work";
    return null;
}

/*************************************/
function findCond(unit_name, mode) {
    for (idx = 0; idx < sCurFilterSeq.length; idx++) {
        if (sCurFilterSeq[idx][1] == unit_name) {
            if (mode == undefined || sCurFilterSeq[idx][2] == mode)
                return idx;
        }
    }
    return null;
}

/*************************************/
function getCondDescripton(cond, short_form) {
    if (cond != null && cond[0] == "numeric") {
        rep_cond = [cond[1]];
        switch (cond[2]) {
            case 0:
                rep_cond.push("> " + cond[3]);
                break;
            case 1:
                rep_cond.push("< " + cond[3]);
                break;
        }
        switch (cond[4]) {
            case true:
                rep_cond.push("with undef");
                break
            case false:
                rep_cond.push("w/o undef");
                break;
        }
        return rep_cond.join(" ");
    }
    if (cond != null && cond[0] == "enum") {
        rep_cond = [cond[1], "IN"];
        if (cond[2]) 
            rep_cond.push(cond[2]);
        sel_names = cond[3];
        if (short_form && sel_names.length > 4) {
            rep_cond.push(sel_names.slice(0, 4).join(", "));
            rep_cond.push("...and " + (sel_names.length - 4) + " more")
        } else {
            rep_cond.push(sel_names.join(", "));
        }
        return rep_cond.join(" ");        
    }
    return ""
}

/*************************************/
function _modifyCond(new_filter_seq, filter_name) {
    sFilterHistory.push([sBaseFilterName, sCurFilterSeq]);
    sBaseFilterName = (filter_name)? filter_name:"_current_";
    sCurFilterSeq = new_filter_seq;
    sFilterRedoStack = [];
    loadStat();
    updateCurFilter(sBaseFilterName, true);
}

function filterAddCond() {
    if (sOpCondition != null && sOpAddIdx != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq.splice(sOpAddIdx, 0, sOpCondition);
        _modifyCond(new_filter_seq);
    }
}

function filterUpdateCond() {
    if (sOpCondition != null && sOpUpdateIdx != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq[sOpUpdateIdx] = sOpCondition;
        _modifyCond(new_filter_seq);
    }
}

function filterDeleteCond() {
    if (sCurCondNo != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq.splice(sCurCondNo, 1);
        _modifyCond(new_filter_seq);
    }
}

function filterUndoCond() {
    if (sFilterHistory.length > 0) {
        sFilterRedoStack.push([sBaseFilterName, sCurFilterSeq]);
        hinfo = sFilterHistory.pop();
        sBaseFilterName = hinfo[0];
        sCurFilterSeq = hinfo[1];
        loadStat();
        updateCurFilter(sBaseFilterName, true);
    }        
}

function filterRedoCond() {
    if (sFilterRedoStack.length > 0) {
        sFilterHistory.push([sBaseFilterName, sCurFilterSeq]);
        hinfo = sFilterRedoStack.pop();
        sBaseFilterName = hinfo[0];
        sCurFilterSeq = hinfo[1];
        loadStat();
        updateCurFilter(sBaseFilterName, true);
    }            
}

function filterLoadNamedFilter(filter_name) {
    _modifyCond(null, filter_name);    
}

/*************************************/
function updateFilterOpMode() {
    disp = (sFiltersOpMode)? "block":"none";
    sBtnFilters_Load.style.display = disp;  
    sBtnFilters_Create.style.display = disp;  
    sBtnFilters_Modify.style.display = disp;   
    sBtnFilters_Delete.style.display = disp;

    if (!sFiltersOpMode) {
        if (sFiltersTimeH != null) {
            clearInterval(sFiltersTimeH);
            sFiltersTimeH = null;
        }
        if (sBaseFilterName == "_current_") {
            sComboFilters_Name.style.display = "none";
        } else {
            sInpFilters_Name.value = sBaseFilterName;
            sInpFilters_Name.disabled = true;
            sSelFilters_Name.disabled = true;
            sComboFilters_Name.style.display = "block";
        }
        return;
    }
    sInpFilters_Name.value = (sBaseFilterName == "_current_")? "":sBaseFilterName;
    sInpFilters_Name.disabled = false;
    sSelFilters_Name.selectedIndex = 0;
    sSelFilters_Name.disabled = false;
    sComboFilters_Name.style.display = "block";
    checkFilterName();
}

function checkFilterName() {
    if (!sFiltersOpMode)
        return;
    filter_name = sInpFilters_Name.value;
    if (filter_name == sBaseFilterName) {
        q_named = false;
        q_create = sAllFilters.indexOf(filter_name) < 0;
        q_modify = (!q_create && sPreFilters.indexOf(filter_name) < 0);
        q_ok = q_modify;
    } else {
        q_modify = false;
        q_named = sAllFilters.indexOf(filter_name) >= 0;
        q_create = !q_named;
        if (q_named) {
            q_ok = true;
        } else {
            q_ok = /^[A-Za-z0-9_\-]+$/i.test(filter_name) && filter_name[0] != '_';
        }
    }
    sInpFilters_Name.className = (q_ok)? "": "bad";
    sBtnFilters_Load.disabled = !q_named;  
    sBtnFilters_Create.disabled = (!q_create) || (sCurFilterSeq.length == 0);  
    sBtnFilters_Modify.disabled = (!q_modify) || (sCurFilterSeq.length == 0);
    sBtnFilters_Delete.disabled = !q_modify;
    
    if (sFiltersTimeH == null) 
        sFiltersTimeH = setInterval(checkFilterName, 100);
}

/*************************************/
function clearFilterOpMode() {
    if (sFiltersOpMode) {
        sFiltersOpMode = false;
        updateFilterOpMode();
    }
}
/*************************************/
function filterFiltersSwitch() {
    sFiltersOpMode = !sFiltersOpMode;
    updateFilterOpMode();    
}

function fltFilterListSel() {
    sInpFilters_Name.value = sSelFilters_Name.value;
    checkFilterName();
}

function filterLoadFilter() {
    checkFilterName();
    if (sFiltersOpMode && !sBtnFilters_Load.disabled) {
        sBaseFilterName = sInpFilters_Name.value;
        sCurFilterSeq = null;
        loadStat();
        updateCurFilter(sBaseFilterName, true);
    }
}

function filterUpdateFilter(mode_mod) {
    checkFilterName();
    if (!sFiltersOpMode)
        return;
    if (mode_mod && sBtnFilters_Modify.disabled)
        return;
    if (!mode_mod && sBtnFilters_Create.disabled)
        return;
    loadStat("UPDATE/" + sInpFilters_Name.value);
    updateCurFilter(sBaseFilterName, true);
}

function filterDeleteFilter() {
    checkFilterName();
    if (!sFiltersOpMode)
        return;
    if (sBtnFilters_Delete.disabled)
        return;
    sBaseFilterName = "_current_";
    loadStat("DROP/" + sInpFilters_Name.value);
    updateCurFilter(sBaseFilterName, true);
}