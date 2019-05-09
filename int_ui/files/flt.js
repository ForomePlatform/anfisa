/*************************************/
/* Utilities                         */
/*************************************/
function ajaxCall(rq_name, args, func_eval) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            func_eval(info);
        }
    };
    xhttp.open("POST", rq_name, true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(args); 
}

/**************************************/
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
            if (!short_form)
                rep_var = sZygosityH.getUnitTitle(cond[2]);
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

/*************************************/
function normFloatLongTail(val, to_up) {
    var ret = val.toString();
    var vv = ret.split('.');
    if (vv.length < 2 || vv[1].length < 6)
        return ret
    if (to_up)
        return (val + .000005).toFixed(5);
    return val.toFixed(5);
}

/*************************************/
function fillStatRepNum(unit_stat, list_stat_rep) {
    val_min   = unit_stat[2];
    val_max   = unit_stat[3];
    count     = unit_stat[4];
    //cnt_undef = unit_stat[5];
    if (count == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
    } else {
        if (val_min == val_max) {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                '</span>');
        } else {
            list_stat_rep.push('<span class="stat-ok">' + normFloatLongTail(val_min) + 
                ' =< ...<= ' + normFloatLongTail(val_max, true) + ' </span>');
        }
        list_stat_rep.push(': <span class="stat-count">' + count + 
            ' records</span>');
    }
}

function fillStatRepEnum(unit_stat, list_stat_rep, expand_mode) {
    var_list = unit_stat[2];
    list_count = 0;
    for (j = 0; j < var_list.length; j++) {
        if (var_list[j][1] > 0)
            list_count++;
    }
    if (list_count == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
        return;
    }
    needs_expand = list_count > 6 && expand_mode;
    if (expand_mode == 2) 
        view_count = list_count
    else
        view_count = (list_count > 6)? 3: list_count; 
        
    if (list_count > 6 && expand_mode) {
        unit_name = unit_stat[1]["name"];
        list_stat_rep.push('<div onclick="exposeEnum(\'' + unit_name + 
            '\',' + (3 - expand_mode) + ');" class="enum-exp">' + 
            ((expand_mode==1)?'+':'-') + '</div>');
    }
    list_stat_rep.push('<ul>');
    for (j = 0; j < var_list.length && view_count > 0; j++) {
        var_name = var_list[j][0];
        var_count = var_list[j][1];
        if (var_count == 0)
            continue;
        view_count -= 1;
        list_count--;
        list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
            '<span class="stat-count">' +
            var_count + ' records</span></li>');
    }
    list_stat_rep.push('</ul>');
    if (list_count > 0) {
        list_stat_rep.push('<p class="stat-comment">...and ' + 
            list_count + ' variants more...</p>');
    }
}

    

        
