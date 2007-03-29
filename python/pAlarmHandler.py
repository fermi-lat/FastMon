## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import logging

from pGlobals    import *
from pXmlElement import pXmlElement

UNDEFINED_STATUS = 'UNDEFINED'
PASSED_STATUS    = 'PASSED'
WARNING_STATUS   = 'WARNING'
ERROR_STATUS     = 'ERROR'
ALARM_HEADER     = 'Type       Status     Parameter  Limits'

## @brief Base class handling all the alarms.

class pAlarmHandler:

    ## @brief Constructor
    ## @param self
    #  The class instance.

    def __init__(self):
        self.__EnabledAlarmsDict = {}

    def addAlarm(self, alarm, plotName):
        if not alarm.isEnabled():
            return
        if plotName not in self.__EnabledAlarmsDict.keys():
            self.__EnabledAlarmsDict[plotName] = [alarm]
        else:
            self.__EnabledAlarmsDict[plotName].append(alarm)

    def activateAlarms(self, plot):
        try:
            for alarm in self.__EnabledAlarmsDict[plot.GetName()]:
                alarm.activate(plot)
        except KeyError:
            pass

    ## @todo Put this in util module.

    def xpand(self, object, length):
        string = '%s' % object
        if len(string) > length:
            return string[:length]
        numSpaces = length - len(string)
        return '%s%s' % (string, ' '*numSpaces)

    def getFormattedSummary(self, verbose=False):
        header  = 'Plot name                    %s' % ALARM_HEADER
        summary = '** Alarm handler summary **\n%s\n' % header
        for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
             for alarm in alarmsList:
                 summary += '%s %s\n' %\
                            (self.xpand(plotName, 28),\
                             alarm.getFormattedStatus())
        return summary

    def __str__(self):
        return self.getFormattedSummary()


## @brief Class describing an alarm to be activated on a plot.
#
#  The basic idea, here, is that the alarm must verify whether a simple
#  plot parameter (average value or RMS of a histogram,
#  etc., depending on the alarm type) lies or not within a specified interval.
## @todo Should we support more sophisticated alarms?
## @todo Should we support multiple-level alarms?

class pAlarm(pXmlElement):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## element
    #  The xml element from which the alarm is constructed.
    
    def __init__(self, element):

        ## @var Type
        ## @brief The type of the alarm.
        #
        #  By default, it is assumed that a member function whose name is
        #  identical to the Type variable exists. In that case the function
        #  is called when the alarm is activated. An error message is
        #  printed otherwise.

        ## @var Min
        ## @brief The minimum value for the plot parameter on which the alarm
        #  is set.

        ## @var Max
        ## @brief The maximum value for the plot parameter on which the alarm
        #  is set.

        ## @var Parameter
        ## @brief The plot parameter the alarm is set on.

        ## @var Status
        ## @brief The status of the alarm.
        #
        #  Set to UNDEFINED_STATUS in the constructor, it is in general
        #  overwritten when the activate() method is called.
        
        pXmlElement.__init__(self, element)
        self.Type      = self.getAttribute('type')
        self.Min       = self.evalTagValue('min')
        self.Max       = self.evalTagValue('max')
        self.Parameter = None
        self.Status    = UNDEFINED_STATUS

    ## @brief Return True if the alarm Status is PASSED_STATUS.
    ## @param self
    #  The class instance.

    def isClean(self):
        return (self.Status == PASSED_STATUS)

    ## @brief Activate the alarm (i.e. actually verify the plot).
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot against which the alarm is set.

    def activate(self, plot):
        try:
            eval('self.%s(plot)' % self.Type)
        except:
            logging.error('Function %s() not implemented in the alarms.' %\
                          self.Type)

    ## @brief Check if the Parameter member lies in the [Min, Max] interval
    #  and set the Status accordingly.
    ## @param self
    #  The class instance.

    def __checkParameter(self):
        if (self.Parameter > self.Min) and (self.Parameter < self.Max):
            self.Status = PASSED_STATUS
        else:
            self.Status = ERROR_STATUS

    ## @brief Verify whether the average x value of a plot lies in a
    #  specific interval.
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot against which the alarm is set.    

    def xaverage(self, plot):
        self.Parameter = plot.GetMean()
        self.__checkParameter()

    ## @brief Verify whether the rms of the x values of a plot lies in a
    #  specific interval.
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot against which the alarm is set. 

    def xrms(self, plot):
        self.Parameter = plot.GetRMS()
        self.__checkParameter()

    ## @todo Put this in util module.

    def xpand(self, object, length=10):
        string = '%s' % object
        if len(string) > length:
            return string[:length]
        numSpaces = length - len(string)
        return '%s%s' % (string, ' '*numSpaces)

    ## @brief Return the Min, Max pair formatted to be printed on the screen.
    ## @param self
    #  The class instance.

    def getFormattedLimits(self):
        return '[%s, %s]' % (self.Min, self.Max)

    ## @brief Return the Parameter member formatted to be printed on
    #  the screen.
    ## @param self
    #  The class instance.

    def getFormattedParameter(self):
        return '%.3f' % self.Parameter

    ## @brief Return all the relevant information on the alarm status,
    #  nicely formatted.
    ## @param self
    #  The class instance.

    def getFormattedStatus(self):
        return '%s %s %s %s' % (self.xpand(self.Type)                   ,\
                                self.xpand(self.Status)                 ,\
                                self.xpand(self.getFormattedParameter()),\
                                self.getFormattedLimits())
