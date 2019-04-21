/*************************************/
/* Utilities                         */
/*************************************/
function getCondDescription(cond, short_form) {
    if (cond == null)
        return "";
    if (cond != null && cond[0] == "numeric") {
        rep_cond = [];
        if (cond[2][0] != null)
            rep_cond.push(cond[2][0] + "&nbsp;&lt;=");
        rep_cond.push(cond[1]);
        if (cond[2][1] != null)
            rep_cond.push("&lt;=&nbsp;" + cond[2][1]);
        return rep_cond.join(" ");
    }
    rep_var = (short_form)? "":cond[1];
    if (cond[0] == "enum") {
        op_mode = cond[2];
        sel_names = cond[3];
    } else {
        if (cond[0] == "zygosity") {
            op_mode = cond[3];
            sel_names = cond[4];
            rep_var = sZygosityH.getUnitTitle(cond[2], short_form);
        }
        else {
            return "???";
        }
    }
    var selection = [];
    for (j=0; j<sel_names.length; j++) {
        if (/^[A-Za-z0-9_]+$/u.test(sel_names[j]))
            selection.push(sel_names[j]);
        else
            selection.push('"' + sel_names[j] + '"');
    }
    selection = '{' + selection.join(', ') + '}';
    
    switch(op_mode) {
        case "NOT":
            rep_cond = rep_var + '&nbsp;not&nbsp;in&nbsp;' + selection;
            break;
        case "ONLY":
            rep_cond = rep_var + '&nbsp;in&nbsp;only(' + selection + ')';
            break;
        case "AND":
            rep_cond = rep_var + '&nbsp;in&nbsp;all(' + selection + ')';
            break;
        default:
            rep_cond = rep_var + '&nbsp;in&nbsp;' + selection;
    }
    if (short_form && rep_cond.length > 80)
        return rep_cond.substr(0, 77) + '...';
    return rep_cond
}

/*************************************/
function checkFilterAsIdent(filter_name) {
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

