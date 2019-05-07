/**************************************/
var sOpNumH = {
    mInfo: null,
    mInputMin: null,
    mInputMax: null,
    mUpdateCondStr: null,

    init: function() {
        this.mInputMin   = document.getElementById("cond-min-inp");
        this.mInputMax   = document.getElementById("cond-max-inp");
    },
    
    getCondType: function() {
        return "numeric";
    },

    suspend: function() {
        this.mInfo = null;
        this.careControls();
    },
    
    updateUnit: function(unit_stat) {
        this.mUpdateCondStr = null;
        this.mInfo = {
            cur_bounds: [null, null],
            unit_type:  unit_stat[0],
            val_min:    unit_stat[2],
            val_max:    unit_stat[3],
            count:      unit_stat[4]}
            
        document.getElementById("cond-min").innerHTML = 
            normFloatLongTail(this.mInfo.val_min);
        document.getElementById("cond-max").innerHTML = 
            normFloatLongTail(this.mInfo.val_max, true);
        document.getElementById("cond-sign").innerHTML = 
            (this.mInfo.val_min == this.mInfo.val_max)? "=":"&le;";
        this.mInputMin.value = "";
        this.mInputMax.value = "";
    },

    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        this.mInfo.cur_bounds   = [cond[2][0], cond[2][1]];
        this.mInputMin.value = (this.mInfo.cur_bounds[0] != null)?
            this.mInfo.cur_bounds[0] : "";
        this.mInputMax.value = (this.mInfo.cur_bounds[1] != null)?
            this.mInfo.cur_bounds[1] : "";
        document.getElementById("cond-sign").innerHTML = "&le;";
    },

    careControls: function() {
        document.getElementById("cur-cond-numeric").style.display = 
            (this.mInfo == null)? "none":"block";
    },

    checkControls: function(opt) {
        if (this.mInfo == null) 
            return;
        var err_msg = null;
        if (this.mInputMin.value.trim() == "") {
            this.mInfo.cur_bounds[0] = null;
            this.mInputMin.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMin.value)
            this.mInputMin.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                err_msg = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[0] = val;
            }
        }
        if (this.mInputMax.value.trim() == "") {
            this.mInfo.cur_bounds[1] = null;
            this.mInputMax.className = "num-inp";
        } else {
            val = toNumeric(this.mInfo.unit_type, this.mInputMax.value)
            this.mInputMax.className = (val == null)? "num-inp bad":"num-inp";
            if (val == null) 
                err_msg = "Bad numeric value";
            else {
                this.mInfo.cur_bounds[1] = val;
            }
        }
        if (err_msg == null) {
            if (this.mInfo.cur_bounds[0] == null && 
                    this.mInfo.cur_bounds[1] == null)
                err_msg = "";            
            if (this.mInfo.cur_bounds[0] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[0] > this.mInfo.val_max)
                err_msg = "Lower bound is above maximum value";
            if (this.mInfo.cur_bounds[1] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[1] < this.mInfo.val_min)
                err_msg = "Upper bound is below minimum value";
            if (this.mInfo.cur_bounds[0] != null && 
                    this.mInfo.cur_bounds[1] != null && 
                    this.mInfo.cur_bounds[0] > this.mInfo.cur_bounds[1])
                err_msg = "Bounds are mixed up";
        }

        condition_data = null;
        if (err_msg == null) {
            condition_data = [this.mInfo.cur_bounds, null]
            if (this.mInfo.cur_bounds[0] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[0] < this.mInfo.val_min)
                err_msg = "Lower bound is below minimal value";
            if (this.mInfo.cur_bounds[1] != null && !this.mUpdateCondStr &&
                    this.mInfo.cur_bounds[1] > this.mInfo.val_max)
                err_msg = "Upper bound is above maximal value";
            if (this.mUpdateCondStr && !err_msg &&    
                    JSON.stringify(condition_data) == this.mUpdateCondStr) {
                err_msg = " ";
                condition_data = null;
            }
        }
        sOpCondH.formCondition(
            condition_data, err_msg, this.mInfo.op, false);
        this.careControls();
    }
};

