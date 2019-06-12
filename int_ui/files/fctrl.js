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
        sOpCondH.formCondition(condition_data, err_msg, this.mInfo.op, false);
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
        sZygosityH.init(!!this.mDivZygPGroup);
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
    
    readyForCondition: function(unit_stat, condition) {
        if (unit_stat[0] == "zygosity")
            return sZygosityH.readyForCondition(unit_stat, condition);
        return true;
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
        this.mDivVarList.className = "";
        
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
            this.mOperationMode = ["OR", "AND", "NOT"].indexOf(op_mode);
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
        for (idx = 1; idx < 3; idx++) {
            vmode = ["or", "and", "not"][idx];
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
            op_mode = ["", "AND", "NOT"][this.mOperationMode];
        
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
    },
    
    waitForUpdate: function(unit_name) {
        this.mDivVarList.className = "wait";
    }
};

/**************************************/
/**************************************/
function newZygStat(stat) {
    var size = 0;
    if (stat) {
        for (var j = 0; j < stat.length; j++) {
            if (stat[j][1] > 0)
                size++;
        }
    }
    return {mStat: stat, mSize: size};
}

function zygStatStatList(zyg_stat) {
    return (zyg_stat.mStat == null)? []:zyg_stat.mStat;
}

function zygStatReportValues(zyg_stat, list_stat_rep) {
    if (zyg_stat.mStat == null) {
        list_stat_rep.push('<span class="stat-bad">Determine problem group</span>');
        return;
    } 
    if (zyg_stat.mSize == 0) {
        list_stat_rep.push('<span class="stat-bad">Out of choice</span>');
        return;
    }
    list_stat_rep.push('<ul>');
    for (var j = 0; j < zyg_stat.mStat.length; j++) {
        var_name = zyg_stat.mStat[j][0];
        var_count = zyg_stat.mStat[j][1];
        if (var_count == 0)
            continue;
        list_stat_rep.push('<li><b>' + var_name + '</b>: ' + 
            '<span class="stat-count">' + var_count + ' records</span></li>');
    }
}
        
function zygStatCheckError(zyg_stat, err_msg) {
    if (zyg_stat.mStat == null)
        return " Determine problem group";
    if (zyg_stat.mSize == 0)
        return "Out of choice";
    return err_msg;
}

/**************************************/
function newZygCase(base, problem_idxs, stat_data, mode_op) {
    return {
        mBase: base,
        mModeOp: mode_op,
        mProblemIdxs: (problem_idxs == null)? this.mBase.mDefaultIdxs:problem_idxs,
        mStat: newZygStat(stat_data)};
}

function zygCaseSameCase(zyg_case, problem_idxs) {
    if (problem_idxs == null) 
        return (zygCaseProblemIdxs(zyg_case, true) == null);
    return problem_idxs.join(',') == zyg_case.mProblemIdxs.join(',');
}


function zygCaseProblemIdxs(zyg_case, check_default) {
    if (check_default && zyg_case.mBase.mDefaultRepr == zyg_case.mProblemIdxs.join(','))
        return null;
    return zyg_case.mProblemIdxs.slice();
}
        
function zygCaseFilIt(zyg_case, list_stat_rep) {
    if (zyg_case.mModeOp && zyg_case.mBase.mSeparateOp) {
        id_prefix = "zyg-fam-op-m__";
        button_id = "zyg-fam-op-reset";
        mode_op = 1;
    } else {
        id_prefix = "zyg-fam-m__";
        button_id = "zyg-fam-reset";
        mode_op = 0;
    }
    list_stat_rep.push('<div class="zyg-family">');
    for (var idx = 0; idx < zyg_case.mBase.mFamily.length; idx++) {
        q_checked = (zyg_case.mProblemIdxs.indexOf(idx)>=0)? " checked":"";
        list_stat_rep.push('<div class="zyg-fam-member">' + 
            '<input type="checkbox" id="' + id_prefix + idx + '" ' + q_checked + 
            ' onchange="sZygosityH.loadCase(' + mode_op + ');" />' +
            zyg_case.mBase.mFamily[idx] + '</div>');
    }
    list_stat_rep.push('</div>');
    if (zyg_case.mBase.mDefaultIdxs.length > 0) {
        reset_dis = (zygCaseProblemIdxs(zyg_case, true) == null)? 'disabled="true"':'';
        list_stat_rep.push('<button id="' + button_id + '"' +
            ' title="Reset affected group" ' + reset_dis + 
            ' onclick="sZygosityH.resetGrp(' + mode_op + ')">Reset</button>');
    }
}

