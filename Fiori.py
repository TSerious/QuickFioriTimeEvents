import logging
import shutil
import sys
import traceback
from bs4 import BeautifulSoup
import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile;
from selenium.webdriver.edge.options import Options as edOptions
from selenium.webdriver.common.keys import Keys
from subprocess import CREATE_NO_WINDOW
import time
from Config import Settings;
import Config;
from enum import Enum
import DatetimeConverters as dtConvert
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
from win32api import GetFileVersionInfo, HIWORD, LOWORD
from packaging import version as vs

class Driver(Enum):
    Firefox = "Firefox"
    Edge = "Edge"
    NotDefined = "NotDefined"

class FioriEvent(Enum):
    NotDefined = 0
    Arrive = 10
    PauseStart = 15
    Leave = 20
    PauseEnd = 25
    Aborted = 666

    def is_arrive(value:str) -> bool:
        return value.__contains__("Kommen") or value.__contains__("Clock-in")

    def is_leave(value:str) -> bool:
        return value.__contains__("Gehen") or value.__contains__("Clock-out")

    def is_pause_start(value:str) -> bool:
        return value.__contains__("Beginn Pause") or value.__contains__("Start of break")
    
    def is_pause_end(value:str) -> bool:
        return value.__contains__("Ende Pause") or value.__contains__("End of break")
    
    def is_aborted(value:str) -> bool:
        return value.__contains__("Abgebrochen") or value.__contains__("Canceled")
    
    def get_event(value:str):

        if FioriEvent.is_arrive(value):
            return FioriEvent.Arrive

        if FioriEvent.is_leave(value):
            return FioriEvent.Leave
        
        if FioriEvent.is_pause_start(value):
            return FioriEvent.PauseStart
        
        if FioriEvent.is_pause_end(value):
            return FioriEvent.PauseEnd
        
        if FioriEvent.is_aborted(value):
            return FioriEvent.Aborted
        
        return FioriEvent.NotDefined

class FioriState:
    IsArrived:bool = False
    ArriveDateTime:datetime = None
    IsLeft:bool = False
    LeaveDateTime:datetime = None
    IsPaused:bool = False
    AccumulatedPauseSeconds:float = 0
    PauseStartTime:datetime = None

class DriverSettings:
    def __init__(self, type:Driver, profilePath:str, binaryPath:str, url:str, urlHome:str, urlTime:str, driverVersion:str, driverPath:str):
        self._profilePath = profilePath
        self._binaryPath = binaryPath
        self._url = url
        self._urlHome = urlHome
        self._urlTime = urlTime
        self._type = type
        self._driverVersion = driverVersion
        self._driverPath = driverPath

        os.environ['WDM_PROGRESS_BAR'] = str(0)

        if type == Driver.Firefox:
            self._driverManager = GeckoDriverManager(path = r".\\Drivers")
        elif type == Driver.Edge:
            self._driverManager = EdgeChromiumDriverManager(path = r".\\Drivers")
            #self._driverManager.edgechromium_driver_base_url = "https://msedgewebdriverstorage.blob.core.windows.net/edgewebdriver?maxresults=4000&comp=list"#&timeout=60000&startAt=10000"
        else:
            self._driverManager = None

    @property
    def url(self):
        return self._url

    @property
    def url_home(self):
        return self._urlHome
    @property
    def url_time(self):
        return self._urlTime

    @property
    def profile_path(self):
        return self._profilePath

    @property
    def binary_path(self):
        return self._binaryPath
    
    @property
    def type(self):
        return self._type

    def get_url_home(self):
        return self.url + self.url_home

    def get_url_time(self):
        return self.url + self.url_time
    
def get_driver(driverSettings: DriverSettings, settings:Settings, closeInstance:bool) -> BaseWebDriver:

    driver:BaseWebDriver = None

    if driverSettings.type == Driver.Firefox:
        driver = get_firefox_driver(driverSettings, settings)
    
    if driverSettings.type == Driver.Edge:
        driver = get_edge_driver(driverSettings, settings)

    if driver == None:
        raise Exception("Couldn't creat a web driver.")

    driver.minimize_window()
    driver.get(driverSettings.get_url_home())

    if (driver.title.startswith('Sign in to your account')):
        if closeInstance:
            driver.quit()

        raise Exception("Sign in is required")

    return driver

def get_version_number(file_path):
  
    file_information = GetFileVersionInfo(file_path, "\\")
  
    ms_file_version = file_information['FileVersionMS']
    ls_file_version = file_information['FileVersionLS']
  
    versionInfo = [str(HIWORD(ms_file_version)), str(LOWORD(ms_file_version)),str(HIWORD(ls_file_version)), str(LOWORD(ls_file_version))]

    version = ".".join(versionInfo)

    return version

