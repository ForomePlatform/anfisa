var sCommonTitle = null;

function setup(common_title) {
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":DIR";
    ajaxCall("dirinfo", "", setupDirData);
}

function setupDirData(info) {
    document.getElementById("span-version").innerHTML = info["version"];
    var tab_cnt = ["<table>"];
    for (idx = 0; idx < info["workspaces"].length; idx++) {
        ws_info = info["workspaces"][idx];
        tab_cnt.push('<tr><td class="name"><a href="ws?ws=' + ws_info["name"] + '" ' +
            'target="' + sCommonTitle + ':' + ws_info["name"] + '">' +
            ws_info["name"] + '</td>');
        tab_cnt.push('<td class="note">' + ws_info["note"].replace('\n', '<br>') + 
            '</td></tr>');
    }
    if (info["xl-datasets"] && info["xl-datasets"].length > 0) {
        tab_cnt.push('<tr><td colspan="2"></td></tr>');
        for (idx = 0; idx < info["xl-datasets"].length; idx++) {
            ds_info = info["xl-datasets"][idx];
            tab_cnt.push('<tr><td class="name"><a href="xl_flt?ds=' + 
                ds_info["name"] + '" ' + 'target="' + sCommonTitle + ':' + 
                ds_info["name"] + '">' +
                ds_info["name"] + '</td>');
            tab_cnt.push('<td class="note">' + ds_info["note"].replace('\n', '<br>') + 
                '</td></tr>');
        }
    }
    tab_cnt.push("</table>");
    document.getElementById("div-main").innerHTML = tab_cnt.join('\n');
}
