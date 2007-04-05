## @package pAlarmHandler
## @brief Module managing the data automated alarm system.

import logging
import pUtils
import time

from pGlobals    import *
from pXmlElement import pXmlElement

UNDEFINED_STATUS = 'UNDEFINED'
PASSED_STATUS    = 'PASSED'
WARNING_STATUS   = 'WARNING'
ERROR_STATUS     = 'ERROR'
ALARM_HEADER     = 'Type      Status  Parameter Limits'

## @brief Base class handling all the alarms.

class pAlarmHandler:

    ## @brief Constructor
    ## @param self
    #  The class instance.

    def __init__(self):

        ## @var __EnabledAlarmsDict
        ## @brief Base dictionary containing all the alarms.
        #
        #  The alarms are store as (name, alarms) pairs, where
        #  name is the name of the plot the alarms refer to and alarms
        #  is a list of pAlarm instances set on the plot itself.
        
        self.__EnabledAlarmsDict = {}

    ## @brief Add an alarm for the specified plot.
    ## @param self
    #  The class instance.
    ## @param alarm
    #  The alarm to be added to the dictionary.
    ## @param plotName
    #  The name of the plot the alarm refers to.
        
    def addAlarm(self, alarm, plotName):
        if not alarm.isEnabled():
            return
        if plotName not in self.__EnabledAlarmsDict.keys():
            self.__EnabledAlarmsDict[plotName] = [alarm]
        else:
            self.__EnabledAlarmsDict[plotName].append(alarm)

    ## @brief Activate all the alarms set on a specified plot.
    #
    #  This actually verifies that the plot parameters lie in the desired
    #  ranges.
    ## @param self
    #  The class instance.
    ## @param plot
    #  The plot (a ROOT object),

    def activateAlarms(self, plot):
        try:
            for alarm in self.__EnabledAlarmsDict[plot.GetName()]:
                alarm.activate(plot)
        except KeyError:
            pass

    ## @brief Return true if all the activated alarms are clean.
    ## @param self
    #  The class instance.        

    def allAlarmsClean(self):
        for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
            for alarm in alarmsList:
                if not alarm.isClean():
                    return False
        return True

    ## @brief Return the alarm handler summary, nicely formatted to be
    #  printed on the screen.
    ## @param self
    #  The class instance.
    ## @param verbose
    #  If the flag is set, the status is printed out for all the alarms,
    #  otherwise only for those which are set (i.e. for the plots which do
    #  not satisfy the required conditions).

    def getFormattedSummary(self, verbose=False):
        summary = '** Alarm handler summary **\n'
        if self.allAlarmsClean():
            summary += 'All alarms clean.\n'
        else:
            summary += 'Plot name                        %s\n' % ALARM_HEADER
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += '%s %s\n' %\
                                   (pUtils.expandString(plotName, 32),\
                                    alarm.getFormattedStatus())
                    else:
                        if verbose:
                            summary += '%s %s\n' %\
                                       (pUtils.expandString(plotName, 32),\
                                        alarm.getFormattedStatus())
        return summary

    ## @brief Return the alarm handler summary, in a doxygen-like fashion,
    #  to be included in the report.
    ## @todo Probably some more work is needed here, cause when the
    #  alarms table gets very long, the LaTeX part may screw up.
    #  We may think oh having more tables (one per list of per plot?).
    ## @param self
    #  The class instance.

    def getDoxygenFormattedSummary(self, verbose=False):   
        caption = 'Summary table'
        label   = 'alarmHandlerTable'
        headers = ['Plot name', 'Type', 'Status', 'Parameter', 'Limits']
        summary = '\n@section alarms_summary Alarm handler summary\n\n'
        if self.allAlarmsClean():
            summary += 'All alarms clean.\n'
        else:
            summary += '@htmlonly\n'                                      +\
                       '<table border="1" width="100%">\n'                +\
                       '<caption>%s</caption>\n' % caption                +\
                       '\t<tr>\n'
            for header in headers:
                summary += '\t\t<td>%s</td>\n' % header
            summary += '\t</tr>\n'
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += '\t\t<td>%s</td>\n' % plotName         +\
                                   alarm.getHtmlFormattedStatus()
                    else:
                        if verbose:
                            summary += '\t\t<td>%s</td>\n' % plotName     +\
                                       alarm.getHtmlFormattedStatus()
            summary += '</table>\n'                                       +\
                       '@endhtmlonly\n\n'                                 +\
                       '@latexonly\n'                                     +\
                       '\\begin{table}[!htb]\n'                           +\
                       '\\begin{center}\n'                                +\
                       '\\caption{%s}\n' % caption                        +\
                       '\\label{%s}\n' % label                            +\
                       '\\begin{tabular}{|c|c|c|c|c|}\n'                  +\
                       '\\hline\n'
            for header in headers[:-1]:
                summary += '%s & ' % header
            summary += '%s \\\\\n' % headers[-1]                          +\
                       '\\hline\n'                                        +\
                       '\\hline\n'
            for (plotName, alarmsList) in self.__EnabledAlarmsDict.items():
                for alarm in alarmsList:
                    if not alarm.isClean():
                        summary += pUtils.formatForLatex('%s & %s'        %\
                                   (plotName,                              \
                                    alarm.getLatexFormattedStatus()))     +\
                                    '\\hline\n'
                    else:
                        if verbose:
                            summary += pUtils.formatForLatex('%s & %s'    %\
                                       (plotName,                          \
                                        alarm.getLatexFormattedStatus())) +\
                                    '\\hline\n'
            summary += '\\end{tabular}\n'                                 +\
                       '\\end{center}\n'                                  +\
                       '\\end{table}\n'                                   +\
                       '@endlatexonly\n'
        return '%s\n\n' % summary

    ## @brief Write the doxygen summary to a file, to be included in the
    #  report at a later stage.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The output file path.
    
    def writeDoxygenFormattedSummary(self, filePath):
        logging.info('Writing the alarms file for the report...')
        startTime = time.time()
        file(filePath, 'w').writelines(self.getDoxygenFormattedSummary())
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Class representation.
    ## @param self
    #  The class instance.

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
    ## @param element
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
    ## @todo Some refinement is needed here to handle the cases in which Min
    #  or Max are not defined.
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

    ## @brief Return the Min, Max pair formatted to be printed on the screen.
    ## @param self
    #  The class instance.

    def getFormattedLimits(self):
        return '[%s, %s]' % (self.Min, self.Max)

    ## @brief Return all the relevant information on the alarm status,
    #  nicely formatted.
    ## @param self
    #  The class instance.

    def getFormattedStatus(self):
        return '%s%s%s%s' % (pUtils.expandString(self.Type)      ,\
                             pUtils.expandString(self.Status, 8)    ,\
                             pUtils.expandNumber(self.Parameter) ,\
                             pUtils.expandString(self.getFormattedLimits(),15))

    def getHtmlFormattedStatus(self):
        return '\t\t<td>%s</td>\n' % self.Type      +\
               '\t\t<td>%s</td>\n' % self.Status    +\
               '\t\t<td>%s</td>\n' % self.Parameter +\
               '\t\t<td>%s</td>\n' % self.getFormattedLimits()

    def getLatexFormattedStatus(self):
        return '%s & %s & %s & %s \\\\\n' % (self.Type, self.Status,\
                                             self.Parameter,\
                                             self.getFormattedLimits())
