var sFiltersTimeH  = null;
var sFilterCurOp   = null;

var sBtnFilters_Switch = null;
var sInpFilters_Name   = null;
var sSelFilters_Name   = null;
var sComboFilters_Name = null;
var sDivFiltersOpList  = null;
var sBtnFilters_Op     = null;
var sBtnFilters_Clear  = null;

function initConditions() {
    sBtnFilters_Switch = document.getElementById("filter-filters-on");
    sInpFilters_Name   = document.getElementById("filter-name-filter");
    sSelFilters_Name   = document.getElementById("filter-name-filter-list");
    sComboFilters_Name = document.getElementById("filter-name-combo");
    sDivFiltersOpList  = document.getElementById("filters-op-list");
    sBtnFilters_Op     = document.getElementById("filter-flt-op");
    sBtnFilters_Clear  = document.getElementById("filter-clear-all");
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
    rep_cond = (short_form)? []:[cond[1]];
    if (cond != null && cond[0] == "numeric") {
        switch (cond[2]) {
            case 0:
                rep_cond.push("&ge; " + cond[3]);
                break;
            case 1:
                rep_cond.push("&le; " + cond[3]);
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
        rep_cond.push("IN");
        if (cond[2] && cond[2] != "OR") 
            rep_cond.push('[' + cond[2] + ']');
        sel_names = cond[3];
        if (sel_names.length > 0)
            rep_cond.push(sel_names[0]);
        else
            rep_cond.push("&lt;?&gt;")
        rep_cond = [rep_cond.join(' ')];        
        rep_len = rep_cond[0].length;
        for (j=1; j<sel_names.length; j++) {
            if (short_form && rep_len > 45) {
                rep_cond.push('<i>+ ' + (sel_names.length - j) + ' more</i>');
                break;
            }
            rep_len += 2 + sel_names[j].length;
            rep_cond.push(sel_names[j]);
        }
        return rep_cond.join(', ');
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

function filterClearAll() {
    if (sCurFilterSeq.length > 0) {
        sFilterHistory.push([sBaseFilterName, sCurFilterSeq]);
        sBaseFilterName = "_current_";
        sCurFilterSeq = [];
        loadStat();
        updateCurFilter(sBaseFilterName, true);
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
function prepareFilterOperations() {
    sFilterCurOp = null;
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
    sInpFilters_Name.style.visibility = "visible";
    sBtnFilters_Clear.disabled = (sCurFilterSeq.length == 0);
    document.getElementById("filters-op-create").className = 
        (sCurFilterSeq.length == 0)? "disabled":"";
    document.getElementById("filters-op-modify").className = 
        (sCurFilterSeq.length == 0 || sBaseFilterName != "_current_" ||
            (sOpFilters.length == 0))? "disabled":"";
    document.getElementById("filters-op-delete").className = 
        (sBaseFilterName == "_current_" || 
            sOpFilters.indexOf(sBaseFilterName) < 0)? "disabled":"";
    /*flt_time = sFltTimeDict[sBaseFilterName];
    document.getElementById("filter-upd-time").innerHTML = 
        (flt_time)? timeRepr(flt_time):'';*/
    sBtnFilters_Op.style.display = "none";
    wsDropShow(false);
}

function checkFilterAsIdent(filter_name) {
    return /^[A-Za-z0-9_\-]+$/i.test(filter_name) && filter_name[0] != '_';
}

function checkFilterName() {
    if (sFilterCurOp == null)
        return;

    filter_name = sInpFilters_Name.value;
    q_all = sAllFilters.indexOf(filter_name) >= 0;
    q_op  = sOpFilters.indexOf(filter_name) >= 0;
    q_load = sLoadFilters.indexOf(filter_name) >= 0;
    
    if (sFilterCurOp == "modify") {
        sBtnFilters_Op.disabled = (!q_op) || filter_name == sBaseFilterName;
        return;
    }
    if (sFilterCurOp == "load") {
        sBtnFilters_Op.disabled = (!q_load) || filter_name == sBaseFilterName;
        return;
    }
    
    if (sFilterCurOp != "create") {
        return; /*assert false! */
    }
    
    q_ok = (q_all)? false: checkFilterAsIdent(filter_name);
    
    sInpFilters_Name.className = (q_ok)? "": "bad";
    sBtnFilters_Op.disabled = !q_ok;
    
    if (sFiltersTimeH == null) 
        sFiltersTimeH = setInterval(checkFilterName, 100);
}

/*************************************/
function clearFilterOpMode() {
    prepareFilterOperations();
    wsDropShow(false);
}

/*************************************/
function filtersOpMenu() {
    if (sDivFiltersOpList.style.display != "none") {
        clearFilterOpMode();
        return;
    }
    prepareFilterOperations();
    wsDropShow(true);
    sDivFiltersOpList.style.display = "block";
}

/*************************************/
function fltFilterListSel() {
    sInpFilters_Name.value = sSelFilters_Name.value;
    checkFilterName();
}

/*************************************/
function filterOpStartLoad() {
    wsDropShow(false);
    sFilterCurOp = "load";
    sInpFilters_Name.value = "";
    sInpFilters_Name.style.visibility = "hidden";
    fillSelectFilterNames(false, sLoadFilters);
    sSelFilters_Name.disabled = false;
    sBtnFilters_Op.innerHTML = "Load";
    sBtnFilters_Op.style.display = "block";
    fltFilterListSel();
    sComboFilters_Name.style.display = "block";
}

function filterOpStartCreate() {
    if (sCurFilterSeq.length == 0)
        return;
    wsDropShow(false);
    sFilterCurOp = "create";
    sInpFilters_Name.value = "";
    sInpFilters_Name.style.visibility = "visible";
    sSelFilters_Name.disabled = false;
    sInpFilters_Name.disabled = false;
    fillSelectFilterNames(true, sAllFilters);
    sBtnFilters_Op.innerHTML = "Create";
    sBtnFilters_Op.style.display = "block";
    checkFilterName();
    sComboFilters_Name.style.display = "block";
}

function filterOpStartModify() {
    if (sCurFilterSeq.length == 0 || sBaseFilterName != "_current_")
        return;
    wsDropShow(false);
    fillSelectFilterNames(false, sOpFilters);
    sFilterCurOp = "modify";
    sInpFilters_Name.value = "";
    sInpFilters_Name.style.visibility = "hidden";
    sSelFilters_Name.disabled = false;
    sBtnFilters_Op.innerHTML = "Modify";
    sBtnFilters_Op.style.display = "block";
    fltFilterListSel();
    sComboFilters_Name.style.display = "block";
}

function filterOpDelete() {
    if (sBaseFilterName == "_current_" || 
            sOpFilters.indexOf(sBaseFilterName) < 0)
        return;
    wsDropShow(false);
    sBaseFilterName = "_current_";
    loadStat(["instr", "DROP/" + sInpFilters_Name.value]);
    updateCurFilter(sBaseFilterName, true);
}

function filterFiltersOperation() {
    filter_name = sInpFilters_Name.value;
    q_all = sAllFilters.indexOf(filter_name) >= 0;
    q_op = sOpFilters.indexOf(filter_name) >= 0;
    q_load = sLoadFilters.indexOf(filter_name) >= 0;
    
    switch (sFilterCurOp) {
        case "create":
            if (!q_all && checkFilterAsIdent(filter_name)) {
                loadStat(["instr", "UPDATE/" + filter_name]);
                updateCurFilter(sBaseFilterName, true);
            }
            break;
        case "modify":
            if (q_op && filter_name != sBaseFilterName) {
                loadStat(["instr", "UPDATE/" + filter_name]);
                updateCurFilter(sBaseFilterName, true);
            }
            break;
        case "load":
            if (q_load && filter_name != sBaseFilterName) {
                sBaseFilterName = filter_name;
                sCurFilterSeq = null;
                loadStat();
                updateCurFilter(sBaseFilterName, true);
            }
            break;
    }
}

function fillSelectFilterNames(with_empty, filter_list) {
    if (sSelFilters_Name == null || sAllFilters == null)
        return;
    for (idx = sSelFilters_Name.length -1; idx >= 0; idx--) {
        sSelFilters_Name.remove(idx);
    }
    if (with_empty) {
        var option = document.createElement('option');
        option.innerHTML = "";
        option.value = "";
        sSelFilters_Name.append(option)
    }
    for (idx = 0; idx < filter_list.length; idx++) {
        flt_name = filter_list[idx];
        var option = document.createElement('option');
        option.innerHTML = flt_name;
        option.value = flt_name;
        sSelFilters_Name.append(option)
    }
    sSelFilters_Name.selectedIndex = 0;
}

