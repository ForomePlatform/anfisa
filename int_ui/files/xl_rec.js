var sBaseAspect = null;
var sAloneRecID = null;
var sStarted = null;
var sCurTabEl = null;

function init_r(init_aspect, ws_name, rec_id) {
    sBaseAspect = init_aspect;
    if (window.parent.sViewH.mSubViewTab == null)
        window.parent.sViewH.mSubViewTab = sBaseAspect;
    else
        sBaseAspect = window.parent.sViewH.mSubViewTab;
    sAloneRecID = rec_id;
    sStarted = true;
    window.onclick = onClick;
    pickAspect(sBaseAspect);
}

function onClick(event_ms) {
    window.parent.sViewH.onclick(event_ms);
}

function pickAspect(aspect_id) {
    window.parent.sViewH.mSubViewTab = aspect_id;
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