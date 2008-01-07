## @package pEvtMetaContextProcessor
## @brief Class dealing with the evt meta context event.

from copy      import copy
from pGlobals  import *

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

    def __init__(self,treeMaker):

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
	self.__localCounter = 0


    def getVariable(self, varName):
        return self.TreeMaker.getVariable(varName)

    ## @brief Set the EvtReader variable to have access to high level quantities
    ## @param self
    #  The class instance.
    ## @param evtReader
    ## @brief The evtReader object

    def setEvtReader(self, evtReader):
	self.EvtReader = evtReader

    ## @brief Calculate the absolute timestamp.
    ## @param self
    #  The class instance.
    ## @param context
    #  The event context information.
    ## @brief The absolute timestamp is calculated here the same way as it is in the DfiDump.py script.
    #  Absolute time is contained in a datetime.datetime object
    #  Need to understand how to create a ROOT Tree branch with the absolute time stamp.
    def calculateTimeStamp(self, meta, context):
	self.__localCounter += 1
        dtics = context.current.timeHack.tics - context.previous.timeHack.tics
        dhacks = ( context.current.timeHack.hacks - context.previous.timeHack.hacks )
        dtics = ( dtics + (dhacks-1) * 0x2000000 ) & 0x01FFFFFF
        dsecs = context.current.timeSecs - context.previous.timeSecs
        if dsecs <= 0: dsecs = 1
        freq  = float(dtics) / float(dsecs)
        elapsed = ( meta.timeTics - context.current.timeHack.tics ) & 0x01FFFFFF
        abstics = long(context.current.timeSecs) * long(20000000) + long(elapsed)
        elapsed = int( (float( elapsed ) / freq * 1000000.0) + 0.5 )
        metaPPS = (meta.timeHack.hacks << 25) | meta.timeHack.tics
        currPPS = (context.current.timeHack.hacks << 25) | context.current.timeHack.tics
        prevPPS = (context.previous.timeHack.hacks << 25) | context.previous.timeHack.tics
        secs    = context.current.timeSecs 
        #tevt is a datetime.datetime object containing the absolute timestamp
	tevt = ProductSpan.utcfromtimestamp( secs, elapsed )
	#if self.__localCounter%100 == 0:
	#    print 'seconds\t%d\telapsed %d\t tevt %s' % (secs, elapsed, tevt)
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
	self.getVariable('meta_context_current_incomplete')[0]     =\
                       context.current.incomplete
	self.getVariable('meta_context_current_timesecs')[0]       =\
                       context.current.timeSecs
	self.getVariable('meta_context_current_flywheeling')[0]    =\
                       context.current.flywheeling
	self.getVariable('meta_context_current_missing_gps')[0]    =\
                       context.current.missingGps
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
	self.getVariable('meta_context_previous_incomplete')[0]    =\
                       context.previous.incomplete
	self.getVariable('meta_context_previous_timesecs')[0]      =\
                       context.previous.timeSecs
	self.getVariable('meta_context_previous_flywheeling')[0]   =\
                       context.previous.flywheeling
	self.getVariable('meta_context_previous_missing_gps')[0]   =\
                       context.previous.missingGps
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


