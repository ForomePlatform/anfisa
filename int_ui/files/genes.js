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
sDynPanelPrefix = '';
sDSName = null;
sPState = null;
sAllPanelNames = null;
sDynPanelNames = null;
sDBVersions = null;
sCurPanelName = null;
sCurSelMode = 0;
sCurPanelList = null;
sCurPanelListInDS = null;
sCurPatternList = null;
sCurPatternListInDS = null;
sCurSymbol = null;
sCurRefSymbol = null;

sCurDynSelMode = 0;
sCurDynPanelName = null;
sCurDynPanelList = null;
sCurDynPanelModListInDS = null;
sCurDynPanelModList = null;
sCurDynPanelToRemove = null;
sCurDynPanelChanged = false;
sCurDynAction = null;
sJoinList = null;
sTimeH = null;

function initGenesPage(ds_name, common_title){
    sDSName = ds_name;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName + ":GENES";
    window.onresize  = arrangeControls;
    //document.getElementById("ds-name").innerHTML = sDSName;
    ajaxCall("panels", "ds=" + sDSName + "&tp=Symbol", setupPanels);
    arrangeControls();
}

function resetPanels(instr) {
    ajaxCall("panels", "ds=" + sDSName + "&tp=Symbol" +
        '&instr=' + encodeURIComponent(JSON.stringify(instr)), setupPanels);
}

function arrangeControls() {
    all_w = document.getElementById("all").offsetWidth;
    all_h = document.getElementById("all").offsetHeight;
    
    document.getElementById("bottom").style.height = all_h - 115;
    document.getElementById("left").style.width = 180;
    document.getElementById("center").style.width = all_w - 370;
    document.getElementById("right").style.width = 180; 
    document.getElementById("symbol-info-wrap").style.height = all_h - 135; 
}

function setupPanels(info) {
    var panels = info["panels"];
    sAllPanelNames = [];
    sDynPanelNames = [];
    for (idx = 0; idx < panels.length; idx++) {
        if (panels[idx]["name"] == "__Symbol__")
            continue;
        sAllPanelNames.push(panels[idx]["name"]);
        if (!panels[idx]["standard"])
            sDynPanelNames.push(panels[idx]["name"]);
    }
    if (sDynPanelPrefix == '' && sDynPanelNames.length > 0)
        sDynPanelPrefix = sDynPanelNames[0][0];
    sPState     = info["panel-sol-version"];
    sDBVersions = info["db-version"];
    resetSelectInput(document.getElementById("panel-select"),
        sAllPanelNames, false, sCurPanelName);
    resetSelectInput(document.getElementById("dyn-panels-combo-list"),
        sDynPanelNames, false, sCurDynPanelName);
    
    document.getElementById("gene-versions").title = sDBVersions.join('\n');
    
    pickPanel();
    checkControls();
    checkSel(sCurSelMode, true);
    checkDynSel(sCurDynSelMode, true);
}

function checkSel(mode, force_it) {
    if (sCurSelMode == mode && !force_it)
        return false;
    sCurSelMode = mode;
    document.getElementById("sel-check-panel").checked = (sCurSelMode == 0);
    document.getElementById("sel-check-pattern").checked = (sCurSelMode == 1);
    renderList();
    return true;
}

function pickPanel() {
    checkSel(0);
    sCurPanelName = document.getElementById("panel-select").value;
    ajaxCall("symbols", "ds=" + sDSName + "&tp=Symbol&panel=" + 
        encodeURIComponent(sCurPanelName), setupList);
}

function pickPattern() {
    checkSel(1);
    pattern = document.getElementById("pattern-input").value;
    ajaxCall("symbols", "ds=" + sDSName + "&tp=Symbol&pattern=" +
        encodeURIComponent(pattern), setupList);
}

function setupList(info) {
    sCurSelMode = 1;
    if (info == null) {
        sCurPatternList = null;
        sCurPatternListInDS = null;
    } else {
        if (info["pattern"]) {
            sCurPatternList = info["all"];
            sCurPatternListInDS = info["in-ds"];
        } else {
            sCurSelMode = 0;
            sCurPanelList = info["all"];
            sCurPanelListInDS = info["in-ds"];
        }
        if (info["panel-sol-version"] !== undefined)
            sPState = info["panel-sol-version"];
    }
    renderList();
    checkControls();
}

