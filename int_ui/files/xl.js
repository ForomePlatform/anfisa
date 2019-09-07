var sDSName = null;
var sCommonTitle = null;
var sWsURL = null;
var sAppModeRq = "";

/*************************************/
function setupXLFilters(ds_name, common_title, ws_url) {
    sWsURL = ws_url;
    sDSName = ds_name;
    sCommonTitle = common_title;
    window.name = sCommonTitle + ":" + sDSName;
    window.onresize  = arrangeControls;
    window.onkeydown  = onKey;
    document.getElementById("xl-name").innerHTML = sDSName;
    
    initXL();
    document.getElementById("close-filter").style.display = "none";
    sFiltersH.init();
    sUnitsH.init("xl_stat", "xl_statunits", "ds=" + sDSName, true);
    sUnitsH.setup();
}
    
/**************************************/
function wsCreate() {
    sCreateWsH.show();
}

function startWsCreate() {
    sCreateWsH.startIt();
}

/**************************************/
function onModalOff() {
}

function updateCurFilter(filter_name, force_it) {
}

function onFilterListChange() {
}

/*************************************/
function showExport() {
    relaxView();
    if (sUnitsH.mExportFormed) {
        sViewH.dropOn(document.getElementById("export-result"));
        return;
    }
    if (sUnitsH.mCount <= 300)
        res_content = 'Export ' + sUnitsH.mCount + ' variants?<br>' +
            '<button class="drop" onclick="doExport();">Export</button>' + 
            '&emsp;<button class="drop" onclick="relaxView();">Cancel</button>';
    else
        res_content = 'Too many variants for export: ' + 
            sUnitsH.mCount + ' > 300.<br>' +
            '<button class="drop" onclick="relaxView();">Cancel</button>';
    res_el = document.getElementById("export-result");
    res_el.innerHTML = res_content;
    sViewH.dropOn(res_el);
}

function doExport() {
    args = "ds=" + sDSName + "&conditions=" + 
        encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
    ajaxCall("xl_export", args, setupExport);
}

function setupExport(info) {
    res_el = document.getElementById("export-result");
    if (info["fname"]) {
        res_el.className = "drop";
        res_el.innerHTML = 'Exported ' + sUnitsH.mCount + ' variants<br>' +
        '<a href="' + info["fname"] + '" target="blank" ' + 'download>Download</a>';
    } else {
        res_el.className = "drop problems";
        res_el.innerHTML = 'Bad configuration';
    }
    sUnitsH.mExportFormed = true;
    showExport();
}

/*************************************/
/**************************************/
function arrangeControls() {
    sSubViewH.arrangeControls();
}

function onKey(event_key) {
    sSubViewH.onKey(event_key);
}
