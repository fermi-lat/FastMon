## @package pGEMcontributionBase
## @brief Package for basic parsing of the GEM contribution.

import logging
import LDF

from copy     import copy
from pGlobals import *


## @brief Implementation of the GEM contribution parsing.

class pGEMcontributionBase:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for the creation and filling
    #  of the output ROOT tree.
    ## @param errorCounter
    #  The pEventErrorCounter object responsible for managing the errors.
    
    def __init__(self, event, contribution, treeMaker, errorCounter):

        ## @var __Contribution
        ## @brief The contribution object.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  and filling of the output ROOT tree.

        ## @var ErrorCounter
        ## @brief The pEventErrorCounter object responsible for
        #  managing the errors.
        
        self.__Contribution = contribution
        self.TreeMaker      = treeMaker
        self.ErrorCounter   = errorCounter

    ## @brief This is from Ric...
    ## @param self
    #  The class instance.
    ## @param attr
    #  The attribute name.

    def __getattr__(self, attr):
        return getattr(self.__Contribution, attr)

    ## @brief Function filling the gem_timebase tree variable.
    ## @param self
    #  The class instance.

    def gem_timebase(self):
        self.TreeMaker.getVariable('gem_timebase')[0] =\
                       copy(self.triggerTime())

    ## @brief Function filling the gem_discarded tree variable.
    ## @param self
    #  The class instance.

    def gem_discarded(self):
        self.TreeMaker.getVariable('gem_discarded')[0] = copy(self.discarded())

    ## @brief Function filling the gem_dead_zone tree variable.
    ## @param self
    #  The class instance.
	
    def gem_dead_zone(self):
        self.TreeMaker.getVariable('gem_dead_zone')[0] = copy(self.deadZone())

    ## @brief Function filling the gem_live_time tree variable.
    ## @param self
    #  The class instance.
	
    def gem_live_time(self):
        self.TreeMaker.getVariable('gem_live_time')[0] = copy(self.liveTime())

    ## @brief Function filling the gem_condition_summary tree variable.
    ## @param self
    #  The class instance.

    def gem_condition_summary(self):
        self.TreeMaker.getVariable('gem_condition_summary')[0] =\
                       copy(self.conditionSummary())

    ## @brief Function filling the gem_tkr_vector tree variable.
    ## @param self
    #  The class instance.

    def gem_tkr_vector(self):
        self.TreeMaker.getVariable('gem_tkr_vector')[0] =\
                       copy(self.tkrVector())

    ## @brief Function filling the gem_roi_vector tree variable.
    ## @param self
    #  The class instance.

    def gem_roi_vector(self):
        self.TreeMaker.getVariable('gem_roi_vector')[0] =\
                       copy(self.roiVector())

    ## @brief Function filling the gem_cal_le_vector tree variable.
    ## @param self
    #  The class instance.

    def gem_cal_le_vector(self):
        self.TreeMaker.getVariable('gem_cal_le_vector')[0] =\
                       copy(self.calLEvector())

    ## @brief Function filling the gem_cal_he_vector tree variable.
    ## @param self
    #  The class instance.

    def gem_cal_he_vector(self):
        self.TreeMaker.getVariable('gem_cal_he_vector')[0] =\
                       copy(self.calHEvector())

    ## @brief Function filling the gem_cond_arr_time_tkr tree variable.
    ## @param self
    #  The class instance.

    def gem_cond_arr_time_tkr(self):
        self.TreeMaker.getVariable('gem_cond_arr_time_tkr')[0] =\
                       copy(self.condArrTime().tkr())

    ## @brief Function filling the gem_cond_arr_time_cal_le tree variable.
    ## @param self
    #  The class instance.

    def gem_cond_arr_time_cal_le(self):
        self.TreeMaker.getVariable('gem_cond_arr_time_cal_le')[0] =\
                       copy(self.condArrTime().calLE())

    ## @brief Function filling the gem_cond_arr_time_cal_he tree variable.
    ## @param self
    #  The class instance.

    def gem_cond_arr_time_cal_he(self):
        self.TreeMaker.getVariable('gem_cond_arr_time_cal_he')[0] =\
                       copy(self.condArrTime().calHE())

    ## @brief Function filling the gem_cond_arr_time_roi tree variable.
    ## @param self
    #  The class instance.

    def gem_cond_arr_time_roi(self):
        self.TreeMaker.getVariable('gem_cond_arr_time_roi')[0] =\
                       copy(self.condArrTime().roi())

    ## @brief Function filling the gem_cond_arr_time_cno tree variable.
    ## @param self
    #  The class instance.

    def gem_cond_arr_time_cno(self):
        self.TreeMaker.getVariable('gem_cond_arr_time_cno')[0] =\
                       copy(self.condArrTime().cno())

    ## @brief Function filling the gem_trigger_time tree variable.
    ## @param self
    #  The class instance.

    def gem_trigger_time(self):
        self.TreeMaker.getVariable('gem_trigger_time')[0] =\
                       copy(self.triggerTime())

    ## @brief Function filling the gem_one_pps_time_time_base tree variable.
    ## @param self
    #  The class instance.

    def gem_one_pps_time_time_base(self):
        self.TreeMaker.getVariable('gem_one_pps_time_time_base')[0] =\
                       copy(self.onePPStime().timebase())

    ## @brief Function filling the gem_one_pps_time_seconds tree variable.
    ## @param self
    #  The class instance.

    def gem_one_pps_time_seconds(self):
        self.TreeMaker.getVariable('gem_one_pps_time_seconds')[0] =\
                       copy(self.onePPStime().seconds())

    ## @brief Function filling the gem_delta_event_time tree variable.
    ## @param self
    #  The class instance.

    def gem_delta_event_time(self):
        self.TreeMaker.getVariable('gem_delta_event_time')[0] =\
                       copy(self.deltaEventTime())

    ## @brief Function filling the gem_delta_window_open_time tree variable.
    ## @param self
    #  The class instance.

    def gem_delta_window_open_time(self):
        self.TreeMaker.getVariable('gem_delta_window_open_time')[0] =\
                       copy(self.deltaWindowOpenTime())

	
	
	