function renderList() {
    if (sCurSelMode == 1) {
        cur_list = sCurPatternList;
        in_ds = sCurPatternListInDS;
    } else {
        cur_list = sCurPanelList;
        in_ds = sCurPanelListInDS;
    }
    var rep = [];
    if (cur_list == null && sCurSelMode == 1) {
        rep.push('<div class="note">Define more detailed pattern</div>');
    } else {
        if (cur_list) {
            for (idx = 0; idx < cur_list.length; idx++) {
                sym = cur_list[idx];
                sym_mode = (in_ds.indexOf(sym) >= 0)? " active":""; 
                rep.push('<div id="sym--' + sym + '" class="sym-ref' + sym_mode + '"' + 
                    ' onclick="selectGene(\'' + sym + '\', 0);">' + sym + '</div>');
            }
        }
    }
    document.getElementById("symbol-list").innerHTML = rep.join('\n');
    var cur_symbol = null;
    if (cur_list && cur_list.length > 0) {
        if (sCurSymbol && cur_list.indexOf(sCurSymbol) >= 0)
            cur_symbol = sCurSymbol;
        else
            cur_symbol = cur_list[0];
    }
    sCurSymbol = null;
    if (cur_symbol)
        selectGene(cur_symbol, 0);
}

sSymPrefixes = ["sym--", "dynsym--"];
function renderSym(sym, cur_mode) {
    for (idx = 0; idx < sSymPrefixes.length; idx++) {
        el = document.getElementById(sSymPrefixes[idx] + sym);
        if (el) {
            if (cur_mode) {
                el.className = pushKeyToStr(el.className, 'cur');
                softScroll(el);
            } else {
                el.className = popKeyFromStr(el.className, 'cur');
            }
        }
    }
}

function selectGene(sym, info_frame) {
    if (!sym) {
        if (info_frame == 0)
            setupSymInfo(null);
        else
            setupSymInfoRef(null);
    } else {
        ajaxCall("symbol_info", "ds=" + sDSName + "&tp=Symbol&symbol=" + sym, 
            (info_frame == 0)? setupSymInfo:setupSymInfoRef);
    }
}

function setupSymInfo(info) { 
    i_el = document.getElementById('symbol-info');
    i_el.innerHTML = renderSymInfo(info, true);
    i_el.scrollTop = 0;
    if (sCurSymbol)
        renderSym(sCurSymbol, false);
    sCurSymbol = symFromInfo(info);
    if (sCurSymbol)
        renderSym(sCurSymbol, true);    
    checkControls();
    selectGene(refSymFromInfo(info), 1);
}

