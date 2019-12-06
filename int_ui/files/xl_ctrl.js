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
sSubViewCurAspect = null;

function initXL() {
    window.onclick = function(event_ms) {sViewH.onclick(event_ms);}
    sViewH.addToDrop(document.getElementById("control-menu"));
    sOpNumH.init();
    sOpEnumH.init();
    sCreateWsH.init()
    sSubViewH.init();
    ajaxCall("dsinfo", "ds=" + sDSName, setupDSInfo);
}

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
                target_ref = (sWsRefURL != "ws")? '': (' target="' + 
                    sCommonTitle + ':' + info[0]["ws"] + '"'); 
                this.mDivModStatus.innerHTML = 'Done: <a href="' + sWsRefURL + 
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

/*************************************/
var sSubViewH = {
    mMode: null,
    mDefaultMode: 0,
    mInfo: null,
    mCurRecIdx: null,
    mDivStatus: null,
    mDivMod: null,
    mInpCheckFull: null,
    mInpCheckSmp: null,
    mSpanCheckFull: null,
    mSpanCheckSmp: null,
    mDivRecList: null,
    mSpanTotal: null,
    mSpanRecTitle: null,
    mFrameRec: null,
    mDivBack: null,
    mButtonShow: null,
    mTaskId: null,
    mTimeH: null,
    
    init: function() {
        sSamplesCtrl = this;
        this.mDivStatus = document.getElementById("sub-view-status");
        this.mDivMod = document.getElementById("sub-view-mod");
        this.mInpCheckFull = document.getElementById("sub-view-check-full");
        this.mInpCheckSmp = document.getElementById("sub-view-check-samples");
        this.mSpanCheckFull = document.getElementById("sub-view-mod-full");
        this.mSpanCheckSmp = document.getElementById("sub-view-mod-samples");
        this.mDivRecList = document.getElementById("sub-view-list");
        this.mSpanTotal = document.getElementById("sub-view-list-report");
        this.mSpanRecTitle = document.getElementById("sub-view-title");
        this.mFrameRec = document.getElementById("rec-frame1");
        this.mDivBack = document.getElementById("sub-view-back");
        this.mButtonShow = document.getElementById("xl-sub-view");
    },
    
    reset: function(count) {
        this.mInfo = null;
        this.mCurRecIdx = null;
        this.mButtonShow.disabled = (count == 0);
    },
    
    show: function() {
        if (this.mInfo != null) {
            this.mDivStatus.style.visibility = "hidden";
            this.mDivMod.style.visibility = "visible";
        } else {
            this.mTaskId = null;
            ajaxCall("xl_list", sUnitsH.getRqArgs(), 
                function(info){sSubViewH._setupTask(info);})
        }
        sViewH.modalOn(this.mDivBack);
        this.arrangeControls();
    },

    _setupTask: function(info) {
        this.mTaskId = info["task_id"];
        this.mDivMod.style.visibility = "hidden";
        this.mDivStatus.style.visibility = "visible";
        this.checkTask();
    },
    
    checkTask: function() {
        if (this.mTaskId == null)
            return;
        ajaxCall("job_status", "task=" + this.mTaskId,
            function(info) {
                sSubViewH._checkTask(info);})
    },
    
    _checkTask: function(info) {
        if (info == null || info[0] == null) {
            this.mTaskId = null;
            relaxView();
            return;
        } 
        if (info[0] == false) {
            this.mDivStatus.innerHTML = info[1];
            if (this.mTimeH == null)
                this.mTimeH = setInterval(function() {sSubViewH.checkTask()}, 3000);
            return;
        }
        if (this.mTimeH != null) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this.mInfo = info[0];
        var mode = this.mDefaultMode;
        if (!this.mInfo["samples"])
            mode = 0;
        if (!this.mInfo["records"])
            mode = 1;
        this.refillControls(mode);
        this.show();
    },
    
    setMode: function(mode) {
        if (this.mMode === mode || this.mInfo == null || 
                !this.mInfo[["records", "samples"][mode]]) {
            this.mInpCheckFull.checked = (this.mMode == 0);
            this.mInpCheckSmp.checked = (this.mMode == 1);
            return;
        }
        this.mDefaultMode = mode;
        this.refillControls(mode);
    },
    
    refillControls: function(mode) {
        this.mMode = mode;
        this.mInpCheckFull.disabled = !this.mInfo["records"];
        this.mInpCheckSmp.disabled = !this.mInfo["samples"];
        this.mInpCheckFull.checked = (mode == 0);
        this.mInpCheckSmp.checked = (mode == 1);
        this.mSpanCheckFull.className = (mode==0)? "":"blocked";
        this.mSpanCheckSmp.className = (mode==1)? "":"blocked";
        this.mMode = mode;
        list_rep = [];
        var records = this.mInfo[["records", "samples"][mode]];
        var v_prefix = ["N-", "S-"][mode];
        for (var idx = 0; idx < records.length; idx++) {
            color  = records[idx][2];
            list_rep.push('<div id="sub-li--' + idx + '" class="' + 
                'rec-label ' + color + '" onclick="sSubViewH.selectRec(' + idx + ');">' + 
                v_prefix  + (idx + 1) + '</div>');
        }
        this.mDivRecList.innerHTML = list_rep.join('\n');
        this.mSpanTotal.innerHTML = "In scope: " + sUnitsH.getCurCount();
        this.mCurRecIdx = null;
        this.selectRec(0);
    },
    
    selectRec: function(rec_idx) {
        if (rec_idx == this.mCurRecIdx)
            return;
        if (this.mCurRecIdx != null) {
            var prev_el = document.getElementById('sub-li--' + this.mCurRecIdx);
            prev_el.className = prev_el.className.replace(" press", "");
        }
        this.mCurRecIdx = rec_idx;
        var new_rec_el = document.getElementById('sub-li--' + this.mCurRecIdx);
        new_rec_el.className = new_rec_el.className + " press";
        var info = this.mInfo[["records", "samples"][this.mMode]][this.mCurRecIdx];
        this.mSpanRecTitle.innerHTML = info[1];
        softScroll(new_rec_el);
        window.frames['rec-frame1'].location.replace(
            "xl_rec?ds=" + sDSName + "&rec=" + info[0]);
    },
    
    onKey: function(event_key) {
        if (this.mDivBack.style.display == "none" || this.mInfo == null)
            return;
        if (event_key.code == "ArrowUp" && this.mCurRecIdx > 0)
            this.selectRec(this.mCurRecIdx - 1);
        if (event_key.code == "ArrowDown" && 
                this.mCurRecIdx + 1 < this.mInfo[["records", "samples"][this.mMode]].length )
            this.selectRec(this.mCurRecIdx + 1);
    },
    
    arrangeControls: function() {
        el_mod_height = this.mDivMod.offsetHeight;
        if (el_mod_height == 0)
            return;
        document.getElementById("sub-view-wrap-list").style.height=
            Math.max(10, el_mod_height - 110);
        document.getElementById("sub-view-rec-wrap").style.height=
            Math.max(10, el_mod_height - 30);
            
    }
};

