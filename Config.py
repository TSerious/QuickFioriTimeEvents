from enum import Enum
from configparser import ConfigParser
from os.path import exists
import logging
import os

configFileName = 'config.ini'
defaultFirefoxBinaryPath = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
defaultEdgeBinaryPath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'

class Order(Enum):
    Seperator = '|'
    Line = '---'
    Quit = 'Quit'
    Arrive = 'Arrive'
    Leave = 'Leave'
    StartPause = 'Start Pause'
    StartPauseAndShutdown = 'Start Pause and '
    EndPause = 'End Pause'
    ShowWorkTime = 'Show work time'
    LeaveLoggedAndArrive = "Arrive (submit Leave)"
    LeaveAndShutdown = 'Leave and '
    LogLeave = 'Log Leave'
    LogLeaveAndShutdown = 'Log Leave and '
    GetCurrentState = 'Update state'
    SetDefaultIcon = 'Reset icon'
    OpenConfig = 'Open config file'
    OpenReadme = 'Open documentation'

    def get_name(value) -> str:
        values = str(value).split('.')

        if len(values) > 0:
            return values[-1]

        return values[0]

    def get_elements() -> str:
        return \
            Order.Line.value + "," + \
            Order.get_name(Order.Quit) + "," + \
            Order.get_name(Order.Arrive) + "," + \
            Order.get_name(Order.Leave) + "," + \
            Order.get_name(Order.StartPause) + "," + \
            Order.get_name(Order.StartPauseAndShutdown) + "," + \
            Order.get_name(Order.EndPause) + "," + \
            Order.get_name(Order.ShowWorkTime) + "," + \
            Order.get_name(Order.LeaveLoggedAndArrive) + "," + \
            Order.get_name(Order.LeaveAndShutdown) + "," + \
            Order.get_name(Order.LogLeave) + "," + \
            Order.get_name(Order.LogLeaveAndShutdown) + "," + \
            Order.get_name(Order.GetCurrentState) + "," + \
            Order.get_name(Order.SetDefaultIcon) + "," + \
            Order.get_name(Order.OpenConfig) + "," + \
            Order.get_name(Order.OpenReadme)

class Sections(Enum):
    State = 'State'
    ArriveLeave = 'ArriveLeave'
    General = 'General'

class State(Enum):
    LastArriveDateTime = 'LastArriveDateTime'
    LastLeaveDateTime = 'LastLeaveDateTime'
    LastPing = 'LastPing'
    IsPause = 'IsPause'
    LastPauseDateTime = 'LastPauseDateTime'
    AccumulatedPauseTime = 'AccumulatedPauseTime'
    LoggedLeaveDateTime = 'LoggedLeaveDateTime'

class General(Enum):
    MinLogLevel = 'MinLogLevel'
    ClearLog = 'ClearLog'
    WaitTimeAfterPageLoad = 'WaitTimeAfterPageLoad'
    Url = 'Url'
    UrlHome = 'UrlHome'
    UrlTime = 'UrlTime'
    Driver = 'Driver'
    ProfilePath = 'ProfilePath'
    BinaryPath = 'BinaryPath'
    CheckProfilePath = 'CheckProfilePath'
    ArriveEvent = 'ArriveEvent'
    LeaveEvent = 'LeaveEvent'
    PauseStartEvent = 'PauseStartEvent'
    PauseStartCommand = 'PauseStartCommand'
    PauseEndEvent = 'PauseEndEvent'
    ShutdownCommand = 'ShutdownCommand'
    CloseInstance = 'CloseInstance'
    ShowWorkTimeOnLeftClick = 'ShowWorkTimeOnLeftClick'
    Order = 'Order'

class ArriveLeave(Enum):
    Approve = 'Approve'
    ArriveOffset = 'ArriveOffset'
    LeaveOffset = 'LeaveOffset'
    LeaveLogOffset = 'LeaveLogOffset'
    StartPauseOffset = 'StartPauseOffset'
    EndPauseOffset = 'EndPauseOffset'

def save(config: ConfigParser):
    with open(configFileName, 'w') as configfile:
        config.write(configfile)