/**************************************/
var sOpEnumH = {
    mVariants: null,
    mOperationMode: null,
    mDivVarList: null,
    mSpecCtrl: null,
    mStatusMode: null,
    mUpdateCondStr: null,
    mDivZygPGroup: null,

    init: function() {
        this.mDivVarList = document.getElementById("op-enum-list");
        this.mDivZygPGroup = document.getElementById("cur-cond-zyg-problem-group");
    },
    
    getCondType: function() {
        if (this.mSpecCtrl != null)
            return this.mSpecCtrl.getCondType();
        return "enum";
    },
    
    suspend: function() {
        this.mVariants = null;
        this.mOperationMode = null;
        this.careControls();
    },

    updateUnit: function(unit_stat) {
        this.mUpdateCondStr = null;
        if (unit_stat[0] == "zygosity") {
            this.mSpecCtrl = sZygosityH;
            this.mVariants = sZygosityH.setupVariants(unit_stat, this.mDivZygPGroup);
            this.mOperationMode = null;
            this.mStatusMode = null;
        } else {
            this.mVariants = unit_stat[2];
            this.mOperationMode = 0;
            this.mStatusMode = (unit_stat[0] == "status");
            this.mSpecCtrl = null;
            if (this.mDivZygPGroup) {
                this.mDivZygPGroup.style.display = "none";
            }
        }
        
        list_val_rep = [];
        has_zero = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            var_count = this.mVariants[j][1];
            has_zero |= (var_count == 0);
            list_val_rep.push('<div class="enum-val' + 
                ((var_count==0)? " zero":"") +'">' +
                '<input id="elcheck--' + j + '" type="checkbox" ' + 
                'onchange="sOpEnumH.checkControls();"/>&emsp;' + var_name + 
                '<span class="enum-cnt">(' + var_count + ')</span></div>');
        }
        this.mDivVarList.innerHTML = list_val_rep.join('\n');
        
        document.getElementById("cur-cond-enum-zeros").style.display = 
            (has_zero)? "block":"none";            
        this.careEnumZeros(false);
    },
    
    updateCondition: function(cond) {
        this.mUpdateCondStr = JSON.stringify(cond.slice(2));
        if (this.mSpecCtrl != null) {
            this.mSpecCtrl = sZygosityH;
            var_list = this.mSpecCtrl.getCondVarList(cond);
            op_mode = this.mSpecCtrl.getCondOpMode(cond);
        } else {
            var_list = cond[3];
            op_mode = cond[2];
        }
        if (this.mOperationMode != null)
            this.mOperationMode = ["OR", "AND", "ONLY", "NOT"].indexOf(op_mode);
        needs_zeros = false;
        for (j = 0; j < this.mVariants.length; j++) {
            var_name = this.mVariants[j][0];
            if (var_list.indexOf(var_name) < 0)
                continue;
            needs_zeros |= (this.mVariants[j][1] == 0);
            document.getElementById("elcheck--" + j).checked = true;
        }
        this.careEnumZeros(needs_zeros);
        this.checkControls();
    },
    
    careControls: function() {
        document.getElementById("cur-cond-enum").style.display = 
            (this.mVariants == null)? "none":"block";
        for (idx = 1; idx < 4; idx++) {
            vmode = ["or", "and", "only", "not"][idx];
            document.getElementById("cond-mode-" + vmode + "-span").
                style.visibility = (this.mOperationMode == null ||
                    (this.mStatusMode && idx != 3))? "hidden":"visible";
            document.getElementById("cond-mode-" + vmode).checked =
                (idx == this.mOperationMode);
        }
    },

    careEnumZeros: function(opt) {
        var check_enum_z = document.getElementById("cur-enum-zeros");
        if (opt == undefined) {
            show_zeros = check_enum_z.checked;
        } else {
            show_zeros = opt;
            check_enum_z.checked = show_zeros;
        }
        this.mDivVarList.className = (show_zeros)? "":"no-zeros";
    },
    
    checkControls: function(opt) {
        if (this.mVariants == null) 
            return;
        this.careControls();
        var err_msg = null;
        if (opt != undefined && this.mOperationMode != null) {
            if (this.mOperationMode == opt)
                this.mOperationMode = 0;
            else
                this.mOperationMode = opt;
        }
        sel_names = [];
        for (j=0; j < this.mVariants.length; j++) {
            if (document.getElementById("elcheck--" + j).checked)
                sel_names.push(this.mVariants[j][0]);
        }
        op_mode = "";
        if (this.mOperationMode != null)
            op_mode = ["", "AND", "ONLY", "NOT"][this.mOperationMode];
        
        condition_data = null;
        if (sel_names.length > 0) {
            condition_data = [op_mode, sel_names];
            err_msg = "";
        } else
            err_msg = " Empty selection"
        if (this.mSpecCtrl != null) {
            condition_data = this.mSpecCtrl.transCondition(condition_data);
            err_msg = this.mSpecCtrl.checkError(condition_data, err_msg);
        }
        if (this.mUpdateCondStr && !err_msg && condition_data &&
                JSON.stringify(condition_data) == this.mUpdateCondStr) {
            err_msg = " ";
            condition_data = null;
        }

        sOpCondH.formCondition(condition_data, err_msg, op_mode, true);
        this.careControls();
    }
};

