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

function initCriteria() {
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
function checkCurCriteriaProblem() {
    if (!sCurFilterSeq || sCurFilterSeq.length == 0)
        return "no rules";
    if (sBaseFilterName != "_current_")
        return sBaseFilterName + " in work";
    return null;
}

/*************************************/
function findCrit(unit_name, mode) {
    for (idx = 0; idx < sCurFilterSeq.length; idx++) {
        if (sCurFilterSeq[idx][1] == unit_name) {
            if (mode == undefined || sCurFilterSeq[idx][2] == mode)
                return idx;
        }
    }
    return null;
}

/*************************************/
function getCritDescripton(crit, short_form) {
    if (crit != null && crit[0] == "numeric") {
        rep_crit = [crit[1]];
        switch (crit[2]) {
            case 0:
                rep_crit.push("> " + crit[3]);
                break;
            case 1:
                rep_crit.push("< " + crit[3]);
                break;
        }
        switch (crit[4]) {
            case true:
                rep_crit.push("with undef");
                break
            case false:
                rep_crit.push("w/o undef");
                break;
        }
        return rep_crit.join(" ");
    }
    if (crit != null && crit[0] == "enum") {
        rep_crit = [crit[1], "IN"];
        if (crit[2]) 
            rep_crit.push(crit[2]);
        sel_names = crit[3];
        if (short_form && sel_names.length > 4) {
            rep_crit.push(sel_names.slice(0, 4).join(", "));
            rep_crit.push("...and " + (sel_names.length - 4) + " more")
        } else {
            rep_crit.push(sel_names.join(", "));
        }
        return rep_crit.join(" ");        
    }
    return ""
}

/*************************************/
function _modifyCrit(new_filter_seq, filter_name) {
    sFilterHistory.push([sBaseFilterName, sCurFilterSeq]);
    sBaseFilterName = (filter_name)? filter_name:"_current_";
    sCurFilterSeq = new_filter_seq;
    sFilterRedoStack = [];
    loadStat();
    updateCurFilter(sBaseFilterName, true);
}

function filterAddCrit() {
    if (sOpCriterium != null && sOpAddIdx != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq.splice(sOpAddIdx, 0, sOpCriterium);
        _modifyCrit(new_filter_seq);
    }
}

function filterUpdateCrit() {
    if (sOpCriterium != null && sOpUpdateIdx != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq[sOpUpdateIdx] = sOpCriterium;
        _modifyCrit(new_filter_seq);
    }
}

function filterDeleteCrit() {
    if (sCurCritNo != null) {
        new_filter_seq = sCurFilterSeq.slice();
        new_filter_seq.splice(sCurCritNo, 1);
        _modifyCrit(new_filter_seq);
    }
}

function filterUndoCrit() {
    if (sFilterHistory.length > 0) {
        sFilterRedoStack.push([sBaseFilterName, sCurFilterSeq]);
        hinfo = sFilterHistory.pop();
        sBaseFilterName = hinfo[0];
        sCurFilterSeq = hinfo[1];
        loadStat();
        updateCurFilter(sBaseFilterName, true);
    }        
}

function filterRedoCrit() {
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
    _modifyCrit(null, filter_name);    
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
        q_ok = false;
        q_delete = sAllFilters.indexOf(filter_name) >= 0;
    } else {
        q_delete = false;
        q_named = sAllFilters.indexOf(filter_name) >= 0;
        if (q_named) {
            q_ok = true;
        } else {
            q_ok = /^[A-Za-z0-9_\-]+$/i.test(filter_name) && filter_name[0] != '_';
        }
    }
    sInpFilters_Name.className = (q_ok)? "": "bad";
    sBtnFilters_Load.disabled = !q_named;  
    sBtnFilters_Create.disabled = q_named || (!q_ok) || (sCurFilterSeq.length == 0);  
    sBtnFilters_Modify.disabled = !q_named;   
    sBtnFilters_Delete.disabled = !q_delete;
    
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