function setupSymInfoRef(info) { 
    if (info == null) {
        document.getElementById('symbol-ref-info').innerHTML = "";
        document.getElementById('symbol-ref-ctrl').style.visibility = 
            "hidden";
        sCurRefSymbol = null;
        return;
    }
    i_el = document.getElementById('symbol-ref-info');
    i_el.innerHTML = renderSymInfo(info, false);
    i_el.scrollTop = 0;
    sCurRefSymbol = symFromInfo(info);
    document.getElementById("symbol-ref-ctrl").style.visibility = "visible";
    checkControls();
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

function symFromInfo(info) {
    if (info != null && info["gtf"]) {
        return info["_id"];
    }
    return null;
}

function refSymFromInfo(info) {
    if (info == null || info["gtf"])
        return null;
    if (info["gtf-refs"]) {
        var base_sym = info["_id"];
        for(j=0; j < info["gtf-refs"].length; j++) {
            var sym = info["gtf-refs"][j];
            if (sym != base_sym) 
                return sym;
        }
    }
    return null;
}

function renderSymInfo(info, with_ref) {
    rep = ['<table class="sym-tab">',
        '<tr><td class="title">Symbol</td><td>' 
            + info["_id"] + '</td></tr>'];
    if (info["gtf-refs"]) {
        rep.push('<tr><td class="title">aliases</td><td>');
        if (with_ref) {
            base_sym = symFromInfo(info);
        }        
        for(j=0; j < info["gtf-refs"].length; j++) {
            sym = info["gtf-refs"][j];
            if (with_ref && sym != base_sym) {
                rep.push('<span class="sym-act-ref" onclick="selectGene(\'' + 
                    sym + '\', 1);">' + sym + '</span>');
            } else {
                rep.push(sym);
            }
        }
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
    return rep.join('\n');
}

function renderDynSelMode() {
    document.getElementById("sel-check-dyn-active").checked = 
        (sCurDynSelMode == 0);
    document.getElementById("sel-check-dyn-panel").checked = 
        (sCurDynSelMode == 1);
    document.getElementById('sel-active-dyn').className = 
        (sCurDynSelMode == 0)? "hit":"";
}

function checkDynSel(mode, force_it) {
    sCurDynSelMode = mode;
    renderDynSelMode();
    if (sCurDynSelMode == 0) {
        dyn_panel = "__Symbol__";
    } else {
        dyn_panel = document.getElementById("dyn-panels-combo-list").value;
    }
    if (dyn_panel != sCurDynPanelName || force_it) {
        if (!dyn_panel) {
            setupDynPanel(null);
        } else {
            ajaxCall("symbols", "ds=" + sDSName + 
                "&tp=Symbol&panel=" + encodeURIComponent(dyn_panel), 
                setupDynPanel);
        }
    }
    return true;
}

function setupDynPanel(info) {
    if (info == null) {
        sCurDynPanelName = "__Symbol__";
        sCurDynPanelList = [];
        sCurDynPanelModListInDS = [];
    } else {
        sCurDynPanelName = info["panel"];
        sCurDynPanelList = info["all"];
        sCurDynPanelModListInDS = info["in-ds"];
        if (info["panel-sol-version"] && sPState != info["panel-sol-version"])
            setupPanels();
    }
    sCurDynPanelModList  = [];
    for (idx = 0; idx < sCurDynPanelList.length; idx++) {
        pushKey(sCurDynPanelModList, sCurDynPanelList[idx]);
    }
    sCurDynPanelChanged = false;
    if (sJoinList != null) {
        for (idx = 0; idx < sJoinList.length; idx++) {
            pushKey(sCurDynPanelModList, sJoinList[idx]);
            sCurDynPanelModList.sort()
            sCurDynPanelChanged = true;
        }
        sJoinList = null;
    }
    sCurDynPanelToRemove = [];
    sCurDynAction = null;
    renderDynList();
    checkControls();
}

function renderDynList() {
    var rep = [];
    for (idx = 0; idx < sCurDynPanelModList.length; idx++) {
        sym = sCurDynPanelModList[idx];
        sym_mode = (sCurDynPanelModListInDS.indexOf(sym) >= 0)? " active":"";
        q_checked = "checked";
        if (sCurDynPanelToRemove.indexOf(sym) >= 0) {
            sym_mode += " remove";
            q_checked = "";
        }
        if (sCurDynPanelList.indexOf(sym) < 0)
            sym_mode += " new";
        rep.push('<div id="dynsym--' + sym + 
            '" class="sym-ref' + sym_mode + '"' + 
            ' onclick="selectGene(\'' + sym + '\', 0);">' +
            '<input id="dyn-sym-check--' + sym + 
            '" type="checkbox" ' + q_checked +
            ' onchange="switchDynSym(\'' + sym + 
            '\');"/>' + sym + '</div>');
    }
    document.getElementById("dyn-symbol-list").innerHTML = rep.join('\n');
}

function checkControls() {
    document.getElementById('symbol-add-button').disabled = 
        (sCurSymbol == null || sCurDynPanelModList == null ||
            sCurDynPanelModList.indexOf(sCurSymbol) >= 0);
    document.getElementById('symbol-ref-add-button').disabled =
        (sCurRefSymbol == null || sCurDynPanelModList == null ||
            sCurDynPanelModList.indexOf(sCurRefSymbol) >= 0);
 
    document.getElementById('sel-check-dyn-active').disabled = sCurDynPanelChanged;
    document.getElementById('sel-check-dyn-panel').disabled = sCurDynPanelChanged;
    document.getElementById('dyn-panels-op-list').disabled = sCurDynPanelChanged;
    document.getElementById('dyn-panels-op-new').disabled = sCurDynPanelChanged;
    
    document.getElementById('dyn-panels-op-drop').disabled = 
        (sCurDynPanelName != "?" && !sCurDynPanelChanged);
    document.getElementById('dyn-panels-op-save').disabled = 
        (sCurDynPanelName == "?" || !sCurDynPanelChanged);
    document.getElementById('dyn-panels-op-save-as').className = 
        (sCurDynPanelName != "?" &&
        (sCurDynPanelChanged || (sCurDynPanelModList &&
        (sCurDynPanelModList.length - sCurDynPanelToRemove.length) > 0)))? 
        "popup": "disabled";
    document.getElementById('dyn-panels-op-delete').className = 
        ((sCurDynPanelName == "__Symbol__" || sCurDynPanelName == "?") &&
            sCurDynPanelList.length == 0 && sCurDynPanelModList.length == 0)?
            "disabled":"popup";
    document.getElementById('dyn-panels-op-join').className = 
        (sCurDynPanelName != "__Symbol__" && sCurDynPanelModList &&
            (sCurDynPanelModList.length - sCurDynPanelToRemove.length) > 0)? 
            "popup":"disabled";
        
    var el_op_act = document.getElementById('dyn-panels-op-act');
    el_op_act.disabled = sCurDynAction && 
        (sCurDynAction != "SaveAs" || dynPanelCheckName()) &&
        ((sCurDynPanelModList.length - sCurDynPanelToRemove.length) < 1);
    el_op_act.style.visibility = (sCurDynAction)? "visible":"hidden";

    document.getElementById('dyn-panels-name-input').style.visibility = 
        (sCurDynAction == "SaveAs")? "visible":"hidden";
    
}

function addSymbol(info_frame) {
    cur_symbol = (info_frame == 0)? sCurSymbol:sCurRefSymbol;
    if (!cur_symbol || sCurDynPanelModList.indexOf(cur_symbol) >= 0)
        return;
    sCurDynPanelModList.push(cur_symbol);
    sCurDynPanelModList.sort();
    sCurDynPanelChanged = true;
    selectGene(cur_symbol, 0);
    ajaxCall("symbols", "ds=" + sDSName + "&tp=Symbol&list=" + 
        encodeURIComponent(JSON.stringify(sCurDynPanelModList)), setupDynList);
}

function switchDynSym(symbol) {
    check_el = document.getElementById('dyn-sym-check--' + symbol);
    sym_el = document.getElementById('dynsym--' + symbol);
    if (check_el.checked) {
        popKey(sCurDynPanelToRemove, symbol);
        sym_el.className = popKeyFromStr(sym_el.className, 'remove');
    } else {
        pushKey(sCurDynPanelToRemove, symbol);
        sym_el.className = pushKeyToStr(sym_el.className, 'remove');
    }    
    sCurDynPanelChanged = true;
    selectGene(symbol, 0);
    checkControls();
}

function setupDynList(info) {
    sCurDynPanelModListInDS = info["in-ds"];
    renderDynList();
    selectGene(sCurSymbol, 0);
}

function dynPanelDrop() {
    checkDynSel(sCurDynSelMode, true);
}

function startDynPanelDelete() {
    sCurDynAction = "Delete";
    document.getElementById("dyn-panels-op-act").innerHTML = "Delete";
    checkControls();
}

function fixModList() {
    idx = sCurDynPanelModList.length - 1;
    while (idx >= 0) {
        if (sCurDynPanelToRemove.indexOf(sCurDynPanelModList[idx]) >= 0) 
            sCurDynPanelModList.splice(idx, 1);
        else
            idx--;
    }
    sCurDynPanelToRemove = [];
}

function dynPanelSave() {
    fixModList();
    ajaxCall("solutions", "ds=" + sDSName + "&entry=" + sCurDynPanelName, doUpdatePanel);
}

function doUpdatePanel(info) {
    if (info === null || info == "panel.Symbol") {
        resetPanels(["UPDATE", sCurDynPanelName, sCurDynPanelModList]);
        return;
    }
    alert("Solution name duplication: " + info);
    document.getElementById('dyn-panels-name-input').className = "bad";
}
function startDynPanelSaveAs() {
    sCurDynAction = "SaveAs";
    document.getElementById("dyn-panels-op-act").innerHTML = "Save as new";
    checkControls();
    dynPanelCheckName();
}

function startDynPanelNew() {
    setupDynPanel({"panel": "?", "all": [], "in-ds": []});
    sCurDynSelMode = 1;
    renderDynSelMode();
    sCurDynAction = "SaveAs";
    document.getElementById("dyn-panels-op-act").innerHTML = "Save new panel";
    checkControls();
    dynPanelCheckName();
}

function dynPanelCheckName() {
    if (sCurDynAction != "SaveAs")
        return;
    inp_el = document.getElementById('dyn-panels-name-input');
    new_name = inp_el.value;
    if (!checkIdentifier(new_name)) {
        new_name = null;
    } else {
        new_name = sDynPanelPrefix + new_name;
        if (sDynPanelNames.indexOf(new_name) >= 0)
            new_name = null;
    }
    inp_el.className = (new_name)? "": "bad";
    if (sTimeH == null) 
        sTimeH = setInterval(dynPanelCheckName, 100);
    return new_name;
}

function dynPanelJoin() {
    if (sCurDynPanelName != "__Symbol__") {
        fixModList();
        sJoinList = sCurDynPanelModList;
        checkDynSel(0, true);
    }
}

function dynPanelAct() {
    if (sCurDynAction == "Delete") {
        if (sCurDynPanelName != "__Symbol__") {
            resetPanels(["DELETE", sCurDynPanelName]);
            sCurDynSelMode = 0;
        } else {
            sCurDynPanelModList = [];
            sCurDynPanelToRemove = [];
            sCurDynSelMode = 0;
            dynPanelSave();
        }
        return;
    }
    if (sCurDynAction == "SaveAs") {
        new_name = dynPanelCheckName();
        if (new_name) {
            sCurDynPanelName = new_name;
            sCurDynSelMode = 1;
            dynPanelSave();
        }
        return;
    }
}

