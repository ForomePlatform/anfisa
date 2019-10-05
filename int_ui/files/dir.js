var sCommonTitle = null;
var sWsExtUrl = null;

function setup(common_title, ws_ext_url) {
    sCommonTitle = common_title;
    sWsExtUrl = ws_ext_url;
    window.name = sCommonTitle + ":DIR";
    ajaxCall("dirinfo", "", setupDirData);
}

function setupDirData(info) {
    document.getElementById("span-version").innerHTML = info["version"];
    var tab_cnt = ["<table>"];
    for (idx = 0; idx < info["workspaces"].length; idx++) {
        renderWS(info["workspaces"][idx], tab_cnt);
    }
    if (info["xl-datasets"] && info["xl-datasets"].length > 0) {
        tab_cnt.push('<tr><td colspan="2"></td></tr>');
        for (idx = 0; idx < info["xl-datasets"].length; idx++) {
            renderXL(info["xl-datasets"][idx], tab_cnt);
        }
    }
    tab_cnt.push("</table>");
    document.getElementById("div-main").innerHTML = tab_cnt.join('\n');
}


function renderWS(ds_info, tab_cnt) {
    tab_cnt.push('<tr><td class="name">')
    if (sWsExtUrl) 
        tab_cnt.push('<a class="ext-ref" href="' + sWsExtUrl + 
            '?ws=' + ds_info["name"] + '" target="_blank" ' +
            'title="To front end">&#x23f5;</a>')
    tab_cnt.push(reprRef(ds_info["name"], "WS"));
    if (ds_info["doc"] != undefined)
        tab_cnt.push(reprRef(ds_info["name"], "DOC", "[doc]"));
     if (ds_info["base"]) {
        tab_cnt.push('<span class="ref-support">');
        tab_cnt.push('<br>&emsp;&lt;-&nbsp;' + reprRefSec(ds_info["base"], "XL"));
        tab_cnt.push('</span>');
     }
    if (ds_info["doc"] != undefined)
        
    tab_cnt.push('</td>')
    tab_cnt.push('<td class="note">' + ds_info["note"].replace('\n', '<br>') + 
        '</td></tr>');
}

function renderXL(ds_info, tab_cnt) {
    tab_cnt.push('<tr><td class="name">' + reprRef(ds_info["name"], "XL"));
    tab_cnt.push('<span class="ref-support">');
    if (ds_info["doc"] != undefined) 
        tab_cnt.push(reprRef(ds_info["name"], "DOC", "[doc]"));
    tab_cnt.push(reprRef(ds_info["name"], "TREE", "[tree]"));
    tab_cnt.push('</span>');
    if (ds_info["secondary"]) {
        for (var idx = 0; idx < ds_info["secondary"].length; idx++) {
            tab_cnt.push('<br>&emsp;-&gt;&nbsp;' + 
                reprRefSec(ds_info["secondary"][idx], "WS"));
        }
    }
    tab_cnt.push('</td>')
    tab_cnt.push('<td class="note">' + ds_info["note"].replace('\n', '<br>') + 
        '</td></tr>');
}

function reprRef(ds_name, mode, label) {
    ret = '<span class="ds-ref" onclick="goToPage(\'' + mode + '\', \'' + 
        ds_name + '\')">' + ((label)? label: ds_name) + '</span>';
    return ret;
}

function reprRefSec(ds_name, mode, label) {
    ret = '<span class="ds-ref-sec" onclick="goToPage(\'' + mode + '\', \'' + 
        ds_name + '\')">' + ((label)? label: ds_name) + '</span>';
    return ret;
}

function onModalOff() {
}

function arrangeControls() {
}