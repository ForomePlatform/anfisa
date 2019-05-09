/**************************************/
var sCreateWsH = {
    mStage: null,
    mDSNames: null,
    mSpanModTitle: null,
    mInputModName: null,
    mDivModProblems: null,
    mDivModStatus: null,
    mButtonModStart: null,
    mButtonModCancel: null,
    mTaskId: null,
    mTimeH: null,
    
    init: function() {
        this.mSpanModTitle = document.getElementById("create-ws-title");
        this.mInputModName = document.getElementById("create-ws-name");
        this.mDivModProblems = document.getElementById("create-ws-problems");
        this.mDivModStatus = document.getElementById("create-ws-status");
        this.mButtonModStart = document.getElementById("create-ws-start");
        this.mButtonModCancel = document.getElementById("create-ws-cancel");
    },
    
    show: function() {
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mDSNames = null;
        this.mTaskId = null;
        
        var info = sUnitsH.prepareWsCreate();
        if (info == null) 
            return;
        
        this.mSpanModTitle.innerHTML = 'Create workspace for ' +
            info[0] + ' of ' + info[1];
        var err_msg = "";
        if (info[0] >= 5000)
            err_msg = "Too many records, try to reduce";
        if (info[0] < 1)
            err_msg = "Empty set";
        this.mDivModProblems.innerHTML = err_msg;
        if (err_msg) {
            this.mStage = "BAD";
            this.checkControls();
            sViewH.modalOn(document.getElementById("create-ws-back"));
            return;
        }
        this.mStage = "NAMES";
        ajaxCall("dirinfo", "", function(info) {
            sCreateWsH._setupName(info);})
    },
    
    _nameReserved: function(dsname) {
        return this.mDSNames.indexOf(dsname) >= 0;
    },
    
    _setupName: function(dirinfo) {
        this.mDSNames = dirinfo["reserved"];
        var no = 1;
        var own_name = sDSName.match(/\_(.*)$/)[1];
        var ws_name;
        while (true) {
            ws_name = "ws" + no + '_' + own_name;
            if (!this._nameReserved(ws_name))
                break;
            no += 1;
        }
        this.mInputModName.value = ws_name;
        this.mStage = "READY";
        this.checkControls();
        sViewH.modalOn(document.getElementById("create-ws-back"));
    },
    
    checkControls: function() {
        if (this.mStage == "BAD")
            this.mInputModName.value = "";
        this.mInputModName.disabled = (this.mStage != "READY");
        err_msg = "";
        if (this.mStage == "READY") {
            if (this._nameReserved(this.mInputModName.value)) 
                err_msg = "Name is reserved, try another one";
            this.mDivModProblems.innerHTML = err_msg;
        }
        this.mButtonModStart.disabled = (this.mStage != "READY" || err_msg);
        if (this.mStage == "BAD" || this.mStage == "READY") {
            this.mDivModProblems.style.display = "block";
            this.mDivModStatus.style.display = "none";
            this.mDivModStatus.innerHTML = "";
        } else {
            this.mDivModProblems.style.display = "none";
            this.mDivModStatus.style.display = "block";
        }
        this.mButtonModCancel.disabled = (this.mStage == "WAIT");
    },
    
    startIt: function() {
        if (this.mStage != "READY")
            return;
         this.checkControls();
        if (this.mButtonModStart.disabled)
            return;
        sViewH.blockModal(true);
        this.mStage = "WAIT";
        ajaxCall("xl2ws", sUnitsH.getWsCreateArgs() +
            "&ws=" + encodeURIComponent(this.mInputModName.value),
            function(info) {sCreateWsH._setupTask(info);})
    },
    
    _setupTask: function(info) {
        this.mTaskId = info["task_id"];
        this.checkTask();
    },
    
    checkTask: function() {
        if (this.mTaskId == null)
            return;
        ajaxCall("job_status", "task=" + this.mTaskId,
            function(info) {
                sCreateWsH._checkTask(info);})
    },
    
    _checkTask: function(info) {
        if (info != null && info[0] == false) {
            this.mDivModStatus.innerHTML = info[1];
            if (this.mTimeH == null)
                this.mTimeH = setInterval(function() {sCreateWsH.checkTask()}, 3000);
            this.checkControls();
            return;
        }
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mStage = "DONE";
        sViewH.blockModal(false);
        this.checkControls();
        if (info == null) {
            this.mDivModStatus.innerHTML = "Task information lost";
        } else {
            if (info[0] == null) {
                this.mDivModStatus.innerHTML = info[1];
            } else {
                target_ref = (sWsURL != "ws")? '': (' target="' + 
                    sTitlePrefix + '/' + info[0]["ws"] + '"'); 
                this.mDivModStatus.innerHTML = 'Done: <a href="' + sWsURL + 
                    '?ws=' +  info[0]["ws"] + '"' + target_ref + '>Open it</a>';
            }
        }
    }
};

/*************************************/
/* Top control                       */
/*************************************/
var sViewH = {
    mShowToDrop: null,
    mDropCtrls: [],
    mModalCtrls: [],
    mBlock: false,
    
    init: function() {
        window.onclick = function(event_ms) {sViewH.onclick(event_ms);}
        this.addToDrop(document.getElementById("ds-control-menu"));
    },

    addToDrop: function(ctrl) {
        this.mDropCtrls.push(ctrl);
    },

    dropOn: function(ctrl) {
        if (this.mDropCtrls.indexOf(ctrl) < 0)
            this.mDropCtrls.push(ctrl);
        if (ctrl.style.display == "block") {
            this.dropOff();
        } else {
            this.dropOff();
            ctrl.style.display = "block";
            this.mShowToDrop = true;
        }
    },
    
    dropOff: function() {
        this.mShowToDrop = false;
        for (idx = 0; idx < this.mDropCtrls.length; idx++) {
            this.mDropCtrls[idx].style.display = "none";
        }
    },
    
    modalOn: function(ctrl, disp_mode) {
        this.mBlock = false;
        if (this.mModalCtrls.indexOf(ctrl) < 0)
            this.mModalCtrls.push(ctrl);
        this.modalOff();
        ctrl.style.display = (disp_mode)? disp_mode: "block";
    },
    
    modalOff: function() {
        if (this.mBlock)
            return;
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            this.mModalCtrls[idx].style.display = "none";
        }
        onModalOff();
    },
    
    blockModal: function(mode) {
        this.mBlock = mode;
        document.body.className = (mode)? "wait":"";
    },
    
    onclick: function(event_ms) {
        for (idx = 0; idx < this.mModalCtrls.length; idx++) {
            if (event_ms.target == this.mModalCtrls[idx]) 
                this.modalOff();
        }
        if (this.mShowToDrop && !event_ms.target.matches('.drop')) {
            this.dropOff();
        }
    }
};
