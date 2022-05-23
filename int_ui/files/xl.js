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

/*************************************/
function setupXLFilters(ds_name, common_title, ws_pub_url) {
    sDSName = ds_name;
    sDSKind = "xl";
    sCommonTitle = common_title;
    sWsPubURL = ws_pub_url;
    window.name = sCommonTitle + ":" + sDSName;
    window.onresize  = arrangeControls;
    window.onkeydown  = onKey;
    document.getElementById("ds-name").innerHTML = sDSName;
    
    setupDSControls();
    document.getElementById("close-filter").style.display = "none";
    sFiltersH.init();
    sUnitsH.init("ds=" + sDSName, true);
    sUnitsH.setup();
}
    
/**************************************/
function updateCurFilter(filter_name, force_it) {
}

function onFilterListChange() {
}

/*************************************/
function doExport() {
    sViewH.popupOff();
    args = "ds=" + sDSName + "&conditions=" + 
        encodeURIComponent(JSON.stringify(sConditionsH.getConditions()));
    ajaxCall("export", args, setupExport);
}

function doCSVExport() {
    sViewH.popupOff();
    window.open("csv_export?" + "ds=" + sDSName + "&conditions=" + 
        encodeURIComponent(JSON.stringify(sConditionsH.getConditions())) + 
        "&schema=csv", "CSV export");
}

/*************************************/
/**************************************/
function arrangeControls() {
    sSubVRecH.arrangeControls();
    sOpEnumH.arrangeControls();
}

function onKey(event_key) {
    sSubVRecH.onKey(event_key);
}
