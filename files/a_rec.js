function chooseAspect(evt, aspect_id) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("r-tabcnt");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = (tabcontent[i].id == aspect_id)? "block":"none";
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

function init_r(first_tab) {
    if (!window.parent.sCurRecTab) 
            window.parent.sCurRecTab = first_tab;
    chooseAspect(null, window.parent.sCurRecTab);
}