class Settings:
    def __init__(self):
        self.load()
        logging.debug("Settings loaded.")

    def load(self):
        self.config = ConfigParser(comment_prefixes="#")
        self.config.optionxform = lambda option: option  # preserve case for letters

        if exists(configFileName):
            logging.debug("Reading existing configuration: " + configFileName)
            self.config.read(configFileName)
        else:
            self.create_default_config()
            self.save()

    def save(self):
        save(self.config)
        logging.debug("Settings saved.")

    def open_file(self):
        os.startfile(configFileName,operation='edit')

    def get(self, section:Sections, option:General|ArriveLeave|State) -> str:

        try:
            return self.config.get(section.value, option.value)
        except:
            logging.error("Couldn't get " + option.value)
            return ''

    def set(self, section:Sections, option:General|ArriveLeave|State, value, comment:str|None = None):
        optionName = option.value
        
        # Writing comments to ini doesn't work propertly!   
        #if (comment != None) and len(comment) > 0:
        #    optionName = "# " + comment + "\n" + optionName

        self.config.set(section.value, optionName, value)
        logging.debug("Setting [" + section.value + "] " + optionName + " to " + value)
        self.save()

    def create_default_config(self):
        logging.debug("Creating default configuration...")

        self.config.add_section(Sections.ArriveLeave.value)
        self.set(Sections.ArriveLeave, ArriveLeave.Approve, str(True), 'A value indicating whether the event shall be approved. Only approved events are stored in fiori. Set to False to approve manual.')
        self.set(Sections.ArriveLeave, ArriveLeave.ArriveOffset, '-5', 'Minutes that will be added to the arrive time. Negative values are possible.')
        self.set(Sections.ArriveLeave, ArriveLeave.LeaveOffset, '0', 'Minutes that will be added to the leave time. Negative values are possible.')
        self.set(Sections.ArriveLeave, ArriveLeave.LeaveLogOffset, '5', 'Minutes that will be added to the leave time. Negative values are possible.')
        self.set(Sections.ArriveLeave, ArriveLeave.StartPauseOffset, '0', 'Minutes that will be added to the pause start time. Negative values are possible.')
        self.set(Sections.ArriveLeave, ArriveLeave.EndPauseOffset, '0', 'Minutes that will be added to the pause end time. Negative values are possible.')

        self.config.add_section(Sections.General.value)
        self.set(Sections.General, General.MinLogLevel, '10', 'The minimum level of log entries. CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0')
        self.set(Sections.General, General.ClearLog, str(True), 'A value indicating whether the log shall be deleted each time the software starts.')
        self.set(Sections.General, General.WaitTimeAfterPageLoad, '10', 'The time in seconds to wait after the initial page is loaded in the browser instance.')
        self.set(Sections.General, General.Url, '', 'The (base) url of Fiori.')
        self.set(Sections.General, General.UrlHome, '#Shell-home', "The path to the 'Home' page.")
        self.set(Sections.General, General.UrlTime, '?appState=lean#TimeEntry-change', "The path to the 'Time' page.")
        self.set(Sections.General, General.Driver, '', 'Defines which driver to use. Currently supported are Firefox and Edge')
        self.set(Sections.General, General.ProfilePath, '', 'The path where the firefox profile is stored.')
        self.set(Sections.General, General.BinaryPath, '', 'The path where the firefox executable us located.')
        self.set(Sections.General, General.CheckProfilePath, str(True), "A value whether to check if '" + General.BinaryPath.value + "' is set.")
        self.set(Sections.General, General.ArriveEvent, 'P10', 'The arrive event indentifier.')
        self.set(Sections.General, General.LeaveEvent, 'P20', 'The leave event indentifier.')
        self.set(Sections.General, General.PauseStartEvent, 'P15', 'The pause start event indentifier.')
        self.set(Sections.General, General.PauseEndEvent, 'P25', 'The pause end event indentifier.')
        self.set(Sections.General, General.PauseStartCommand, 'shutdown.exe /h', "The shutdown command. '/h' means hybernate instead of normal shutdown.")
        self.set(Sections.General, General.ShutdownCommand, 'shutdown.exe /h', "The shutdown command. '/h' means hybernate instead of normal shutdown.")
        self.set(Sections.General, General.CloseInstance, str(True), 'A value indicating whether the browser instance should be quit after the event has been created.')
        self.set(Sections.General, General.ShowWorkTimeOnLeftClick, str(True), 'A value indicating whether a left click on the icon shows the current work time.')

        self.config.add_section(Sections.State.value)
        self.set(Sections.State, State.LastArriveDateTime, '', 'The date and time the arrive event was set the last time.')
        self.set(Sections.State, State.LastLeaveDateTime, '', 'The date and time the leave event was set the last time.')
        self.set(Sections.State, State.LastPing, '', 'The date and time of the last interaction with the software.')
        self.set(Sections.State, State.IsPause, str(False), 'A value indicating whether you are currently in a pause.')
        self.set(Sections.State, State.LastPauseDateTime, '', 'The date and time of the last pause start event.')
        self.set(Sections.State, State.AccumulatedPauseTime, '0', 'The time in seconds the user has been in a pause.')
        self.set(Sections.State, State.LoggedLeaveDateTime, '', 'The date and time of the leave event that will be created when using LeaveAndArrive')

        order = \
            Order.get_name(Order.Quit) + Order.Seperator.value + \
            Order.Line.value + Order.Seperator.value + \
            Order.get_name(Order.Arrive) + Order.Seperator.value + \
            Order.get_name(Order.Leave) + Order.Seperator.value + \
            Order.get_name(Order.LeaveAndShutdown) + Order.Seperator.value + \
            Order.Line.value + Order.Seperator.value + \
            Order.get_name(Order.StartPause) + Order.Seperator.value + \
            Order.get_name(Order.StartPauseAndShutdown) + Order.Seperator.value + \
            Order.get_name(Order.EndPause) + Order.Seperator.value + \
            Order.Line.value + Order.Seperator.value + \
            Order.get_name(Order.LeaveLoggedAndArrive) + Order.Seperator.value + \
            Order.get_name(Order.LogLeave) + Order.Seperator.value + \
            Order.get_name(Order.LogLeaveAndShutdown) + Order.Seperator.value + \
            Order.Line.value + Order.Seperator.value + \
            Order.get_name(Order.GetCurrentState) + Order.Seperator.value + \
            Order.get_name(Order.SetDefaultIcon) + Order.Seperator.value + \
            Order.get_name(Order.OpenConfig) + Order.Seperator.value + \
            Order.get_name(Order.OpenReadme) + Order.Seperator.value + \
            Order.Line.value + Order.Seperator.value + \
            Order.get_name(Order.ShowWorkTime)

        orderComment = \
            "The order of the elemnts in the right click menu of the icon. " + \
            "Each element is seperated with '|'. " + \
            "Possible elements: " + Order.get_elements()

        self.set(Sections.General, General.Order, order, orderComment)

        logging.debug("Default configuration created.")