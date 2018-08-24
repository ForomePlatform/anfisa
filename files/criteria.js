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
        if (crit[4]) 
            rep_crit.push("with undef");
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
        loadList();
    }
}

function filterUndoCrit() {
    if (sFilterHistory.length > 0) {
        sFilterRedoStack.push(sCurFilter);
        sCurFilter = sFilterHistory.pop();
        loadList();
    }        
}

function filterRedoCrit() {
    if (sFilterRedoStack.length > 0) {
        sFilterHistory.push(sCurFilter);
        sCurFilter = sFilterRedoStack.pop();
        loadList();
    }            
}

/*************************************/
