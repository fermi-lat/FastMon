## @package pEvtMetaContextProcessor
## @brief Class dealing with the evt meta context event.

from copy      import copy
from pGlobals  import *
import math

#To run locally, needs the appropriate setup
from ISOC.ProductUtils import ProductSpan

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

    def __init__(self,treeMaker, errorHandler):

        ## @var TreeMaker
        ## @brief The TreeMaker object which is responsible to fill the tree
        #  with the meta event information.

        ## @var EvtReader
        ## @brief The EvtReader object created by calling LSEReader(filename)
	#  to have access to RunId

        ## @var TimeHackRollOverNum
        ## @brief The number of time hack rollovers.

        ## @var TimeHackHasJustRolledOver
        ## @brief Flag set after a rollover.

        self.TreeMaker    = treeMaker
	self.EvtReader	  = None
	self.ErrorHandler = errorHandler
	self.__localCounter = 0
        self.PreviousHacks = 0
        self.PreviousTics  = 0


    def getVariable(self, varName):
        return self.TreeMaker.getVariable(varName)

    ## @brief Set the EvtReader variable to have access to high level
    #  quantities
    ## @param self
    #  The class instance.
    ## @param evtReader
    ## @brief The evtReader object

    def setEvtReader(self, evtReader):
	self.EvtReader = evtReader


    ## @brief Check the TimeTone information for Errors
    ## This function is called only when the timeHack second has changed.
    ## First check if there is an error in the TimeTone by controlling
    #  the incomplete flag. Then fill in the error handler according to
    #  the error type. 
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta event information.
    ## @param context
    #  The event context information.
    def checkTimeTone(self, meta, context):
        if context.current.incomplete:
	    self.ErrorHandler.fill('TIMETONE_INCOMPLETE', [context.current.timeSecs])
	    if context.current.missingTimeTone:
	        self.ErrorHandler.fill('TIMETONE_MISSING_TIMETONE', [])
	    if context.current.missingCpuPps:
	        self.ErrorHandler.fill('TIMETONE_MISSING_CPUPPS', [])
	    if context.current.missingLatPps:
	        self.ErrorHandler.fill('TIMETONE_MISSING_LATPPS', [])
	    if context.current.flywheeling:
	        self.ErrorHandler.fill('TIMETONE_FLYWHEELING', [])
	    if context.current.earlyEvent:
	        self.ErrorHandler.fill('TIMETONE_EARLY_EVENT', [])
	    if not context.current.sourceGps:
	        self.ErrorHandler.fill('TIMETONE_NULL_SOURCE_GPS', [])
	return 0

    ## @brief Calculate the number of ticks between successive 1-PPS
    #  and get the deviation from the 20 MHz clock.
    #  GEM time base counter is 25bits, we need that to trace back rollovers
    #  Information from the meta event timeHack are used.
    ## The value is initialized to -9999 as default and is overwritten only 
    #  when the second has changed. 
    ## We also take advantage of the knowledge taht second has changed to
    #  check TimeTone errors.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta event information.
    ## @param context
    #  The event context information.

    def getClockTicsDev20MHz(self, meta, context):
        ticsDev = -9999

	ppsCounter = meta.timeHack.hacks
	clockTics  = meta.timeHack.tics

        if (self.PreviousHacks==0 and self.PreviousTics==0):
            self.PreviousHacks = ppsCounter
            self.PreviousTics  = clockTics
	    return -9999
	    
        if (ppsCounter != self.PreviousHacks) :
	    # Check TimeTone errors
	    self.checkTimeTone(meta, context)
	    # Now really checking tics
	    DeltaTics = clockTics - self.PreviousTics
	    if DeltaTics>=0:
	        ticsDev = 20000000 - DeltaTics
	    else:
	        ticsDev = 20000000 - (math.pow(2,25) - 1 -self.PreviousTics + clockTics)

        self.PreviousHacks = ppsCounter
	self.PreviousTics  = clockTics
        return ticsDev

    ## @brief Calculate the absolute timestamp.
    #  The absolute timestamp is calculated here the same way as it is in
    #  the DfiDump.py script.
    #  Absolute time is contained in a datetime.datetime object.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta event information.
    ## @param context
    #  The event context information.

    def calculateTimeStamp(self, meta, context):
	self.__localCounter += 1
        dtics = context.current.timeHack.tics - context.previous.timeHack.tics
        dhacks = (context.current.timeHack.hacks -\
                  context.previous.timeHack.hacks)
        dtics = (dtics + (dhacks-1) * 0x2000000) & 0x01FFFFFF
        dsecs = context.current.timeSecs - context.previous.timeSecs
        if dsecs <= 0: dsecs = 1
        freq  = float(dtics) / float(dsecs)
        elapsed = (meta.timeTics - context.current.timeHack.tics ) & 0x01FFFFFF
        abstics = long(context.current.timeSecs)*long(20000000) + long(elapsed)
        elapsed = int( (float( elapsed ) / freq * 1000000.0) + 0.5 )
        metaPPS = (meta.timeHack.hacks << 25) | meta.timeHack.tics
        currPPS = (context.current.timeHack.hacks << 25) |\
                  context.current.timeHack.tics
        prevPPS = (context.previous.timeHack.hacks << 25) |\
                  context.previous.timeHack.tics
        secs    = context.current.timeSecs 
	tevt = ProductSpan.utcfromtimestamp( secs, elapsed )
        return secs + elapsed/1000000.


    ## @brief Process the lsf meta event.
    ## @param self
    #  The class instance.
    ## @param context
    #  The evt meta context information

    def process(self, meta, context):	
        self.getVariable('event_timestamp')[0]                     =\
                       self.calculateTimeStamp(meta, context)      
        self.getVariable('meta_context_run_id')[0] = \
                       self.EvtReader.runid()  
		            
	self.getVariable('meta_context_open_action')[0]            =\
                       context.open.action
	self.getVariable('meta_context_open_crate')[0]             =\
                       context.open.crate
	self.getVariable('meta_context_open_datagrams')[0]         =\
                       context.open.datagrams
	self.getVariable('meta_context_open_mode')[0]              =\
                       context.open.mode
	self.getVariable('meta_context_open_modechanges')[0]       =\
                       context.open.modeChanges
	self.getVariable('meta_context_open_reason')[0]            =\
                       context.open.reason
	self.getVariable('meta_context_close_action')[0]           =\
                       context.close.action
	self.getVariable('meta_context_close_reason')[0]           =\
                       context.close.reason
	self.getVariable('meta_context_run_origin')[0]             =\
                       context.run.origin   
        self.getVariable('meta_context_run_platform')[0]           =\
                       context.run.platform	       
	self.getVariable('meta_context_run_startedat')[0]          =\
                       context.run.startedAt   
	self.getVariable('meta_context_gem_scalers_elapsed')[0]    =\
                       context.scalers.elapsed
	self.getVariable('meta_context_gem_scalers_livetime')[0]   =\
                       context.scalers.livetime
	self.getVariable('meta_context_gem_scalers_prescaled')[0]  =\
                       context.scalers.prescaled
	self.getVariable('meta_context_gem_scalers_discarded')[0]  =\
                       context.scalers.discarded
	self.getVariable('meta_context_gem_scalers_sequence')[0]   =\
                       context.scalers.sequence
	self.getVariable('meta_context_gem_scalers_deadzone')[0]   =\
                       context.scalers.deadzone
	self.getVariable('meta_context_current_earlyevent')[0]     =\
                       context.current.earlyEvent
	self.getVariable('meta_context_current_incomplete')[0]     =\
                       context.current.incomplete
	self.getVariable('meta_context_current_timesecs')[0]       =\
                       context.current.timeSecs
	self.getVariable('meta_context_current_flywheeling')[0]    =\
                       context.current.flywheeling
	self.getVariable('meta_context_current_source_gps')[0]    =\
                       context.current.sourceGps
	self.getVariable('meta_context_current_missing_cpupps')[0] =\
                       context.current.missingCpuPps
	self.getVariable('meta_context_current_missing_latpps')[0] =\
                       context.current.missingLatPps
	self.getVariable('meta_context_current_missing_timetone')[0]=\
                       context.current.missingTimeTone
	self.getVariable('meta_context_current_gem_timehacks')[0]  =\
                       context.current.timeHack.hacks
	self.getVariable('meta_context_current_gem_timeticks')[0]  =\
                       context.current.timeHack.tics
	self.getVariable('meta_context_previous_earlyevent')[0]     =\
                       context.previous.earlyEvent
	self.getVariable('meta_context_previous_incomplete')[0]    =\
                       context.previous.incomplete
	self.getVariable('meta_context_previous_timesecs')[0]      =\
                       context.previous.timeSecs
	self.getVariable('meta_context_previous_flywheeling')[0]   =\
                       context.previous.flywheeling
	self.getVariable('meta_context_previous_source_gps')[0]   =\
                       context.previous.sourceGps
	self.getVariable('meta_context_previous_missing_cpupps')[0]=\
                       context.previous.missingCpuPps
	self.getVariable('meta_context_previous_missing_latpps')[0]=\
                       context.previous.missingLatPps
	self.getVariable('meta_context_previous_missing_timetone')[0]=\
                       context.previous.missingTimeTone
	self.getVariable('meta_context_previous_gem_timehacks')[0] =\
                       context.previous.timeHack.hacks
	self.getVariable('meta_context_previous_gem_timeticks')[0] =\
                       context.previous.timeHack.tics

        self.getVariable('clocktics_dev_20MHz')[0]             =\
                       self.getClockTicsDev20MHz(meta, context)      


