from copy      import copy
from pGlobals  import *

## @brief Class to handle the Meta part of an event
#
#  The MetaEvent contains some usefull information about
#  the context in which the event was acquired :
#  counters, timestamp, errors

class pMetaEventProcessor:
    ## @brief Constructor
    ## @param self
    #  The class instance.

    def __init__(self, treeMaker):

        ## @var TreeMaker
        ## @brief The TreeMaker object to be filled with the MetaEvent information

        self.TreeMaker = treeMaker
	self.TimeHackRollOverNum = 0
	self.TimeHackHasJustRolledOver = False

    def getVariable(self, name):
        return self.TreeMaker.VariablesDictionary[name]

    def calculateTimeStamp(self, meta):
	timeTics = copy(meta.timeTics())
	timeHack_tics = copy(meta.timeHack().tics())
	timeHack_hacks = copy(meta.timeHack().hacks())
	clockTicksEvt1PPS = timeTics - timeHack_tics	
	if(clockTicksEvt1PPS <0):
	    clockTicksEvt1PPS += CLOCK_ROLLOVER

	#Check for timeHack rollover
	hPrevious = meta.context().previous().timeHack().hacks()
	hCurrent  = meta.context().current().timeHack().hacks()
	if (hCurrent - hPrevious < 0) and not self.TimeHackHasJustRolledOver :
	    self.TimeHackRollOverNum += 1
	    self.TimeHackHasJustRolledOver = True
	if hCurrent - hPrevious > 0:
	   self.TimeHackHasJustRolledOver = False
	
	timestamp = 128*self.TimeHackRollOverNum + timeHack_hacks +  clockTicksEvt1PPS*CLOCK_TIC
	return timestamp

    def process(self, meta):
        self.getVariable('event_timestamp')[0]               = self.calculateTimeStamp(meta)      

	self.getVariable('meta_context_open_action')[0]      = meta.context().open().action()
	self.getVariable('meta_context_open_crate')[0]       = meta.context().open().crate()
	self.getVariable('meta_context_open_datagrams')[0]   = meta.context().open().datagrams()
	self.getVariable('meta_context_open_mode')[0]        = meta.context().open().mode()
	self.getVariable('meta_context_open_modechanges')[0] = meta.context().open().modeChanges()
	self.getVariable('meta_context_open_reason')[0]      = meta.context().open().reason()

	self.getVariable('meta_context_close_action')[0] = meta.context().close().action()
	self.getVariable('meta_context_close_reason')[0] = meta.context().close().reason()

        self.getVariable('meta_context_run_id')[0]        = meta.context().run().id()	       
	self.getVariable('meta_context_run_origin')[0]    = meta.context().run().origin()   
        self.getVariable('meta_context_run_platform')[0]  = meta.context().run().platform()	       
	self.getVariable('meta_context_run_startedat')[0] = meta.context().run().startedAt()   
	      
	self.getVariable('meta_context_gem_scalers_elapsed')[0]   = meta.context().scalers().elapsed()
	self.getVariable('meta_context_gem_scalers_livetime')[0]  = meta.context().scalers().livetime()
	self.getVariable('meta_context_gem_scalers_prescaled')[0] = meta.context().scalers().prescaled()
	self.getVariable('meta_context_gem_scalers_discarded')[0] = meta.context().scalers().discarded()
	self.getVariable('meta_context_gem_scalers_sequence')[0]  = meta.context().scalers().sequence()
	self.getVariable('meta_context_gem_scalers_deadzone')[0]  = meta.context().scalers().deadzone()

	self.getVariable('meta_context_current_incomplete')[0]       = meta.context().current().incomplete()
	self.getVariable('meta_context_current_timesecs')[0]         = meta.context().current().timeSecs()
	self.getVariable('meta_context_current_flywheeling')[0]      = meta.context().current().flywheeling()
	#self.getVariable('meta_context_current_flagsvalid')[0]       = meta.context().current().flagsValid()
	self.getVariable('meta_context_current_missing_gps')[0]      = meta.context().current().missingGps()
	self.getVariable('meta_context_current_missing_cpupps')[0]   = meta.context().current().missingCpuPps()
	self.getVariable('meta_context_current_missing_latpps')[0]   = meta.context().current().missingLatPps()
	self.getVariable('meta_context_current_missing_timetone')[0] = meta.context().current().missingTimeTone()
	self.getVariable('meta_context_current_gem_timehacks')[0]    = meta.context().current().timeHack().hacks()
	self.getVariable('meta_context_current_gem_timeticks')[0]    = meta.context().current().timeHack().tics()

	self.getVariable('meta_context_previous_incomplete')[0]       = meta.context().previous().incomplete()
	self.getVariable('meta_context_previous_timesecs')[0]         = meta.context().previous().timeSecs()
	self.getVariable('meta_context_previous_flywheeling')[0]      = meta.context().previous().flywheeling()
	#self.getVariable('meta_context_previous_flagsvalid')[0]       = meta.context().previous().flagsValid()
	self.getVariable('meta_context_previous_missing_gps')[0]      = meta.context().previous().missingGps()
	self.getVariable('meta_context_previous_missing_cpupps')[0]   = meta.context().previous().missingCpuPps()
	self.getVariable('meta_context_previous_missing_latpps')[0]   = meta.context().previous().missingLatPps()
	self.getVariable('meta_context_previous_missing_timetone')[0] = meta.context().previous().missingTimeTone()
	self.getVariable('meta_context_previous_gem_timehacks')[0]    = meta.context().previous().timeHack().hacks()
	self.getVariable('meta_context_previous_gem_timeticks')[0]    = meta.context().previous().timeHack().tics()

