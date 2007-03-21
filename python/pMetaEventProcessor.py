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
        self.getVariable('meta_context_run_id')[0]           = meta.context().run().id()
	self.getVariable('meta_context_run_startedAt')[0]    = meta.context().run().startedAt()
	self.getVariable('meta_context_scalers_livetime')[0] = meta.context().scalers().livetime()
	self.getVariable('meta_context_open_crate')[0]       = meta.context().open().crate()


