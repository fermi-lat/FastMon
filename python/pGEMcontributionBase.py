## @package pGEMcontributionBase
## @brief Package for basic parsing of the GEM contribution.

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
    ## @param errorHandler
    #  The pErrorHandler object responsible for managing the errors.
    
    def __init__(self, event, contribution, treeMaker, errorHandler):

        ## @var __Contribution
        ## @brief The contribution object.

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  and filling of the output ROOT tree.

        ## @var ErrorHandler
        ## @brief The pErrorHandler object responsible for
        #  managing the errors.
        
        self.__Contribution = contribution
        self.TreeMaker      = treeMaker
        self.ErrorHandler   = errorHandler

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

    ## @brief Function filling the DiscardedLast tree variable.
    ## @param self
    #  The class instance.

    def DiscardedLast(self):
        self.TreeMaker.getVariable('DiscardedLast')[0] = copy(self.discarded())

    ## @brief Function filling the DiscardedDelta tree variable.
    #  Do not reset this variable! 
    ## @param self
    #  The class instance.

    def DiscardedDelta(self):
        tmpDisc = copy(self.discarded())
        if self.ErrorHandler.EventNumber == 0:
            self.TreeMaker.getVariable('DiscardedDelta')[0] = 0
        else:
            if self.TreeMaker.getVariable('DiscardedDelta')[1] > tmpDisc:
                self.TreeMaker.getVariable('DiscardedDelta')[0] =\
                tmpDisc - self.TreeMaker.getVariable('DiscardedDelta')[1] + 2**24                
            else:
                self.TreeMaker.getVariable('DiscardedDelta')[0] =\
                tmpDisc - self.TreeMaker.getVariable('DiscardedDelta')[1]
        self.TreeMaker.getVariable('DiscardedDelta')[1] = tmpDisc


            
    ## @brief Function filling the DeadZoneLast tree variable.
    ## @param self
    #  The class instance.
	
    def DeadZoneLast(self):
        self.TreeMaker.getVariable('DeadZoneLast')[0] = copy(self.deadZone())

    ## @brief Function filling the DeadZoneDelta tree variable.
    #  Do not reset this variable!        
    ## @param self
    #  The class instance.
    ## @note The DeadZone counter is a 16 bit counter, but the GEMcontribution::deadZone()
    #  used here use only the last 8 bit (see LDF docs for more information)
	
    def DeadZoneDelta(self):
        tmpDZone = copy(self.deadZone())
        if self.ErrorHandler.EventNumber == 0:
            self.TreeMaker.getVariable('DeadZoneDelta')[0] = 0
        else:
            if self.TreeMaker.getVariable('DeadZoneDelta')[1] > tmpDZone:
                self.TreeMaker.getVariable('DeadZoneDelta')[0] =\
                tmpDZone - self.TreeMaker.getVariable('DeadZoneDelta')[1] + 2**8             
            else:
                self.TreeMaker.getVariable('DeadZoneDelta')[0] =\
                tmpDZone - self.TreeMaker.getVariable('DeadZoneDelta')[1]
        self.TreeMaker.getVariable('DeadZoneDelta')[1] = tmpDZone

        
    ## @brief Function filling the LivetimeLast tree variable.
    ## @param self
    #  The class instance.
	
    def LivetimeLast(self):
        self.TreeMaker.getVariable('LivetimeLast')[0] = copy(self.liveTime())

    def PrescaledLast(self):
        self.TreeMaker.getVariable('PrescaledLast')[0] = copy(self.prescaled())

    ## @brief Function filling the condsummary tree variable.
    ## @param self
    #  The class instance.

    def condsummary(self):
        self.TreeMaker.getVariable('condsummary')[0] =\
                       copy(self.conditionSummary())

    ## @brief Function filling the TkrTriggerTower tree variable (used to be gem_tkr_vector).
    ## @param self
    #  The class instance.

    def TkrTriggerTower(self):
        self.TreeMaker.getVariable('TkrTriggerTower')[0] =\
                       copy(self.tkrVector())

    ## @brief TBD 

    def AcdGemVeto_AcdTile(self):
        gemTL = self.tileList()
        for iGemIdx in range(16):
            if ( gemTL.XZM() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx]+=1
            if ( gemTL.XZP() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+16]+=1
            if ( gemTL.YZM() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+32]+=1
            if ( gemTL.YZP() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+48]+=1
            if ( gemTL.XY() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+64]+=1
            if ( gemTL.XY() & ( 1 << (16+iGemIdx) ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+80]+=1
            if ( gemTL.RBN() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+96]+=1
            if ( gemTL.NA() & ( 1 << iGemIdx ) ):
                self.TreeMaker.getVariable('AcdGemVeto_AcdTile')[iGemIdx+112]+=1
        

    ## @brief TBD 

    def AcdGemCNO_GARC(self):
        self.TreeMaker.getVariable('AcdGemCNO_GARC')[0] =\
                       copy(self.cnoVector())
        
    ## @brief Function filling the AcdGemROI_Tower tree variable (used to be gem_roi_vector).
    ## @note This name is inconsistent with the others: requires a change!
    ## @param self
    #  The class instance.

    def AcdGemROI_Tower(self):
        self.TreeMaker.getVariable('AcdGemROI_Tower')[0] =\
                       copy(self.roiVector())

    ## @brief Function filling the gem_cal_le_vector tree variable (used to be gem_cal_le_vector).
    ## @param self
    #  The class instance.

    def CalLoTriggerTower(self):
        self.TreeMaker.getVariable('CalLoTriggerTower')[0] =\
                       copy(self.calLEvector())

    ## @brief Function filling the CalHiTriggerTower tree variable (used to be gem_cal_he_vector).
    ## @param self
    #  The class instance.

    def CalHiTriggerTower(self):
        self.TreeMaker.getVariable('CalHiTriggerTower')[0] =\
                       copy(self.calHEvector())

    ## @brief Function filling the gem_cond_arr_time_tkr tree variable.
    ## @param self
    #  The class instance.

    def condarrtkr(self):
        self.TreeMaker.getVariable('condarrtkr')[0] =\
                       copy(self.condArrTime().tkr())

    ## @brief Function filling the gem_cond_arr_time_cal_le tree variable.
    ## @param self
    #  The class instance.

    def condarrcallo(self):
        self.TreeMaker.getVariable('condarrcallo')[0] =\
                       copy(self.condArrTime().calLE())

    ## @brief Function filling the gem_cond_arr_time_cal_he tree variable.
    ## @param self
    #  The class instance.

    def condarrcalhi(self):
        self.TreeMaker.getVariable('condarrcalhi')[0] =\
                       copy(self.condArrTime().calHE())

    ## @brief Function filling the gem_cond_arr_time_roi tree variable.
    ## @param self
    #  The class instance.

    def condarrroi(self):
        self.TreeMaker.getVariable('condarrroi')[0] =\
                       copy(self.condArrTime().roi())

    ## @brief Function filling the gem_cond_arr_time_cno tree variable.
    ## @param self
    #  The class instance.

    def condarrcno(self):
        self.TreeMaker.getVariable('condarrcno')[0] =\
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