/**************************************/
var sZygosityH = {
    mFamily: null,
    mProblemIdxs: null,
    mUnitName: null,
    mDefaultIdxs: null,
    mDefaultRepr: null,
    mZStat: null,
    mZEmpty: null,
    
    setup: function(unit_stat, list_stat_rep) {
        this.mUnitName = unit_stat[1]["name"];
        this.mFamily = unit_stat[1]["family"];
        this.mDefaultIdxs = unit_stat[1]["affected"];
        this.mDefaultRepr = this.mDefaultIdxs.join(',');
        this.mProblemIdxs = unit_stat[2];
        if (this.mProblemIdxs == null)
            this.mProblemIdxs = this.mDefaultIdxs.slice();
        this.mZStat = unit_stat[3] ;
        list_stat_rep.push('<div id="zyg-wrap">');
        list_stat_rep.push('<div id="zyg-problem">');
        this._fillProblemGroup(this.mFamily, this.mProblemIdxs, list_stat_rep);
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div id="zyg-stat">');
        this._reportStat(list_stat_rep);
        list_stat_rep.push('</div></div>');
        sUnitsH.setCtxPar("problem_group", this.mProblemIdxs.slice())
    },
    
    _fillProblemGroup: function(family, problem_idxs, list_stat_rep) {
        list_stat_rep.push('<div class="zyg-family">');
        for (var idx = 0; idx < family.length; idx++) {
            q_checked = (problem_idxs.indexOf(idx)>=0)? " checked":"";
            list_stat_rep.push('<div class="zyg-fam-member">' + 
                '<input type="checkbox" id="zyg-fam_m__' + idx + '" ' + q_checked + 
                ' onchange="sZygosityH.checkMember(' + idx + ');" />' +
                family[idx] + '</div>');
        }
        list_stat_rep.push('</div>');
        if (this.mDefaultIdxs.length > 0) {
            reset_dis = (this.mDefaultIdxs.join(',') == problem_idxs.join(','))?
                'disabled="true"':'';
            list_stat_rep.push('<button id="zyg-fam-reset" ' +
                'title="Reset affected group" ' + reset_dis + 
                ' onclick="sZygosityH.resetGrp()">Reset</button>');
        }
    },
    
    getCondType: function() {
        return "zygosity";
    },
    
    setupVariants: function(unit_stat, div_pgroup) {
        if (div_pgroup) {
            list_stat_rep = [];
            problem_idxs = unit_stat[2];
            if (problem_idxs == null)
                problem_idxs = this.mDefaultIdxs;
            this._fillProblemGroup(this.mFamily, problem_idxs, list_stat_rep);
            div_pgroup.innerHTML = list_stat_rep.join('\n');
            div_pgroup.style.display = "flex";
        }
        return (this.mZStat == null)? []:this.mZStat;
    },
    
    transCondition: function(condition_data) {
        if (condition_data == null)
            return null;
        ret = condition_data.slice();
        ret.splice(0, 0, (this.mProblemIdxs.join(',') == this.mDefaultRepr)? 
            null: this.mProblemIdxs.slice());
        return ret;
    },
    
    checkError: function(condition_data, err_msg) {
        if (this.mZStat == null)
            return " Determine problem group";
        if (this.mZEmpty)
            return "Out of choice";
        return err_msg;
    },
    
    getUnitTitle: function(problem_group) {
        if (problem_group == undefined || problem_group.join(',') == this.mDefaultRepr)
            return this.mUnitName + '()';        
        return this.mUnitName + '({' + problem_group.join(',') + '})';        
    },
    
    checkUnitTitle: function(unit_name) {
        if (unit_name != this.mUnitName)
            return null;
        return this.getUnitTitle();
    },
    
    getCondOpMode: function(condition_data) {
        return condition_data[3];
    },
    
    getCondVarList: function(condition_data) {
        return condition_data[4];
    },
    
    onSelectCondition: function(condition_data) {
        if (condition_data[1] != this.mUnitName)
            return;
        if (condition_data[2] == null) {
            if (this.mProblemIdxs.join(",") == this.mDefaultRepr)
                return;
        } else {
            if (this.mProblemIdxs.join(",") == condition_data[2].join(","))
                return;
        }
        this.mProblemIdxs = condition_data[2];
        this._reselectFamily();
    },
    
    _reselectFamily: function() {
        for (var m_idx = 0; m_idx < this.mFamily.length; m_idx++)
            document.getElementById("zyg-fam_m__" + m_idx).checked =
                (this.mProblemIdxs.indexOf(m_idx) >= 0);
        this.refreshContext();
    },
    
    _reportStat: function(list_stat_rep) {
        this.mZEmpty = true;
        if (this.mZStat == null) {
            list_stat_rep.push('<span class="stat-bad">Determine problem group</span>');
        } else {
            list_count = 0;
            for (j = 0; j < this.mZStat.length; j++) {
                if (this.mZStat[j][1] > 0)
                    list_count++;
            }
            if (list_count > 0) {
                list_stat_rep.push('<ul>');
                for (j = 0; j < this.mZStat.length; j++) {
                    var_name = this.mZStat[j][0];
                    var_count = this.mZStat[j][1];
                    if (var_count == 0)
                        continue;
                    this.mZEmpty = false;
                    list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
                        '<span class="stat-count">' +
                        var_count + ' records</span></li>');
                }
            } else {
                list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
            }
        }
    },
    
    resetGrp: function() {
        if (this.mDefaultRepr != this.mProblemIdxs.join(',')) {
            this.mProblemIdxs = this.mDefaultIdxs;
            this._reselectFamily();
            return;
        }
    },
    
    checkMember: function(m_idx) {
        m_checked = document.getElementById("zyg-fam_m__" + m_idx).checked;
        if (m_checked && this.mProblemIdxs.indexOf(m_idx) < 0) {
            this.mProblemIdxs.push(m_idx);
            this.mProblemIdxs.sort();
            this.refreshContext();
            return;
        } 
        if (!m_checked) {
            pos = this.mProblemIdxs.indexOf(m_idx);
            if (pos >= 0) {
                this.mProblemIdxs.splice(pos, 1);
                this.refreshContext();
            }
        }
    },
    
    refreshContext: function() {
        if (this.mDefaultIdxs.length > 0)
            document.getElementById("zyg-fam-reset").disabled = 
                (this.mDefaultRepr == this.mProblemIdxs.join(','));
        sUnitsH.setCtxPar("problem_group", this.mProblemIdxs.slice());
        ajaxCall("xl_statunits", sUnitsH.getRqArgs() + 
            "&units=" + encodeURIComponent(JSON.stringify([this.mUnitName])), 
            function(info){sZygosityH._refresh(info);})
    },
    
    _refresh: function(info) {
        this.mZStat = info["units"][0][3];
        rep_list = [];
        this._reportStat(rep_list);
        document.getElementById("zyg-stat").innerHTML = rep_list.join('\n');
        sUnitsH.updateZygUnit(this.getUnitTitle());
    }
};

