## @package pEvtMetaContextProcessor
## @brief Class dealing with the evt meta context event.

from copy      import copy
from pGlobals  import *

## @brief Class to handle the evt meta context event.
#
#  The meta event contains some usefull information about the context
#  in which the event was acquired: counters, timestamp, errors...

class pEvtMetaContextProcessor:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for filling the ROOT tree.

    def __init__(self,treeMaker):

        ## @var TreeMaker
        ## @brief The TreeMaker object which is responsible to fill the tree
        #  with the meta event information.

        ## @var EvtReader
        ## @brief The EvtReader object created by calling LSEReader(filename)

        ## @var TimeHackRollOverNum
        ## @brief The number of time hack rollovers.

        ## @var TimeHackHasJustRolledOver
        ## @brief Flag set after a rollover.

        self.TreeMaker                 = treeMaker
	self.EvtReader		       = None
	self.TimeHackRollOverNum       = 0
	self.TimeHackHasJustRolledOver = False

    ## @brief Set the EvtReader variable to have access to high level quantities
    ## @param self
    #  The class instance.
    ## @param evtReader
    ## @brief The evtReader object

    def setEvtReader(self, evtReader):
	self.EvtReader = evtReader

    ## @brief Calculate the timestamp.
    ## @param self
    #  The class instance.
    ## @param context
    #  The event context information.

    def calculateTimeStamp(self, meta, context):	
	timeTics = meta.timeTics
	timeHack_tics = meta.timeHack.tics
	timeHack_hacks = meta.timeHack.hacks	
	clockTicksEvt1PPS = timeTics - timeHack_tics	
	if(clockTicksEvt1PPS <0):
	    clockTicksEvt1PPS += CLOCK_ROLLOVER
	hPrevious = context.previous.timeHack.hacks
	hCurrent  = context.current.timeHack.hacks
	if (hCurrent - hPrevious < 0) and not self.TimeHackHasJustRolledOver :
	    self.TimeHackRollOverNum += 1
	    self.TimeHackHasJustRolledOver = True
	if hCurrent - hPrevious > 0:
	   self.TimeHackHasJustRolledOver = False
	timestamp = 128*self.TimeHackRollOverNum + timeHack_hacks +\
                    clockTicksEvt1PPS*CLOCK_TIC
	return timestamp

    ## @brief Process the lsf meta event.
    ## @param self
    #  The class instance.
    ## @param context
    #  The evt meta context information

    def process(self, meta, context):
        self.TreeMaker.getVariable('event_timestamp')[0]                     =\
                       self.calculateTimeStamp(meta, context)      
        self.TreeMaker.getVariable('meta_context_run_id')[0]                 =\
                       self.EvtReader.runid()  
		            
	self.TreeMaker.getVariable('meta_context_open_action')[0]            =\
                       context.open.action
	self.TreeMaker.getVariable('meta_context_open_crate')[0]             =\
                       context.open.crate
	self.TreeMaker.getVariable('meta_context_open_datagrams')[0]         =\
                       context.open.datagrams
	self.TreeMaker.getVariable('meta_context_open_mode')[0]              =\
                       context.open.mode
	self.TreeMaker.getVariable('meta_context_open_modechanges')[0]       =\
                       context.open.modeChanges
	self.TreeMaker.getVariable('meta_context_open_reason')[0]            =\
                       context.open.reason
	self.TreeMaker.getVariable('meta_context_close_action')[0]           =\
                       context.close.action
	self.TreeMaker.getVariable('meta_context_close_reason')[0]           =\
                       context.close.reason
	self.TreeMaker.getVariable('meta_context_run_origin')[0]             =\
                       context.run.origin   
        self.TreeMaker.getVariable('meta_context_run_platform')[0]           =\
                       context.run.platform	       
	self.TreeMaker.getVariable('meta_context_run_startedat')[0]          =\
                       context.run.startedAt   
	self.TreeMaker.getVariable('meta_context_gem_scalers_elapsed')[0]    =\
                       context.scalers.elapsed
	self.TreeMaker.getVariable('meta_context_gem_scalers_livetime')[0]   =\
                       context.scalers.livetime
	self.TreeMaker.getVariable('meta_context_gem_scalers_prescaled')[0]  =\
                       context.scalers.prescaled
	self.TreeMaker.getVariable('meta_context_gem_scalers_discarded')[0]  =\
                       context.scalers.discarded
	self.TreeMaker.getVariable('meta_context_gem_scalers_sequence')[0]   =\
                       context.scalers.sequence
	self.TreeMaker.getVariable('meta_context_gem_scalers_deadzone')[0]   =\
                       context.scalers.deadzone
	self.TreeMaker.getVariable('meta_context_current_incomplete')[0]     =\
                       context.current.incomplete
	self.TreeMaker.getVariable('meta_context_current_timesecs')[0]       =\
                       context.current.timeSecs
	self.TreeMaker.getVariable('meta_context_current_flywheeling')[0]    =\
                       context.current.flywheeling
	self.TreeMaker.getVariable('meta_context_current_missing_gps')[0]    =\
                       context.current.missingGps
	self.TreeMaker.getVariable('meta_context_current_missing_cpupps')[0] =\
                       context.current.missingCpuPps
	self.TreeMaker.getVariable('meta_context_current_missing_latpps')[0] =\
                       context.current.missingLatPps
	self.TreeMaker.getVariable('meta_context_current_missing_timetone')[0]=\
                       context.current.missingTimeTone
	self.TreeMaker.getVariable('meta_context_current_gem_timehacks')[0]  =\
                       context.current.timeHack.hacks
	self.TreeMaker.getVariable('meta_context_current_gem_timeticks')[0]  =\
                       context.current.timeHack.tics
	self.TreeMaker.getVariable('meta_context_previous_incomplete')[0]    =\
                       context.previous.incomplete
	self.TreeMaker.getVariable('meta_context_previous_timesecs')[0]      =\
                       context.previous.timeSecs
	self.TreeMaker.getVariable('meta_context_previous_flywheeling')[0]   =\
                       context.previous.flywheeling
	self.TreeMaker.getVariable('meta_context_previous_missing_gps')[0]   =\
                       context.previous.missingGps
	self.TreeMaker.getVariable('meta_context_previous_missing_cpupps')[0]=\
                       context.previous.missingCpuPps
	self.TreeMaker.getVariable('meta_context_previous_missing_latpps')[0]=\
                       context.previous.missingLatPps
	self.TreeMaker.getVariable('meta_context_previous_missing_timetone')[0]=\
                       context.previous.missingTimeTone
	self.TreeMaker.getVariable('meta_context_previous_gem_timehacks')[0] =\
                       context.previous.timeHack.hacks
	self.TreeMaker.getVariable('meta_context_previous_gem_timeticks')[0] =\
                       context.previous.timeHack.tics


