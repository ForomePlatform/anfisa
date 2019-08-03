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
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupRulesData(info);
        }
    };
    xhttp.open("POST", "rules_data", true);
    xhttp.setRequestHeader("Content-type", 
        "application/x-www-form-urlencoded");
    xhttp.send("ws=" + sWorkspaceName + sAppModeRq); 
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
    new_content = document.getElementById("rule-item-content").value;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var info = JSON.parse(this.responseText);
            setupItemChange(info);
        }
    };
    xhttp.open("POST", "rules_modify", true);
    xhttp.setRequestHeader("Content-type", 
        "application/x-www-form-urlencoded");
    xhttp.send("ws=" + sWorkspaceName + sAppModeRq +
        "&it=" + encodeURIComponent(sCurItem) + 
        "&cnt=" + encodeURIComponent(new_content));
}

function ruleItemReset() {
    document.getElementById("rule-item-content").value =
        sItemsContents[sCurItem];
    document.getElementById("rule-item-errors").innerHTML = "";
}

function setupItemChange(info) {
    if (info["status"] == "OK") {
        rulesModOff();
        updateCurFilter(sCurFilterName, true);
        loadStat();
        loadRulesData();
    } else {
        document.getElementById("rule-item-errors").innerHTML =
            info["error"]; 
    }
}

/*************************************/
