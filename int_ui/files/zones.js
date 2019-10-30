var sWorkZoneDescr = null;
var sWorkZoneData  = null;
var sWorkZoneTitle = null;
var sZoneListCache = {};
var sZoneDictCache = {};
var sZoneSetCache  = {};
var sWorkZoneCur   = null;
var sZoneTagsIntVersion = null;

/*************************************/
function checkCurZoneStatus() {
    if (sWorkZoneDescr == null)
        return "not set";
    return null;
}

/*************************************/
function loadZone(zone_name){
    var args = "ws=" + sDSName + "&zone=" + zone_name;
    ajaxCall("zone_list", args, setupZone);
}

function setupZone(info) {
    zone_name = info["zone"];
    sWorkZoneCur = zone_name;
    var variants = info["variants"];
    sZoneListCache[zone_name] = [variants, info["title"]];
    sZoneDictCache[zone_name] = {};
    var sel_variants = sZoneSetCache[sWorkZoneCur];
    if (sel_variants == undefined)
        sel_variants = [];
    var new_sel = [];
    
    list_val_rep = [];
    for (j = 0; j < variants.length; j++) {
        val_name = variants[j];
        var check_mark = "";
        if (sel_variants.indexOf(val_name) >= 0) {
            new_sel.push(val_name);
            check_mark = "checked ";
        }
        sZoneDictCache[zone_name][val_name] = j;
        zone_ctrl_id = 'zn--' + zone_name + '-check--' + j;
        list_val_rep.push('<div class="zone-enum-val">' +
            '<input id="' + zone_ctrl_id + 
            '" type="checkbox" class="zn-check-val" ' + check_mark +
            'onchange="checkZoneCheck(\'' + zone_name + '\',' + 
            j + ');"/><label for="' + zone_ctrl_id + 
            '">&emsp;' + val_name + '</label></div>');
    }
    sZoneSetCache[sWorkZoneCur] = new_sel;
    document.getElementById("zn-div--" + zone_name).innerHTML =
        list_val_rep.join('\n');
    checkWorkZone(sWorkZoneCur);
}

/*************************************/
function checkWorkZone(zone_name) {
    if(zone_name && !sZoneListCache[zone_name]) {
        loadZone(zone_name);
        return;
    }
    sWorkZoneCur = zone_name;
    sWorkZoneTitle = (zone_name)? sZoneListCache[zone_name][1]:"";

    zone_check_id = "zn-check--" + zone_name;
    checkboxes = document.getElementsByClassName("zone-checkbox");
    for (i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = (checkboxes[i].id == zone_check_id);
    }
    
    zone_div_id = "zn-div--" + zone_name;
    divs = document.getElementsByClassName("work-zone-list");
    for (i = 0; i < divs.length; i++) {
        divs[i].style.display = (divs[i].id == zone_div_id)? "block":"none";
    }
    determineZoneData();
}

/*************************************/
function determineZoneData() {
    if (!sWorkZoneCur) {
        rep = ["<i>Define zone</i>"];
        sWorkZoneDescr = null;
        sWorkZoneData  = null;
    } else {
        rep = ["<i>Zone:</i> " + sWorkZoneCur + "<br/>"];
        variants = sZoneSetCache[sWorkZoneCur];
        if (variants == null || variants.length < 1) {
            rep.push("<i>Select a variant</i>");
            sWorkZoneDescr = null;            
        } else {
            sWorkZoneData = [sWorkZoneCur, variants];
            if (variants.length == 1) {
                sWorkZoneDescr = variants[0];
                rep.push("= <b>" + variants[0] + "</b>");
            } else {
                sWorkZoneDescr = variants[0] + 
                    " <i>+" + (variants.length - 1) + " more</i>";
                rep.push("<i>In:</i><br/>");
                for (j=0; j<variants.length; j++) {
                    inp_ctrl_id = "check-drop-" + j;
                    rep.push('<input type="checkbox" checked id="' + inp_ctrl_id + 
                        '" onclick="dropZoneVal(\'' + variants[j] + '\');"/>' +
                        '<label for="' + inp_ctrl_id + '">&emsp;' + variants[j] + 
                        '</label><br/>');
                }
            }
        }
    }
    el = document.getElementById("work-zone-def");
    el.innerHTML = rep.join('\n');
    updateCurZone(sWorkZoneData != null);
    document.getElementById("work-zone-clear").disabled = (sWorkZoneData == null);
}

/*************************************/
function checkZoneCheck(zone_name, zone_var_idx) {
    if (zone_name == sWorkZoneCur) {
        val_name = sZoneListCache[zone_name][0][zone_var_idx];
        if (sZoneSetCache[zone_name])
            idx = sZoneSetCache[zone_name].indexOf(val_name);
        else
            idx = -1;
        if (idx < 0) {
            if (!sZoneSetCache[zone_name]) {
                sZoneSetCache[zone_name] = [val_name];
            } else {
                sZoneSetCache[zone_name].push(val_name);
            }
        } else {
            if (sZoneSetCache[zone_name].length == 1)
                delete sZoneSetCache[zone_name];
            else
                sZoneSetCache[zone_name].splice(idx, 1);
        }
        el_id = 'zn--' + zone_name + '-check--' + zone_var_idx;
        document.getElementById(el_id).checked = (idx < 0);
        determineZoneData();
    }
}

function zoneClearSelect() {
    if (sWorkZoneCur) {
        delete sZoneSetCache[sWorkZoneCur];
        zone_check_id = 'zn--' + sWorkZoneCur + '-check--';
        checkboxes = document.getElementsByClassName("zn-check-val");
        for (i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].id.startsWith(zone_check_id))
                checkboxes[i].checked = false;
        }   
    }
    determineZoneData();
}

function dropZoneVal(val_name) {
    if (sZoneSetCache[sWorkZoneCur]) {
        idx = sZoneSetCache[sWorkZoneCur].indexOf(val_name);
        if (idx >= 0) {
            if (sZoneSetCache[sWorkZoneCur].length > 1)
                sZoneSetCache[sWorkZoneCur].splice(idx, 1);
            else
                delete sZoneSetCache[sWorkZoneCur];
        }
        idx = sZoneDictCache[sWorkZoneCur][val_name];
        if (idx != undefined) {
            el_id = 'zn--' + sWorkZoneCur + '-check--' + idx;
            document.getElementById(el_id).checked = false;
        }
        determineZoneData();
    }
}

function checkZoneTagsIntVersion(tags_int_version) {
    if (tags_int_version != sZoneTagsIntVersion) {
        if (sZoneListCache["_tags"]) {
            delete sZoneListCache["_tags"];
            loadZone("_tags");
        }
        sZoneTagsIntVersion = tags_int_version;
    }
}