def update_driver(driverSettings:DriverSettings, settings:Settings, useLatest:bool):

    if driverSettings._driverManager == None:
        raise Exception("No web driver manager available.")

    installedDriverVersion = get_version_number(driverSettings._binaryPath)

    if not useLatest:
        if driverSettings.type == Driver.Firefox:
            driverSettings._driverManager = GeckoDriverManager(version=installedDriverVersion, path = r".\\Drivers")
        elif driverSettings.type == Driver.Edge:
            driverSettings._driverManager = EdgeChromiumDriverManager(version=installedDriverVersion, path = r".\\Drivers")
    
    download_driver(driverSettings)

    settings.set(Config.Sections.State, Config.State.DriverVersion, get_version_number(driverSettings._binaryPath))
    settings.set(Config.Sections.State, Config.State.DriverPath, driverSettings._driverPath)

def download_driver(driverSettings:DriverSettings):

    logging.debug(f"current driver path is: {driverSettings._driverPath}")

    try:
        logging.debug("about to install driver")
        newPath = driverSettings._driverManager.install()
        driverSettings._driverPath = newPath
        logging.debug("driver installed")
    except Exception as e:
        logging.debug(f"failed to install driver: {e}")
        with open('tb.txt', 'w+') as f:
            traceback.print_exc(None, f, True)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=None, file=f)

            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                limit=None, file=f)
        
        logging.debug(f"failed to install driver: {e.with_traceback(None)}")
        logging.debug(f"removing current driver")
        path = os.path.dirname(driverSettings._driverPath)
        path = os.path.abspath(path + "\\..")
        if os.path.exists(path):
            shutil.rmtree(path)

        os.mkdir(path)

        logging.debug("about to install driver again")
        driverSettings._driverPath = driverSettings._driverManager.install()
        logging.debug("driver installed")

#     return path    

def get_firefox_driver(driverSettings:DriverSettings, settings:Settings) -> BaseWebDriver:

    update_driver(driverSettings, settings, True)

    fp = FirefoxProfile(driverSettings.profile_path)
    binary = FirefoxBinary(driverSettings.binary_path) 

    ffService = FirefoxService(driverSettings._driverPath)
    ffService.creation_flags = CREATE_NO_WINDOW
    driver:BaseWebDriver = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp, service=ffService)

    return driver

def get_edge_driver(driverSettings:DriverSettings, settings:Settings) -> BaseWebDriver:

    update_driver(driverSettings, settings, False)

    options = edOptions()
    options.headless = False
    options.add_argument(f'user-data-dir={driverSettings.profile_path}')
    options.binary_location = driverSettings.binary_path

    edService = EdgeService(driverSettings._driverPath)
    edService.creation_flags = CREATE_NO_WINDOW
    
    driver:BaseWebDriver = webdriver.Edge(options=options, service=edService)

    return driver

def wait_and_get_element(driver:BaseWebDriver, by: By, value: str):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
    time.sleep(0.1)
    return driver.find_element(by, value)

def get_element(driver:BaseWebDriver, by:By, value:str):
    
    element = None
    try:
        element = driver.find_element(By.ID, 'serviceErrorMessageBox')
    except Exception as e:
        logging.debug(f"Exception catched when trying to get element: {str(by)}:{str(value)} | {str(e)}")
        element = None

    return element

def click(driver:BaseWebDriver, by: By, value: str, retryTries:int = 20) -> bool:
    
    logging.debug(f"Trying to click {value}")
    clickCount: int = 0
    clicked = False
    while(clickCount < retryTries):

        catched: bool = False
        try:
            element = wait_and_get_element(driver, by, value)
            ActionChains(driver).move_to_element(element).click(element).perform()
        except Exception:
            logging.debug(f"Exception catched while trying to click {value} ({str(clickCount)}/{retryTries})")
            time.sleep(1)
            catched = True

        if catched:
            clickCount = clickCount + 1
        else:
            clickCount = 20
            clicked = True 

    logging.debug(f"Trying to click {value} succueeded: {str(clicked)}")
    return clicked

def select_event_type(driver:BaseWebDriver, eventType:str) -> bool:

    selected = click(driver, By.ID, '__xmlview0--idTimeEventType-arrow')
    events = wait_and_get_element(driver, By.ID, '__xmlview0--idTimeEventType-popup-list-listUl')
    eventId = get_event_id(events, eventType)

    if len(eventId) <= 0:
        return False

    selected = selected and click(driver, By.ID, eventId)

    return selected