/*************************************/
/*************************************/
function fillEnumStat(items, unit_map, list_stat_rep, unit_names_to_load) {
    var group_title = false;
    for (idx = 0; idx < items.length; idx++) {
        unit_stat = items[idx];
        unit_type = unit_stat[0];
        unit_name   = unit_stat[1]["name"];
        unit_title  = unit_stat[1]["title"];
        unit_vgroup = unit_stat[1]["vgroup"];
        unit_map[unit_name] = idx;
        if (group_title != unit_vgroup || unit_vgroup == null) {
            if (group_title != false) {
                list_stat_rep.push('</div>');
            }
            group_title = unit_vgroup;
            list_stat_rep.push('<div class="stat-group">');
            if (group_title != null) {
                list_stat_rep.push('<div class="stat-group-title">' + 
                    group_title + '</div>');
            }
        }
        list_stat_rep.push('<div id="stat--' + unit_name + 
            '" class="stat-unit" onclick="sUnitsH.selectUnit(\'' + 
            unit_name + '\');">');
        list_stat_rep.push('<div class="wide"><span class="stat-unit-name">' +
            unit_name + '</span>');
        if (unit_title)
            list_stat_rep.push('<span class="stat-unit-title">' + 
                unit_title + '</span>');
        list_stat_rep.push('</div>')
        if (false && unit_name == "Rules") {
            list_stat_rep.push(
                '<span id="flt-run-rules" title="Rules evaluation setup" ' +
                ' onclick="rulesModOn();">&#9874;</span>')
        }
        list_stat_rep.push('<div id="stat-data--' + unit_name + '" class="stat-unit-data">');
        if (unit_stat.length == 2) {
            unit_names_to_load.push(unit_name);
            list_stat_rep.push('<div class="loading">Loading data...</div>');
        } else {
            if (unit_type == "zygosity") 
                sZygosityH.setup(unit_stat, list_stat_rep);
            else {
                if (unit_type == "long" || unit_type == "float") 
                    fillStatRepNum(unit_stat, list_stat_rep);
                else
                    fillStatRepEnum(unit_stat, list_stat_rep);
            }
        }
        list_stat_rep.push('</div></div>')
    }
    if (group_title != false) {
        list_stat_rep.push('</div>')
    }
}

function refillUnitStat(unit_stat) {
    unit_type = unit_stat[0];
    unit_name = unit_stat[1]["name"];
    div_el = document.getElementById("stat-data--" + unit_name);
    list_stat_rep = [];
    if (unit_type == "zygosity") 
        sZygosityH.setup(unit_stat, list_stat_rep);
    else {
        if (unit_type == "long" || unit_type == "float") 
            fillStatRepNum(unit_stat, list_stat_rep);
        else
            fillStatRepEnum(unit_stat, list_stat_rep);
    }
    div_el.innerHTML = list_stat_rep.join('\n');
}

function topUnitStat(unit_stat) {
    return document.getElementById("stat--" + unit_name).getBoundingClientRect().top;
}

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
        
        var info = _prepareWsCreate();
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
        ajaxCall("xl2ws", "ds=" + sDSName + _callWsArgs() +
            "&ws=" + encodeURIComponent(this.mInputModName.value),
            function(info) {
                sCreateWsH._setupTask(info);})
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