/**************************************/
var sZygosityH = {
    mSeparateOp: false,
    mUnitName: null,
    mFamily: null,
    mDefaultIdxs: null,
    mDefaultRepr: null,
    mCases: [null, null],
    mWaitIdxs: [null, null],
    mTimeH: null,
    mOpBaseUnitStat: null,
    mOpBaseCondition: null,
    mOpSetUp: null,
    
    init: function(separate_op) {
        this.mSeparateOp = separate_op;
    },
    
    _baseSetup: function(unit_stat) {
        this.mUnitName = unit_stat[1]["name"];
        this.mFamily = unit_stat[1]["family"];
        this.mDefaultIdxs = unit_stat[1]["affected"];
        this.mDefaultRepr = this.mDefaultIdxs.join(',');
    },
    
    readyForCondition: function(unit_stat, condition_data) {
        if (!this.mSeparateOp)
            return true;
        if (this.mOpBaseUnitStat == unit_stat && condition_data == this.mOpBaseCondition)
            return true;
        this.mOpSetUp = false;
        this.mOpBaseUnitStat = unit_stat;
        this.mOpBaseCondition = condition_data;
        if (this.mUnitName == null) {
            this._baseSetup(unit_stat);
        }
        var cond_problem_idxs = condition_data[2];
        if (JSON.stringify(cond_problem_idxs) == JSON.stringify(unit_stat[2])) {
            this.mCases[1] = newZygCase(this, unit_stat[2], unit_stat[3], 1);
            return true;
        }
        this.reload(1, (cond_problem_idxs == null)? this.mDefaultIdxs:cond_problem_idxs);
        return false;
    },
    
    setup: function(unit_stat, list_stat_rep) {
        if (this.mTimeH) {
            clearInterval(this.mTimeH);
            this.mTimeH = null;
        }
        this._baseSetup(unit_stat);
        this.mCases[0] = newZygCase(this, unit_stat[2], unit_stat[3], 0);
        if (this.mSeparateOp && this.mOpBaseUnitStat) {
            if (JSON.stringify(unit_stat) != JSON.stringify(this.mOpBaseUnitStat)) {
                this.mOpBaseUnitStat = null;
                this.mOpBaseCondition = null;
                this.mCases[1] = null;
            } else 
                this.mOpBaseUnitStat = unit_stat;
        }
            
        list_stat_rep.push('<div id="zyg-wrap">');
        list_stat_rep.push('<div id="zyg-problem">');
        zygCaseFilIt(this.mCases[0], list_stat_rep);
        list_stat_rep.push('</div>');
        list_stat_rep.push('<div id="zyg-stat">');
        zygStatReportValues(this.mCases[0].mStat, list_stat_rep);
        list_stat_rep.push('</div></div>');
        sUnitsH.setCtxPar("problem_group", zygCaseProblemIdxs(this.mCases[0]))
    },    
    
    getCondType: function() {
        return "zygosity";
    },
    
    setupVariants: function(unit_stat, div_pgroup) {
        var mode_op = (this.mSeparateOp)? 1:0;
        if (div_pgroup && !this.mOpSetUp) {
            list_stat_rep = [];
            zygCaseFilIt(this.mCases[mode_op], list_stat_rep);
            div_pgroup.innerHTML = list_stat_rep.join('\n');
            div_pgroup.style.display = "flex";
            if (this.mSeparateOp)
                this.mOpSetUp = true;
        }
        return zygStatStatList(this.mCases[mode_op].mStat);
    },
    
    transCondition: function(condition_data) {
        if (condition_data == null)
            return null;
        ret = condition_data.slice();
        ret.splice(0, 0, zygCaseProblemIdxs(this.mCases[(this.mSeparateOp)? 1:0], true));
        return ret;
    },
    
    checkError: function(condition_data, err_msg) {
        return zygStatCheckError(this.mCases[(this.mSeparateOp)? 1:0].mStat, err_msg);
    },
    
    getUnitTitle: function(problem_idxs) {
        if (problem_idxs == null) 
            return this.mUnitName + '()';
        var problem_repr = problem_idxs.join(',');
        if (problem_repr == this.mDefaultRepr)
            return this.mUnitName + '()';        
        return this.mUnitName + '({' + problem_repr + '})';        
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
        this.reSelect(0, condition_data[2]);
        this.loadCase(0);
    },
    
    resetGrp: function(mode_op) {
        this.reSelect(mode_op, this.mDefaultIdxs);
        this.loadCase(mode_op);
    },

    reSelect: function(mode_op, problem_idxs) {
        if (problem_idxs == null)
            problem_idxs = this.mDefaultIdxs;
        var id_prefix = (mode_op)?"zyg-fam-op-m__" : "zyg-fam-m__";
        for (var idx = 0; idx < this.mFamily.length; idx++)
            document.getElementById(id_prefix + idx).checked =
                (problem_idxs.indexOf(idx) >= 0);
    },
    
    collectIdxs: function(mode_op) {
        var id_prefix = (mode_op)?"zyg-fam-op-m__" : "zyg-fam-m__";
        var problem_idxs = [];
        for (var idx = 0; idx < this.mFamily.length; idx++) {
            if (document.getElementById(id_prefix + idx).checked)
                problem_idxs.push(idx);
        }
        return problem_idxs;
    },
    
    loadCase: function(mode_op) {
        if (this.mTimeH == null)
            this.mTimeH = setInterval(function(){sZygosityH.reload(mode_op);}, 30)
        document.getElementById((mode_op)? "zyg-fam-op-reset":"zyg-fam-reset").disabled = 
            zygCaseProblemIdxs(this.mCases[mode_op], true) == null;
    },

    reload: function(mode_op, problem_idxs) {
        clearInterval(this.mTimeH);
        this.mTimeH = null;
        var check_same = true;
        if (problem_idxs == undefined) 
            var problem_idxs = this.collectIdxs(mode_op);
        else
            check_same = false;
        if (check_same && this.mCases[mode_op] && 
                zygCaseSameCase(this.mCases[mode_op], problem_idxs)) {
            if (this.mCases[1 - mode_op] == null) 
                return;
            problem_idxs = this.collectIdxs(1 - mode_op);
            if (zygCaseSameCase(this.mCases[1-mode_op], problem_idxs))
                return;
            mode_op = 1 - mode_op;
        }
        if (mode_op == 0) {
            sUnitsH.setCtxPar("problem_group", problem_idxs);
            document.getElementById("stat-data--" + this.mUnitName).className = "wait";
        }
        if (mode_op || !self.mSeparateOp) 
            document.getElementById("zyg-stat").className = "wait";
        var args = sUnitsH.getRqArgs(mode_op == 1) + 
            "&units=" + encodeURIComponent(JSON.stringify([this.mUnitName]));
        sOpEnumH.waitForUpdate();
        if (mode_op == 1) {
            args += "&ctx=" + encodeURIComponent(
                JSON.stringify({"problem_group": problem_idxs}));
        }
        ajaxCall(sUnitsH.getCallPartStat(), args, 
            function(info){sZygosityH._reload(info, mode_op);})
    },
    
    _reload: function(info, mode_op) {
        var unit_stat = info["units"][0];
        this.mCases[mode_op] = newZygCase(this, unit_stat[2], unit_stat[3], mode_op);
        if (mode_op == 0) {
            rep_list = [];
            zygStatReportValues(this.mCases[0].mStat, rep_list);
            zyg_div = document.getElementById("zyg-stat");
            zyg_div.innerHTML = rep_list.join('\n');
            zyg_div.className = "";
            sUnitsH.updateZygUnit(this.mUnitName, unit_stat);
            if (!self.mSeparateOp) 
                refillUnitStat(unit_stat);
        } else {
            updateZygCondStat(this.mUnitName);
        }
        if (this.mCases[1 - mode_op])
            this.loadCase(1-mode_op);
    }
};

