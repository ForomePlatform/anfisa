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

var sRulesData = null;
var sCurItem = null;
var sItemsContents = null;
var sCurItemNode = null;

var sNodeItemParam = null;

/*************************************/
function setupRulesCtrl() {
    if (sNodeItemParam != null)
        return;
    sNodeItemParam = document.getElementById("hi----param");
    loadRulesData();
}

/*************************************/
function loadRulesData() {
    var args = "ds=" + sDSName;
    //if (content)
    //  args += "&note=" + encodeURIComponent(content);
    ajaxCall("rules_data", args, setupRulesData);
}

function setupRulesData(info) {
    var col_rep = [];
    sItemsContents = {};
    columns = info["columns"];
    for (idx = 0; idx < columns.length; idx++) {
        col_name = columns[idx][0];
        sItemsContents[col_name] = columns[idx][1];
        col_rep.push('<div id="hi--' + col_name + '" class="rule-item" ' +
          'onclick="ruleItemSel(\'' + col_name + '\');">' + 
          col_name + '</div>');
    }
    sItemsContents["--param"] = info["params"];
    document.getElementById("rules-columns").innerHTML =
        col_rep.join('\n');
    sNodeItemParam.className = "rule-item";

    sCurItem = null;
    sCurItemNode = null;
    ruleItemSel("--param");
}

/*************************************/
function ruleItemSel(item) {
    if (sCurItem == item) 
        return;
    var new_it_el = document.getElementById("hi--" + item);
    if (new_it_el == null) 
        return;
    if (sCurItemNode != null) {
        sCurItemNode.className = sCurItemNode.className.replace(" cur", "");
    }
    sCurItem = item;
    sCurItemNode = new_it_el;
    sCurItemNode.className = sCurItemNode.className + " cur";
    ruleItemReset();
    document.getElementById("rule-item-reset").disabled = true;
    document.getElementById("rule-item-modify").disabled = true;
    document.getElementById("rule-item-content").disabled = (sCurItem != "--param");
    checkRuleContent();
}


/*************************************/
function checkRuleContent() {
    modified = false;
    if (sCurItem == "--param") {
        new_content = document.getElementById("rule-item-content").value;
        modified = (new_content != sItemsContents[sCurItem]);
    }
    document.getElementById("rule-item-reset").disabled = !modified;
    document.getElementById("rule-item-modify").disabled = !modified;
    return modified;
}

/*************************************/
function ruleItemModify() {
    if (!checkRuleContent())
        return;
    var new_content = document.getElementById("rule-item-content").value;
    var args = "ds=" + sDSName + 
        "&it=" + encodeURIComponent(sCurItem) + 
        "&cnt=" + encodeURIComponent(new_content);
    ajaxCall("rules_modify", args, setupItemChange);
}

function ruleItemReset() {
    document.getElementById("rule-item-content").value =
        sItemsContents[sCurItem];
    document.getElementById("rule-item-errors").innerHTML = "";
}

function setupItemChange(info) {
    if (info["status"] == "OK") {
        relaxView();
        updateCurFilter(sCurFilterName, true);
        sUnitsH.setup();
        loadRulesData();
    } else {
        document.getElementById("rule-item-errors").innerHTML =
            info["error"]; 
    }
}

/*************************************/
