var sStarted = null;
var sViewPort = null;
var sCurTabEl = null;
var sBlockedTabEl = null;
var sBaseAspect = null;

function pickAspect(aspect_id) {
    if (sBlockedTabEl != null && sBlockedTabEl.id == "la--" + aspect_id)
        return;
    window.parent.sTabPortData[sViewPort] = aspect_id;
    window.parent.updateTabCfg();
}

function tabCfgChange() {
    tab_port_data = window.parent.sTabPortData;
    tab_port_data[0] = !tab_port_data[0];
    window.parent.updateTabCfg();
}

function resetTabPort() {
    window.parent.sTabPortData[sViewPort] = sBaseAspect;
}

function updateCfg(reset_port) {
    var tab_port_data = window.parent.sTabPortData;
    if (sViewPort == null || tab_port_data[sViewPort] == null)
        return;
    document.getElementById("img-tab2").src = 
        tab_port_data[0]? "images/tab2-exp.png": "images/tab2-col.png";
    
    var cur_cnt_id = "a--" + tab_port_data[sViewPort];
    cnt = 0;
    tabcontent = document.getElementsByClassName("r-tabcnt");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = 
            (tabcontent[i].id == cur_cnt_id)? "block":"none";
        if (tabcontent[i].id == cur_cnt_id) 
            cnt += 1;
    }
    if (sBlockedTabEl != null && (!tab_port_data[0] ||
            sBlockedTabEl.id != "la--" + tab_port_data[3 - sViewPort])) {
        sBlockedTabEl.disabled = false;
        sBlockedTabEl = null;
    }
    var cur_tab_id = "la--" + tab_port_data[sViewPort];
    if (sCurTabEl == null || sCurTabEl.id != cur_tab_id) {  
        if (sCurTabEl != null) 
            sCurTabEl.className = sCurTabEl.className.replace(" active", "");
        sCurTabEl = document.getElementById(cur_tab_id);
        sCurTabEl.className += " active";
    }
    if (sBlockedTabEl == null && tab_port_data[0] && 
            tab_port_data[1] != tab_port_data[2] &&
            tab_port_data[3 - sViewPort] != null) {
        sBlockedTabEl = document.getElementById(
            "la--" + tab_port_data[3 - sViewPort]);
        sBlockedTabEl.disabled = true;
    }        
}

function init_r(port, init_aspect, rec_no) {
    sViewPort = port;
    sBaseAspect = init_aspect;
    tab_port_data = window.parent.sTabPortData;
    if ( tab_port_data[sViewPort] == null ) {
        tab_port_data[sViewPort] = init_aspect;
    }
    initTagsEnv();
    sStarted = true;
    window.parent.updateTabCfg();
}

