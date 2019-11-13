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

var sBaseAspect = null;
var sAloneRecID = null;
var sStarted = null;
var sCurTabEl = null;

function init_r(init_aspect, ws_name, rec_id) {
    sBaseAspect = init_aspect;
    if (window.parent.sSubViewCurAspect == null)
        window.parent.sSubViewCurAspect = sBaseAspect;
    else
        sBaseAspect = window.parent.sSubViewCurAspect;
    sAloneRecID = rec_id;
    sStarted = true;
    window.onclick = onClick;
    pickAspect(sBaseAspect);
}

function onClick(event_ms) {
    window.parent.sViewH.onclick(event_ms);
}

function pickAspect(aspect_id) {
    window.parent.sSubViewCurAspect = aspect_id;
    var cur_cnt_id = "a--" + aspect_id;
    tabcontent = document.getElementsByClassName("r-tabcnt");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].className = 
            (tabcontent[i].id == cur_cnt_id)? "r-tabcnt active":"r-tabcnt";
    }
    var cur_tab_id = "la--" + aspect_id;
    if (sCurTabEl == null || sCurTabEl.id != cur_tab_id) {  
        if (sCurTabEl != null) 
            sCurTabEl.className = sCurTabEl.className.replace(" active", "");
        sCurTabEl = document.getElementById(cur_tab_id);
        sCurTabEl.className += " active";
    }
}

function tabCfgChange(q) {
}