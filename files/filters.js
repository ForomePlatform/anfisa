/*
# Unit functions
#  - setup(): setup div inner html
#  - update(data): setup values of contols 
#  - check(): criterium is good/bad/none 
#  
#=====================
# IntValueUnit
# FloatValueUnit
#   * min / max
#   * count, count_undef
#   Criterium: cr_min, cr_max, keep_undef
# StatusUnit
# PresenceUnit
# MultiStatusUnit
#   Static: list of values
#   * [counts]
#   Criterium: (set of no), OR/AND
#=====================*/

var sCurFilter = [];
var sFilterHistory = [sCurFilter];
var sCurStatList = null;
var sCurStatUnit = null;

/*************************************/
function setupStatList(stat_list) {
    sCurStatList = stat_list;
    var stat_rep = [];
    for (idx = 0; idx < stat_list.length; idx++) {
        unit_stat = stat_list[idx];
        unit_type = unit_stat[0];
        unit_name = unit_stat[1];
        stat_rep.push('<div id="stat--' + unit_name + '" class="stat-unit" ' +
          'onclick="selectStat(\'' + unit_name + '\');">');
        stat_rep.push('<span class="stat-unit-name">' + unit_name + '</span>');
        if (unit_type == "int" || unit_type == "float") {
            val_min   = unit_stat[2];
            val_max   = unit_stat[3];
            count     = unit_stat[4];
            cnt_undef = unit_stat[5];
            if (count == 0) {
                stat_rep.push('<span class="stat-bad">No data</span>');
            } else {
                if (val_min == val_max) {
                    stat_rep.push('<span class="stat-ok">' + val_min + '</span>');
                } else {
                    stat_rep.push('<span class="stat-ok">' + val_min + ' =< ...<= ' +
                        val_max + ' </span>');
                }
                stat_rep.push('<span class="stat-count">' + count + ' records</span>');
                if (cnt_undef > 0) 
                    stat_rep.push('<span class="stat-undef-count">+' + cnt_undef + 
                        ' undefined</span>');
            }
        } else {
            var_list = unit_stat[2];
            stat_rep.push('<ul>');
            for (j = 0; j < Math.min(4, var_list.length); j++) {
                var_name = var_list[j][0];
                var_count = var_list[j][1];
                stat_rep.push('<li><b>' + var_name + '</b>: <span class="count">' +
                    var_count + ' records</span></li>');
            }
            stat_rep.push('</ul>');
            if (var_list.length > 4) {
                stat_rep.push('<p>...and ' + (var_list.length - 4) + ' more...</p>');
            }
        }
        stat_rep.push('</div>')
    }
    document.getElementById("stat-list").innerHTML = stat_rep.join('\n');
    sCurStatUnit = null;
    selectStat(stat_list[0][1]);
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
}

/*************************************/
function checkCurCrit(){
}

/*************************************/
function filterAddCrit() {
}

function filterUpdateCrit() {
}

function filterDeleteCrit() {
}

function filterUndoCrit() {
}

function filterRedoCrit() {
}

function filterAddCrit() {
}

/*************************************/
