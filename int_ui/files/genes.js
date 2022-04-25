/*
 * Copyright (c) 2019. Partners HealthCare and other members of
 * Forome Association
 *
 * Developed by Sergey Trifonov based on contributions by Joel Krier,
 * Michael Bouzinier, Shamil Sunyaev and other members of Division of
 * Genetics, Brigham and Women's Hospital
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

sCommonTitle = null;
sDSName = null;
sPState = null;
sPanelNames = null;
sCurPanel = null;
sCurList = null;
sCurListInDS = null;
sCurSelMode = null;
sCurSymbol = null;

function initGenesPage(ds_name, common_title){
    sDSName = ds_name;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName + ":DOC";
    window.onresize  = arrangeControls;
    //document.getElementById("ds-name").innerHTML = sDSName;
    ajaxCall("panels", "ds=" + sDSName + "&tp=Symbol", setupPanels);
    arrangeControls();
}

function arrangeControls() {
    document.getElementById("right").style.width = 
        document.getElementById("all").style.width - 425;
    document.getElementById("symbol-info").style.height = 
        document.getElementById("all").style.height - 55;
}

function setupPanels(info) {
    sPanelNames = info["panels"];
    sPState     = info["state"];
    sel_el = document.getElementById("panel-select");
    for (idx = sel_el.length - 1; idx >= 0; idx--) {
        sel_el.remove(idx);
    }
    for (idx = 0; idx < sPanelNames.length; idx++) {
        pname = sPanelNames[idx];
        var option = document.createElement('option');
        option.innerHTML = pname;
        option.value = pname;
        sel_el.append(option)
    }
    if (sPanelNames.indexOf(sCurPanel) < 0) 
        sCurPanel = sPanelNames[0];
    sel_el.selectedIndex = sPanelNames.indexOf(sCurPanel);
        
    sCurSelMode = null;
    checkSel(0);
}

function checkSel(mode) {
    if (sCurSelMode == mode)
        return false;
    sCurSelMode = mode;
    document.getElementById("sel-check-panel").checked = (sCurSelMode == 0);
    document.getElementById("sel-check-pattern").checked = (sCurSelMode == 1);
    if (sCurSelMode == 0) 
        pickPanel();
    else
        pickPattern();
    return true;
}

function pickPanel() {
    if (checkSel(0)) {
        return;
    }
    sCurPanel = document.getElementById("panel-select").value;
    ajaxCall("symbols", "ds=" + sDSName + "&tp=Symbol&panel=" + sCurPanel, setupList);
}

function pickPattern() {
    if (checkSel(1)) {
        return;
    }
    pattern = document.getElementById("pattern-input").value;
    ajaxCall("symbols", "ds=" + sDSName + "&tp=Symbol&pattern=" +
        encodeURIComponent(pattern), setupList);
}

function setupList(info) {
    var rep = [];
    if (info == null) {
        sCurList = null;
        sCurListInDS = null;
        rep.push('<div class="note">Define more detailed pattern</div>');
    } else {
        sCurList = info["all"];
        sCurListInDS = info["in-ds"];
        if (info["state"] !== undefined)
            sPState = info["state"];
        if (sCurList) {
            for (idx = 0; idx < sCurList.length; idx++) {
                sym = sCurList[idx];
                sym_mode = (sCurListInDS.indexOf(sym) >= 0)? " active":""; 
                rep.push('<div id="sym--' + sym + '" class="sym-ref' + sym_mode + '"' + 
                    ' onclick="selectGene(\'' + sym + '\');">' + sym + '</div>');
            }
        }
    }
    document.getElementById("symbol-list").innerHTML = rep.join('\n');
    var cur_symbol = null;
    if (sCurList && sCurList.length > 0) {
        if (sCurSymbol && sCurList.indexOf(sCurSymbol) >= 0)
            cur_symbol = sCurSymbol;
        else
            cur_symbol = sCurList[0];
    }
    sCurSymbol = null;
    if (cur_symbol)
        selectGene(cur_symbol);
}

function renderSym(sym, cur_mode) {
    el = document.getElementById('sym--' + sym);
    cl_names = el.className.split(' ');
    if (cur_mode && cl_names[cl_names.length - 1] != "cur") {
        cl_names.push("cur");
    }
    if (!cur_mode && cl_names[cl_names.length - 1] == "cur")
        cl_names.pop()
    el.className = cl_names.join(' ');
}

function selectGene(sym) {
    if (sCurSymbol)
        renderSym(sCurSymbol, false);
    sCurSymbol = sym;
    renderSym(sCurSymbol, true);
    ajaxCall("gene_info", "symbol=" + sCurSymbol, setupSymInfo);
}

function renderValues(dict_values, rep) {
    keys = Object.keys(dict_values);
    keys.sort();
    rep.push('<table class="data-keys">');
    for (j=0; j< keys.length; j++) {
        val = dict_values[keys[j]];
        if (Array.isArray(val))
            val = val.join(" ");
        rep.push('<tr><td class="key">' + keys[j] + 
            '</td><td class="val">' + val + '</td></tr>');
    }
    rep.push('</table>');
}

function setupSymInfo(info) {
    rep = ['<table class="sym-tab">',
        '<tr><td class="title">Symbol</td><td>' 
            + info["_id"] + '</td></tr>'];
    if (info["gtf-refs"]) {
        rep.push('<tr><td class="title">aliases</td><td>');
        for(j=0; j < info["gtf-refs"].length; j++)
            rep.push(info["gtf-refs"][j]);
        rep.push('</td></tr>');
    }
    if (info["hgnc"]) {
        rep.push('<tr><td class="title">HGNC</td><td>');
        renderValues(info["hgnc"], rep);
    }
    if (info["gtf"]) {
        rep.push('<tr><td class="title" rowspan=' + info["gtf"].length + 
            '>Ensembl</td>');
        for (idx = 0; idx < info["gtf"].length; idx++) {
            rep.push((idx>0)?'<tr><td>':'<td>');
            renderValues(info["gtf"][idx], rep);
            rep.push('</td></tr>');
        }
    }
    document.getElementById('symbol-info').innerHTML = rep.join('\n');
}
