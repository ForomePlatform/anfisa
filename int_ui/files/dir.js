var sTitlePrefix = null;

function setup() {
    if (sTitlePrefix == null) 
        sTitlePrefix = window.document.title;
    window.name = sTitlePrefix + ":dir";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupData(info);
        }
    };
    xhttp.open("POST", "dirinfo", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(""); 
}

function setupData(info) {
    document.getElementById("span-version").innerHTML = info["version"];
    var tab_cnt = ["<table>"];
    for (idx = 0; idx < info["workspaces"].length; idx++) {
        ws_info = info["workspaces"][idx];
        tab_cnt.push('<tr><td class="name"><a href="ws?ws=' + ws_info["name"] + '" ' +
            'target="' + sTitlePrefix + '/' + ws_info["name"] + '">' +
            ws_info["name"] + '</td>');
        tab_cnt.push('<td class="note">' + ws_info["note"].replace('\n', '<br>') + 
            '</td></tr>');
    }
    tab_cnt.push("</table>");
    document.getElementById("div-main").innerHTML = tab_cnt.join('\n');
}