/*************************************/
/*************************************/
function fillEnumStat(items, unit_map, list_stat_rep, 
        unit_names_to_load, expand_mode) {
    var group_title = false;
    for (idx = 0; idx < items.length; idx++) {
        unit_stat = items[idx];
        unit_type = unit_stat[0];
        unit_name   = unit_stat[1]["name"];
        unit_title  = unit_stat[1]["title"];
        unit_vgroup = unit_stat[1]["vgroup"];
        unit_tooltip = unit_stat[1]["tooltip"];
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
            '" class="stat-unit" ');
        if (unit_tooltip) 
            list_stat_rep.push('title="' + escapeText(unit_tooltip) + '" ');

        list_stat_rep.push('onclick="sUnitsH.selectUnit(\'' + unit_name + '\');">');
        list_stat_rep.push('<div class="wide"><span class="stat-unit-name">' +
            unit_name + '</span>');
        if (unit_title) 
            list_stat_rep.push('<span class="stat-unit-title">' + 
                unit_title + '</span>');
        list_stat_rep.push('</div>')
        if (unit_name == "Rules") {
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
                if (unit_type == "int" || unit_type == "float") 
                    fillStatRepNum(unit_stat, list_stat_rep);
                else
                    fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
            }
        }
        list_stat_rep.push('</div></div>')
    }
    if (group_title != false) {
        list_stat_rep.push('</div>')
    }
}

function refillUnitStat(unit_stat, expand_mode) {
    unit_type = unit_stat[0];
    unit_name = unit_stat[1]["name"];
    div_el = document.getElementById("stat-data--" + unit_name);
    list_stat_rep = [];
    if (unit_type == "zygosity") 
        sZygosityH.setup(unit_stat, list_stat_rep);
    else {
        if (unit_type == "int" || unit_type == "float") 
            fillStatRepNum(unit_stat, list_stat_rep);
        else
            fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
    }
    div_el.innerHTML = list_stat_rep.join('\n');
    div_el.className = "";
}

function exposeEnumUnitStat(unit_stat, expand_mode) {
    unit_name = unit_stat[1]["name"];
    list_stat_rep = [];
    fillStatRepEnum(unit_stat, list_stat_rep, expand_mode);
    div_el = document.getElementById("stat-data--" + unit_name);
    div_el.innerHTML = list_stat_rep.join('\n');
}

function topUnitStat(unit_stat) {
    return document.getElementById("stat--" + unit_name).getBoundingClientRect().top;
}
