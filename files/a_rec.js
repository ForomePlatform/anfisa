function chooseAspect(evt, aspect_id) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("r-tabcnt");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.zIndex = (tabcontent[i].id == aspect_id)? "1":"0";
    }

    tablinks = document.getElementsByClassName("r-tablnk");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    tab_link_el = document.getElementById(aspect_id);
    window.parent.sCurRecTab = aspect_id;
    
    if (evt != null) {
        evt.currentTarget.className += " active";
    } else {
        document.getElementById("l" + aspect_id).className += " active";
    }
}

function init_r() {
    if (!window.parent.sCurRecTab) 
            window.parent.sCurRecTab = "a--main";
    chooseAspect(null, window.parent.sCurRecTab);
}