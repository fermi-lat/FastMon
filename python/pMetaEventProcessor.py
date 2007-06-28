## @package pMetaEventProcessor
## @brief Class dealing with the lsf meta event.

from copy      import copy
from pGlobals  import *

## @brief Class to handle the lsf meta event.
#
#  The meta event contains some usefull information about the context
#  in which the event was acquired: counters, timestamp, errors...

class pMetaEventProcessor:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for filling the ROOT tree.

    def __init__(self, treeMaker):

        ## @var TreeMaker
        ## @brief The TreeMaker object which is responsible to fill the tree
        #  with the meta event information.

        ## @var TimeHackRollOverNum
        ## @brief The number of time hack rollovers.

        ## @var TimeHackHasJustRolledOver
        ## @brief Flag set after a rollover.

        self.TreeMaker                 = treeMaker
	self.TimeHackRollOverNum       = 0
	self.TimeHackHasJustRolledOver = False

    ## @brief Calculate the timestamp.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The lsf meta event.

    def calculateTimeStamp(self, meta):
	timeTics = copy(meta.timeTics())
	timeHack_tics = copy(meta.timeHack().tics())
	timeHack_hacks = copy(meta.timeHack().hacks())
	clockTicksEvt1PPS = timeTics - timeHack_tics	
	if(clockTicksEvt1PPS <0):
	    clockTicksEvt1PPS += CLOCK_ROLLOVER
	hPrevious = meta.context().previous().timeHack().hacks()
	hCurrent  = meta.context().current().timeHack().hacks()
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
    ## @param meta
    #  The lsf meta event.

    def process(self, meta):
        self.TreeMaker.getVariable('event_timestamp')[0]                     =\
                       self.calculateTimeStamp(meta)      
	self.TreeMaker.getVariable('meta_context_open_action')[0]            =\
                       meta.context().open().action()
	self.TreeMaker.getVariable('meta_context_open_crate')[0]             =\
                       meta.context().open().crate()
	self.TreeMaker.getVariable('meta_context_open_datagrams')[0]         =\
                       meta.context().open().datagrams()
	self.TreeMaker.getVariable('meta_context_open_mode')[0]              =\
                       meta.context().open().mode()
	self.TreeMaker.getVariable('meta_context_open_modechanges')[0]       =\
                       meta.context().open().modeChanges()
	self.TreeMaker.getVariable('meta_context_open_reason')[0]            =\
                       meta.context().open().reason()
	self.TreeMaker.getVariable('meta_context_close_action')[0]           =\
                       meta.context().close().action()
	self.TreeMaker.getVariable('meta_context_close_reason')[0]           =\
                       meta.context().close().reason()
        self.TreeMaker.getVariable('meta_context_run_id')[0]                 =\
                       meta.context().run().id()	       
	self.TreeMaker.getVariable('meta_context_run_origin')[0]             =\
                       meta.context().run().origin()   
        self.TreeMaker.getVariable('meta_context_run_platform')[0]           =\
                       meta.context().run().platform()	       
	self.TreeMaker.getVariable('meta_context_run_startedat')[0]          =\
                       meta.context().run().startedAt()   
	self.TreeMaker.getVariable('meta_context_gem_scalers_elapsed')[0]    =\
                       meta.context().scalers().elapsed()
	self.TreeMaker.getVariable('meta_context_gem_scalers_livetime')[0]   =\
                       meta.context().scalers().livetime()
	self.TreeMaker.getVariable('meta_context_gem_scalers_prescaled')[0]  =\
                       meta.context().scalers().prescaled()
	self.TreeMaker.getVariable('meta_context_gem_scalers_discarded')[0]  =\
                       meta.context().scalers().discarded()
	self.TreeMaker.getVariable('meta_context_gem_scalers_sequence')[0]   =\
                       meta.context().scalers().sequence()
	self.TreeMaker.getVariable('meta_context_gem_scalers_deadzone')[0]   =\
                       meta.context().scalers().deadzone()
	self.TreeMaker.getVariable('meta_context_current_incomplete')[0]     =\
                       meta.context().current().incomplete()
	self.TreeMaker.getVariable('meta_context_current_timesecs')[0]       =\
                       meta.context().current().timeSecs()
	self.TreeMaker.getVariable('meta_context_current_flywheeling')[0]    =\
                       meta.context().current().flywheeling()
	self.TreeMaker.getVariable('meta_context_current_missing_gps')[0]    =\
                       meta.context().current().missingGps()
	self.TreeMaker.getVariable('meta_context_current_missing_cpupps')[0] =\
                       meta.context().current().missingCpuPps()
	self.TreeMaker.getVariable('meta_context_current_missing_latpps')[0] =\
                       meta.context().current().missingLatPps()
	self.TreeMaker.getVariable('meta_context_current_missing_timetone')[0]=\
                       meta.context().current().missingTimeTone()
	self.TreeMaker.getVariable('meta_context_current_gem_timehacks')[0]  =\
                       meta.context().current().timeHack().hacks()
	self.TreeMaker.getVariable('meta_context_current_gem_timeticks')[0]  =\
                       meta.context().current().timeHack().tics()
	self.TreeMaker.getVariable('meta_context_previous_incomplete')[0]    =\
                       meta.context().previous().incomplete()
	self.TreeMaker.getVariable('meta_context_previous_timesecs')[0]      =\
                       meta.context().previous().timeSecs()
	self.TreeMaker.getVariable('meta_context_previous_flywheeling')[0]   =\
                       meta.context().previous().flywheeling()
	self.TreeMaker.getVariable('meta_context_previous_missing_gps')[0]   =\
                       meta.context().previous().missingGps()
	self.TreeMaker.getVariable('meta_context_previous_missing_cpupps')[0]=\
                       meta.context().previous().missingCpuPps()
	self.TreeMaker.getVariable('meta_context_previous_missing_latpps')[0]=\
                       meta.context().previous().missingLatPps()
	self.TreeMaker.getVariable('meta_context_previous_missing_timetone')[0]=\
                       meta.context().previous().missingTimeTone()
	self.TreeMaker.getVariable('meta_context_previous_gem_timehacks')[0] =\
                       meta.context().previous().timeHack().hacks()
	self.TreeMaker.getVariable('meta_context_previous_gem_timeticks')[0] =\
                       meta.context().previous().timeHack().tics()