def get_logged_events(driver:BaseWebDriver):
    logging.debug("Getting logged events")
    element = wait_and_get_element(driver, By.ID, '__xmlview0--idEventsTable-listUl')

    if not element:
        return []

    time.sleep(2)
    events = wait_and_get_element(driver, By.ID, '__xmlview0--idEventsTable-listUl').text.split('\n')
    i = get_first_event_index(events)

    if i < 0:
        events = wait_and_get_element(driver, By.ID, '__xmlview0--idEventsTable-listUl').text.split('\n')
        i = get_first_event_index(events)

    listOfEvents = []

    if i < 0:
        return listOfEvents

    while i < len(events):
        event = FioriEvent.get_event(events[i])

        if event == FioriEvent.NotDefined or FioriEvent.get_event(events[i+3]) == FioriEvent.Aborted:
            i += 4
            continue
        
        eventTime = dtConvert.to_datetime(f"{events[i+1]} {events[i+2]}", dtConvert.Formats.DMY_H_M_S)
        listOfEvents.append({"event":event,"datetime":eventTime})
        i += 4

    return listOfEvents

def get_first_event_index(events) -> int:
    firstEvent = -1
    i = 0
    while i < len(events) and firstEvent < 0:

        event = FioriEvent.get_event(events[i])
        if event != FioriEvent.NotDefined:
            firstEvent = i

        i += 1

    return firstEvent

def get_has_event_and_time(events, event:FioriEvent):
    logging.debug(f"Getting has event {str(event)}")

    if len(events) <= 0:
        return False, None
    
    eventIndex = -1
    i = 0
    while eventIndex < 0 and i < len(events):
        if events[i]["event"] == event:
            eventIndex = i

        i += 1

    if eventIndex < 0:
        return False, None
    
    return True, events[eventIndex]["datetime"]

def get_pause_state(events):

    if len(events) <= 0:
        return False, 0, None
    
    i = 0
    accumulatedSeconds = 0
    isPaused = False
    pauseStartTime = None
    while i < len(events):

        if events[i]["event"] == FioriEvent.PauseStart:
            isPaused = True
            pauseStartTime = events[i]["datetime"]
            i += 1
            continue

        if events[i]["event"] == FioriEvent.PauseEnd:
            isPaused = False

            if pauseStartTime:
                accumulatedSeconds += (events[i]["datetime"] - pauseStartTime).total_seconds()
                
            pauseStartTime = None
            i += 1
            continue

        i += 1

    return isPaused, accumulatedSeconds, pauseStartTime

def set_date(driver:BaseWebDriver, date: datetime) -> bool:
    dateSet = click(driver, By.ID, '__xmlview0--datePicker-inner')
    dateInput = wait_and_get_element(driver, By.ID, '__xmlview0--datePicker-inner')
    for i in range(10):
        dateInput.send_keys(Keys.BACKSPACE)

    dateInput.send_keys("{:>02}".format(str(date.day)))
    dateInput.send_keys(".")
    dateInput.send_keys("{:>02}".format(str(date.month)))
    dateInput.send_keys(".")
    dateInput.send_keys("{:>02}".format(str(date.year)))

    return dateSet

def set_time(driver:BaseWebDriver, value:datetime) -> bool:

    setTime = dtConvert.to_string(value, dtConvert.Formats.HMS)

    if setTime == None or len(setTime) != 6:
        return False

    timeSet = click(driver, By.ID, '__xmlview0--timePicker-inner')
    timeInput = wait_and_get_element(driver, By.ID, '__xmlview0--timePicker-inner')

    for i in range(10):
        timeInput.send_keys(Keys.BACKSPACE)

    timeInput.send_keys(setTime)
    return timeSet

def get_event_id(events, event: str) -> str:

    eventsSoup = BeautifulSoup(events.get_attribute('innerHTML'), 'lxml')
    content = list(eventsSoup.descendants)

    eventIndex: int = -1
    for i in range(len(content)):
        if content[i] == event:
            eventIndex = i
            break

    eventIndex = eventIndex - 1
    if eventIndex < 0:
        return ''

    try:
        id = str(content[eventIndex]).split('id="')[1].split('">')[0].split('-')[0]
    except:
        return ''

    return id

