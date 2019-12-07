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

/**************************************/
/* XL base support: units, stats, etc.
 * Used in regimes: 
 * XL-Filter/XL-Tree
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
            err_msg = "Too many variants, try to reduce";
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
                target_ref = (sWsPubURL != "ws")? '': (' target="' + 
                    sCommonTitle + ':' + info[0]["ws"] + '"'); 
                this.mDivModStatus.innerHTML = 'Done: <a href="' + sWsPubURL + 
                    '?ds=' +  info[0]["ws"] + '"' + target_ref + '>Open it</a>';
            }
        }
    }
};

function wsCreate() {
    sCreateWsH.show();
}

function startWsCreate() {
    sCreateWsH.startIt();
}


