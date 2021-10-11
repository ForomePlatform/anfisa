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

//=====================================
var sZoneH = {
    mCurState: null,
    mElCurZState: null,
    mElCurZCheck: null,
    mElNegateDiv: null,
    mElNegateCheck: null,
    
    mWorkDescr: null,
    mWorkData: null,
    mWorkTitle: null,
    mWorkCur: null,
    mTagsState: null,
    mCacheList: {},
    mCacheDict: {},
    mCacheSet: {},
    
    init: function() {
        this.mElCurZCheck = document.getElementById("zone-check");
        this.mElCurZState = document.getElementById("zone-descr");
        this.mElNegateDiv = document.getElementById("work-zone-wrap-negate");
        this.mElNegateCheck = document.getElementById("work-zone-negate");
        this.updateCur();
        this.setWorkZone("");
        this.mElNegateCheck.checked = false;
    },
    
    getCurState: function() {
        return this.mCurState;
    },
    
    updateCur: function(mode_on) {
        cur_zone_status = this.getStatus();
        prev_zone_data = this.mCurState;
        document.getElementById("zone-cur-title").innerHTML = 
            (this.mWorkTitle)? this.mWorkTitle:"";
        this.mCurState = null;
        if (cur_zone_status) {
            this.mElCurZState.innerHTML = cur_zone_status;
            this.mElCurZState.className = "status";
            this.mElCurZCheck.disabled = true;
        } else {
            this.mElCurZState.innerHTML = this.mWorkDescr;
            this.mElCurZState.className = "";
            this.mElCurZCheck.disabled = false;
            this.mElCurZCheck.checked = (mode_on)? true:false;
            if (mode_on && this.mWorkData != null) {
                this.mCurState = [this.mWorkData];
                if (this.mWorkCur == "_tags" && this.mElNegateCheck.checked)
                    this.mCurState = [[this.mWorkData[0], this.mWorkData[1], false]];
            }
        }
        if (prev_zone_data != this.mCurState)
            reloadList();
    },

    checkControls: function() {
        this.updateCur(this.mElCurZCheck.checked);
    },
    
    arrangeControls: function() {
        zone_mod_height = document.getElementById("zone-mod").
            getBoundingClientRect().height;
        document.getElementById("work-zone-area").style.height = 
            zone_mod_height - 60;
        document.getElementById("work-zone-wrap-list").style.height = 
            zone_mod_height - 125;
    },

    clearSelection: function() {
        if (this.mWorkCur) {
            delete this.mCacheSet[this.mWorkCur];
            zone_check_id = 'zn--' + this.mWorkCur + '-check--';
            checkboxes = document.getElementsByClassName("zn-check-val");
            for (i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].id.startsWith(zone_check_id))
                    checkboxes[i].checked = false;
            }   
        }
        update();
    },
    
    setWorkZone: function(zone_name) {
        if(zone_name && !this.mCacheList[zone_name]) {
            this.loadZone(zone_name);
            return;
        }
        this.mWorkCur = zone_name;
        this.mWorkTitle = (zone_name)? this.mCacheList[zone_name][1]:"";

        zone_check_id = "zn-check--" + zone_name;
        checkboxes = document.getElementsByClassName("zone-checkbox");
        for (i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = (checkboxes[i].id == zone_check_id);
        }
        
        zone_div_id = "zn-div--" + zone_name;
        divs = document.getElementsByClassName("work-zone-list");
        for (i = 0; i < divs.length; i++) {
            divs[i].style.display = (divs[i].id == zone_div_id)? "block":"none";
        }
        this.update();
    },
    
    checkTagsState: function(tags_state) {
        if (tags_state != this.mTagsState) {
            if (this.mCacheList["_tags"]) {
                delete this.mCacheList["_tags"];
                this.loadZone("_tags");
            }
            this.mTagsState = tags_state;
        }
    },

    loadZone: function(zone_name) {
        var args = "ds=" + sDSName + "&zone=" + zone_name;
        ajaxCall("zone_list", args, function(info) {sZoneH.setupZone(info);})
    },

    setupZone: function(info) {
        zone_name = info["zone"];
        this.mWorkCur = zone_name;
        var variants = info["variants"];
        this.mCacheList[zone_name] = [variants, info["title"]];
        this.mCacheDict[zone_name] = {};
        var sel_variants = this.mCacheSet[this.mWorkCur];
        if (sel_variants == undefined)
            sel_variants = [];
        var new_sel = [];
        
        list_val_rep = [];
        for (j = 0; j < variants.length; j++) {
            val_name = variants[j];
            var check_mark = "";
            if (sel_variants.indexOf(val_name) >= 0) {
                new_sel.push(val_name);
                check_mark = "checked ";
            }
            this.mCacheDict[zone_name][val_name] = j;
            zone_ctrl_id = 'zn--' + zone_name + '-check--' + j;
            list_val_rep.push('<div class="zone-enum-val">' +
                '<input id="' + zone_ctrl_id + 
                '" type="checkbox" class="zn-check-val" ' + check_mark +
                'onchange="sZoneH.checkItem(\'' + zone_name + '\',' + 
                j + ');"/><label for="' + zone_ctrl_id + 
                '">&emsp;' + val_name + '</label></div>');
        }
        this.mCacheSet[this.mWorkCur] = new_sel;
        document.getElementById("zn-div--" + zone_name).innerHTML =
            list_val_rep.join('\n');
        this.setWorkZone(this.mWorkCur);
    },

    update: function() {
        this.mElNegateCheck.disabled = (this.mWorkCur != "_tags");
        if (!this.mWorkCur) {
            rep = ["<i>Define zone</i>"];
            this.mWorkDescr = null;
            this.mWorkData  = null;
        } else {
            rep = ["<i>Zone:</i> " + this.mWorkCur + "<br/>"];
            variants = this.mCacheSet[this.mWorkCur];
            if (variants == null || variants.length < 1) {
                rep.push("<i>Select a variant</i>");
                this.mWorkDescr = null;            
            } else {
                this.mWorkData = [this.mWorkCur, variants];
                this.mWorkDescr = "";
                if (this.mWorkCur == "_tags" && this.mElNegateCheck.checked) {
                    this.mWorkDescr = "NOT ";
                    rep.push("<b>NOT</b><br/>");
                }
                if (variants.length == 1) {
                    this.mWorkDescr += variants[0];
                    rep.push("= <b>" + variants[0] + "</b>");
                } else {
                    this.mWorkDescr += variants[0] + 
                        " <i>+" + (variants.length - 1) + " more</i>";
                    rep.push("<i>In:</i><br/>");
                    for (j=0; j<variants.length; j++) {
                        inp_ctrl_id = "check-drop-" + j;
                        rep.push('<input type="checkbox" checked id="' + inp_ctrl_id + 
                            '" onclick="sZoneH.dropItem(\'' + variants[j] + '\');"/>' +
                            '<label for="' + inp_ctrl_id + '">&emsp;' + variants[j] + 
                            '</label><br/>');
                    }
                }
            }
        }
        el = document.getElementById("work-zone-def");
        el.innerHTML = rep.join('\n');
        this.updateCur(this.mWorkData != null);
        document.getElementById("work-zone-clear").disabled = (this.mWorkData == null);
    },

    checkItem: function (zone_name, zone_var_idx) {
        if (zone_name == this.mWorkCur) {
            val_name = this.mCacheList[zone_name][0][zone_var_idx];
            if (this.mCacheSet[zone_name])
                idx = this.mCacheSet[zone_name].indexOf(val_name);
            else
                idx = -1;
            if (idx < 0) {
                if (!this.mCacheSet[zone_name]) {
                    this.mCacheSet[zone_name] = [val_name];
                } else {
                    this.mCacheSet[zone_name].push(val_name);
                }
            } else {
                if (this.mCacheSet[zone_name].length == 1)
                    delete this.mCacheSet[zone_name];
                else
                    this.mCacheSet[zone_name].splice(idx, 1);
            }
            el_id = 'zn--' + zone_name + '-check--' + zone_var_idx;
            document.getElementById(el_id).checked = (idx < 0);
            this.update();
        }
    },

    dropItem: function(val_name) {
        if (this.mCacheSet[this.mWorkCur]) {
            idx = this.mCacheSet[this.mWorkCur].indexOf(val_name);
            if (idx >= 0) {
                if (this.mCacheSet[this.mWorkCur].length > 1)
                    this.mCacheSet[this.mWorkCur].splice(idx, 1);
                else
                    delete this.mCacheSet[this.mWorkCur];
            }
            idx = this.mCacheDict[this.mWorkCur][val_name];
            if (idx != undefined) {
                el_id = 'zn--' + this.mWorkCur + '-check--' + idx;
                document.getElementById(el_id).checked = false;
            }
            this.update();
        }
    },

    getStatus: function() {
        if (this.mWorkDescr == null)
            return "not set";
        return null;
    }
};


function updateCurZone(mode_on) {
    sZoneH.updateCur(mode_on)
}

/*************************************/