class QuickFioriTimeEvents:
    def __init__(self,settings:Settings):
        self.ArriveEvent = settings.get(Config.Sections.General, Config.General.ArriveEvent)
        self.LeaveEvent = settings.get(Config.Sections.General, Config.General.LeaveEvent)
        self.PauseStartEvent = settings.get(Config.Sections.General, Config.General.PauseStartEvent)
        self.PauseEndEvent = settings.get(Config.Sections.General, Config.General.PauseEndEvent)
        self.WaitTimeAfterPageLoad = int(settings.get(Config.Sections.General, Config.General.WaitTimeAfterPageLoad))
        self.settings = settings

        driverType = Driver.Firefox
        setDriverType = settings.get(Config.Sections.General, Config.General.Driver)
        if setDriverType == Driver.Firefox.value:
            driverType = Driver.Firefox
        elif setDriverType == Driver.Edge.value:
            driverType = Driver.Edge            

        self.driverSettings:DriverSettings = DriverSettings(
            driverType,
            settings.get(Config.Sections.General, Config.General.ProfilePath),
            settings.get(Config.Sections.General, Config.General.BinaryPath),
            settings.get(Config.Sections.General, Config.General.Url),
            settings.get(Config.Sections.General, Config.General.UrlHome),
            settings.get(Config.Sections.General, Config.General.UrlTime),
            settings.get(Config.Sections.State, Config.State.DriverVersion),
            settings.get(Config.Sections.State, Config.State.DriverPath)
        )

    def set_event(self, type: FioriEvent, setDateTime: datetime, approve: bool, closeInstance:bool):    

        if setDateTime == None:
            return False, "No date provided."    

        driver:BaseWebDriver = None
        done:bool = True
        msg:str = ''      

        try:
            driver = get_driver(self.driverSettings, self.settings, closeInstance)

            if driver == None:
                raise Exception(f"Couldn't go to website: {self.driverSettings.get_url_home()}")
                
            driver.get(self.driverSettings.get_url_time())
            time.sleep(self.WaitTimeAfterPageLoad)

            for i in range(3):
                if not click(driver, By.ID, '__filter0') and i >= 2:
                    raise Exception("Couldn't go to 'Detailed Entry'.")

            time.sleep(1)

            if type == FioriEvent.Arrive and not select_event_type(driver, self.ArriveEvent):
                raise Exception(f"Couldn't select {self.ArriveEvent} event.")
            elif type == FioriEvent.Leave and not select_event_type(driver, self.LeaveEvent):
                raise Exception(f"Couldn't select {self.LeaveEvent} event.")
            elif type == FioriEvent.PauseStart and not select_event_type(driver, self.PauseStartEvent):
                raise Exception(f"Couldn't select {self.PauseStartEven} event.")
            elif type == FioriEvent.PauseEnd and not select_event_type(driver, self.PauseEndEvent):
                raise Exception(f"Couldn't select {self.PauseEndEvent} event.")

            if not set_time(driver, setDateTime):
                raise Exception(f"Couldn't set time to {dtConvert.to_string(setDateTime, dtConvert.Formats.H_M_S)}.")

            if not set_date(driver, setDateTime):
                raise Exception(f"Couldn't set date to {dtConvert.to_string(setDateTime, dtConvert.Formats.d_m_y)}.")

            if not click(driver, By.ID,'__xmlview0--save-BDI-content'):
                raise Exception("Couldn't click 'Save'.")

            if approve:
                if not click(driver, By.ID,'__button2'):
                    raise Exception("Couldn't click 'OK'.")

                time.sleep(1)

                errorMsg = get_element(driver, By.ID, 'serviceErrorMessageBox')
                if (errorMsg != None):
                    raise Exception("Error occured when approving the event.")

            else:
                if not click(driver, By.ID, '__button3'):
                    raise Exception("Couldn't click 'Cancel'.")

            time.sleep(1)

        except Exception as e:
            done = False
            msg = str(e)
        
        if closeInstance and driver != None and done:
            driver.quit()

        return done, msg
    
    def get_state(self,closeInstance:bool):

        done:bool = True
        msg:str = ''
        state:FioriState = None
        driver:BaseWebDriver = None
        try:
            driver = get_driver(self.driverSettings, self.settings, closeInstance)

            if driver == None:
                raise Exception(f"Couldn't go to website: {self.driverSettings.get_url_home()}")
                
            driver.get(self.driverSettings.get_url_time())
            time.sleep(self.WaitTimeAfterPageLoad)

            for i in range(3):
                if not click(driver, By.ID, '__xmlview0--overview') and i >= 2:
                    raise Exception("Couldn't go to 'Time Event List'.")

            time.sleep(2)

            events = get_logged_events(driver)
            isArrived, arriveDateTime = get_has_event_and_time(events, FioriEvent.Arrive)
            isLeft, leaveDateTime = get_has_event_and_time(events, FioriEvent.Leave)
            isPause, accumulatedPauseSeconds, pauseStartTime = get_pause_state(events)

            state = FioriState()
            state.IsArrived = isArrived
            state.ArriveDateTime = arriveDateTime
            state.IsLeft = isLeft
            state.LeaveDateTime = leaveDateTime
            state.IsPaused = isPause
            state.AccumulatedPauseSeconds = accumulatedPauseSeconds
            state.PauseStartTime = pauseStartTime

        except Exception as e:
            done = False
            msg = str(e)

        if closeInstance and driver != None and done:
            driver.quit()

        return done, msg, state