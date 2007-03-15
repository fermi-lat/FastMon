
import logging
import LDF

from copy import copy

class pGEMcontributionBase:
    
    def __init__(self, event, contribution, treeMaker):
        self.__Contribution = contribution
        self.TreeMaker = treeMaker

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]
        
    def __getattr__(self, attr):
        return getattr(self.__Contribution, attr)

    def gem_timebase(self):
        self.getVariable("gem_timebase")[0] = copy(self.triggerTime())

# Discarded and Dead zone
    def gem_discarded(self):
        self.getVariable("gem_discarded")[0] = copy(self.discarded())
	
    def gem_dead_zone(self):
        self.getVariable("gem_dead_zone")[0] = copy(self.deadZone())
	
    def gem_live_time(self):
        self.getVariable("gem_live_time")[0] = copy(self.liveTime())
	
# Trigger Vector
    def gem_condition_summary(self):
        self.getVariable("gem_condition_summary")[0] = copy(self.conditionSummary())

    def gem_tkr_vector(self):
        self.getVariable("gem_tkr_vector")[0] = copy(self.tkrVector())

    def gem_cal_le_vector(self):
        self.getVariable("gem_cal_le_vector")[0] = copy(self.calLEvector())

    def gem_cal_he_vector(self):
        self.getVariable("gem_cal_he_vector")[0] = copy(self.calHEvector())

# Arrival Time
    def gem_cond_arr_time_tkr(self):
        self.getVariable("gem_cond_arr_time_tkr")[0] = copy(self.condArrTime().tkr())

    def gem_cond_arr_time_cal_le(self):
        self.getVariable("gem_cond_arr_time_cal_le")[0] = copy(self.condArrTime().calLE())

    def gem_cond_arr_time_cal_he(self):
        self.getVariable("gem_cond_arr_time_cal_he")[0] = copy(self.condArrTime().calHE())

    def gem_cond_arr_time_roi(self):
        self.getVariable("gem_cond_arr_time_roi")[0] = copy(self.condArrTime().roi())

    def gem_cond_arr_time_cno(self):
        self.getVariable("gem_cond_arr_time_cno")[0] = copy(self.condArrTime().cno())

# Time Info
    def gem_trigger_time(self):
        self.getVariable("gem_trigger_time")[0] = copy(self.triggerTime())
	#print "GEM Trigger Time ", self.triggerTime()

    def gem_one_pps_time_time_base(self):
        self.getVariable("gem_one_pps_time_time_base")[0] = copy(self.onePPStime().timebase())
	#print "GEM Time Base ", self.onePPStime().timebase()

    def gem_one_pps_time_seconds(self):
        self.getVariable("gem_one_pps_time_seconds")[0] = copy(self.onePPStime().seconds())
	#print "GEM Time Seconds ",  self.onePPStime().seconds()

    def gem_delta_event_time(self):
        self.getVariable("gem_delta_event_time")[0] = copy(self.deltaEventTime())

    def gem_delta_window_open_time(self):
        self.getVariable("gem_delta_event_time")[0] = copy(self.deltaWindowOpenTime())

	
	
	

