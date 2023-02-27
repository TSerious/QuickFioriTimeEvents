import logging
import Config
import os
from Fiori import QuickFioriTimeEvents, FioriEvent, Driver
import DatetimeConverters as dtConvert
import datetime
from varname import nameof
import sys
from tkinter import messagebox, filedialog, simpledialog
import validators
from TrayApplicationIcon import Icons, set_icon, notify
import pystray

class TrayApplication:
    def __init__(self, logFile:str):
        self.startLogging(logFile)

        self._trayIcon:pystray = None
        self._settings:Config.Settings = Config.Settings()
        self.check_settings()

        self._automatFiori:QuickFioriTimeEvents = QuickFioriTimeEvents(self._settings)

        self._lastArriveDateTime:datetime.datetime = dtConvert.to_datetime(self._settings.get(Config.Sections.State, Config.State.LastArriveDateTime))
        self._lastLeaveDateTime:datetime.datetime = dtConvert.to_datetime(self._settings.get(Config.Sections.State, Config.State.LastLeaveDateTime))
        self._lastPingDateTime:datetime.datetime = dtConvert.to_datetime(self._settings.get(Config.Sections.State, Config.State.LastPing))

        lastPauseTime:datetime.datetime = dtConvert.to_datetime(self._settings.get(Config.Sections.State, Config.State.LastPauseDateTime))

        if lastPauseTime == None or lastPauseTime.day != datetime.datetime.now().day:
            self._isPaused:bool = False
            self._pauseStartTime:datetime.datetime = None
        else:
            self._isPaused:bool = eval(self._settings.get(Config.Sections.State, Config.State.IsPause))
            self._pauseStartTime:datetime.datetime = lastPauseTime

        accumulatedPauseTime:float = float(self._settings.get(Config.Sections.State, Config.State.AccumulatedPauseTime))
        self._pauseAccumulatedTime:datetime.timedelta = datetime.timedelta(0,accumulatedPauseTime,0,0,0,0,0)

        self._loggedLeaveDatetime:datetime.datetime = dtConvert.to_datetime(self._settings.get(Config.Sections.State, Config.State.LoggedLeaveDateTime))

        if eval(self._settings.get(Config.Sections.General, Config.General.ClearLog)) and os.path.isfile(logFile):
            self.stopLogging()
            
            try:
                os.remove(logFile)
            except:
                messagebox.showwarning(
                    "Already started",
                    "Another instance of this application might already be running.\r\nPlease close this one or close all other instances.")
            
            self.startLogging(logFile)

        #logging.basicConfig(level=int(self._settings.get(Config.Sections.General, Config.General.MinLogLevel)), force=True)
        logging.debug('TrayApplication initialized')

    @property
    def settings(self) -> Config.Settings:
        return self._settings

    @property
    def automatefiori(self) -> QuickFioriTimeEvents:
        return self._automatFiori

    @property
    def trayIcon(self) -> pystray.Icon:
        return self._trayIcon
    
    @trayIcon.setter
    def trayIcon(self, value: pystray.Icon):
        self._trayIcon = value

    @property
    def last_arrive_datetime(self) -> datetime.datetime:
        return self._lastArriveDateTime

    @last_arrive_datetime.setter
    def last_arrive_datetime(self, value:datetime.datetime):
        self._lastArriveDateTime = value
        v = dtConvert.to_string(self._lastArriveDateTime)
        logging.debug(f'Setting {nameof(self._lastArriveDateTime)} to: {v}')
        self._settings.set(Config.Sections.State, Config.State.LastArriveDateTime, v)

    @property
    def last_leave_datetime(self) -> datetime.datetime:
        return self._lastLeaveDateTime

    @last_leave_datetime.setter
    def last_leave_datetime(self, value:datetime.datetime):
        self._lastLeaveDateTime = value
        v = dtConvert.to_string(self._lastLeaveDateTime)
        logging.debug(f'Setting {nameof(self._lastLeaveDateTime)} to: {v}')
        self._settings.set(Config.Sections.State, Config.State.LastLeaveDateTime, v)

    @property
    def ping_datetime(self) -> datetime.datetime:
        return self.pingDateTime

    @property
    def is_paused(self) -> bool:
        return self._isPaused

    @is_paused.setter
    def is_paused(self, value:bool):
        self._isPaused = value
        v = str(value)
        logging.debug(f'Setting {nameof(self._isPaused)} to: {v}')
        self._settings.set(Config.Sections.State, Config.State.IsPause, v)

    @property
    def pause_start_datetime(self) -> datetime.datetime:
        return self._pauseStartTime

    @pause_start_datetime.setter
    def pause_start_datetime(self, value:datetime.datetime):
        self._pauseStartTime = value
        pauseStartTime = dtConvert.to_string(self._pauseStartTime)
        logging.debug(f'Setting {nameof(self._pauseStartTime)} to: {pauseStartTime}')
        self._settings.set(Config.Sections.State, Config.State.LastPauseDateTime, pauseStartTime)

    @property
    def pause_accumulated_datetime(self) -> datetime.timedelta:
        return self._pauseAccumulatedTime

    @pause_accumulated_datetime.setter
    def pause_accumulated_datetime(self, value:datetime.timedelta):
        self._pauseAccumulatedTime = value
        v = str(value.total_seconds())
        logging.debug(f'Setting {nameof(self._pauseAccumulatedTime)} to: {v}')
        self._settings.set(Config.Sections.State, Config.State.AccumulatedPauseTime, v)

    @property
    def logged_leave_datetime(self) -> datetime.datetime:
        return self._loggedLeaveDatetime

    @logged_leave_datetime.setter
    def logged_leave_datetime(self, value:datetime.datetime):
        self._loggedLeaveDatetime = value
        v = dtConvert.to_string(self._loggedLeaveDatetime)
        logging.debug(f'Setting {nameof(self._loggedLeaveDatetime)} to: {v}')
        self._settings.set(Config.Sections.State, Config.State.LoggedLeaveDateTime, v)

    def ping(self):
        logging.info('ping')
        self.pingDateTime = datetime.datetime.now()
        self._settings.set(Config.Sections.State, Config.State.LastPing, dtConvert.to_string(self.pingDateTime))

    def append_shutdown_command(self, value:Config.Order) -> str:

        command:Config.Order = Config.General.ShutdownCommand
        if (value == Config.Order.StartPauseAndShutdown):
            command = Config.General.PauseStartCommand

        if self._settings.get(Config.Sections.General, command).endswith("h"):
            return f"{value.value}hybernate"

        return f"{value.value}shutdown"

    def check_settings(self):
        logging.debug(sys._getframe().f_code.co_name)

        browser = self.settings.get(Config.Sections.General, Config.General.Driver)

        if browser != Driver.Edge.value and browser != Driver.Firefox.value:
            self.settings.set(Config.Sections.General, Config.General.BinaryPath, '')
            self.settings.set(Config.Sections.General, Config.General.ProfilePath, '')
            self.settings.set(Config.Sections.State, Config.State.DriverVersion, '')
            self.settings.set(Config.Sections.State, Config.State.DriverPath, '')

            driver = self.define_driver()

            if driver == Driver.NotDefined:
                messagebox.showinfo("Browser (driver) not defined","You must define a browser for this application.", icon='error')
                logging.error('No driver defined')
                quit()

            self.settings.set(Config.Sections.General, Config.General.Driver, driver.value)

        if not self.check_binary_path():
            messagebox.showinfo(f"{browser} missing", f"Couldn't find web browser: {browser}", icon='error')
            logging.error(f'{Config.General.BinaryPath.value} is not defined.')
            quit()

        if not self.check_profile_path():
            logging.warn(f'{Config.General.ProfilePath.value} is not defined.')

            if eval(self._settings.get(Config.Sections.General, Config.General.CheckProfilePath)):
                showAgainAnswer = messagebox.askquestion(\
                    f"{browser} profile not defined",\
                    f"No {browser} profile is defined but you might be able to use this application without defining one.\nDo you want to see this warning again?",\
                    icon='warning')

                showAgain = True
                if showAgainAnswer == messagebox.NO:
                    showAgain = False

                self._settings.set(Config.Sections.General, Config.General.CheckProfilePath, str(showAgain))

        if not self.check_fiori_url():
            messagebox.showinfo("Fiori url not defined", "The url for fiori isn't configured.",icon='error')
            logging.error(f'{Config.General.Url.value} is not defined.')
            quit()

    def define_driver(self) -> Driver:
        messagebox.showinfo("Select browser", f"You will now be asked which browser (driver) to use.\nYou must choose either {Driver.Edge.value} or {Driver.Firefox.value}.")

        answer = messagebox.askyesno("Select browser", f"Do you want to use {Driver.Edge.value}?")
        if answer:
            return Driver.Edge
        
        answer = messagebox.askyesno("Select browser", f"Do you want to use {Driver.Firefox.value}?")
        if answer:
            return Driver.Firefox
        
        return Driver.NotDefined

    def check_fiori_url(self) -> bool:
        logging.debug(sys._getframe().f_code.co_name)
        fioriUrl = self.settings.get(Config.Sections.General, Config.General.Url)

        if len(fioriUrl) > 0 and validators.url(fioriUrl):
            return True

        fioriUrl = simpledialog.askstring( \
            "Define Fiori url",\
            "You need to define the url (address) of Fiori.\nPlease open a browser, go to your Fiori website and copy the url to here:")

        if fioriUrl == None:
            return False

        if len(fioriUrl) > 0 and validators.url(fioriUrl):
            fioriUrl = fioriUrl.split('#')[0]
            self.settings.set(Config.Sections.General, Config.General.Url, fioriUrl)
            return True

        return False

    def check_profile_path(self) -> bool:
        logging.debug(sys._getframe().f_code.co_name)
        profilePath = self.settings.get(Config.Sections.General, Config.General.ProfilePath)

        if len(profilePath) > 0 and os.path.exists(profilePath):
            return True

        driverType = self.settings.get(Config.Sections.General, Config.General.Driver)
        if driverType == Driver.Firefox.value:
            profilePath = self.search_for_firefox_profile()
        elif driverType == Driver.Edge.value:
            profilePath = self.search_for_edge_profile()

        if len(profilePath) <= 0 or not os.path.exists(profilePath):
            return False

        self.settings.set(Config.Sections.General, Config.General.ProfilePath, profilePath)
        return True

    def check_binary_path(self) -> bool:
        logging.debug(sys._getframe().f_code.co_name)
        binaryPath = self.settings.get(Config.Sections.General, Config.General.BinaryPath)

        if len(binaryPath) > 0 and os.path.exists(binaryPath):
            return True

        driverType = self.settings.get(Config.Sections.General, Config.General.Driver)
        if driverType == Driver.Firefox.value:
            binaryPath = self.search_for_firefox()
        elif driverType == Driver.Edge.value:
            binaryPath = self.search_for_edge()

        if len(binaryPath) <= 0 or not os.path.exists(binaryPath):
            return False

        self.settings.set(Config.Sections.General, Config.General.BinaryPath, binaryPath)
        return True

    def search_for_firefox(self) -> str:
        if os.path.exists(Config.defaultFirefoxBinaryPath):
            return Config.defaultFirefoxBinaryPath

        messagebox.showinfo('Firefox binary not found', "Couldn't find firefox.exe.\nPlease make sure that Firefox is installed.")

        firefoxPath = filedialog.askopenfilename(defaultextension='.exe',filetypes=[("Firefox", "firefox.exe")],initialdir='C:\\Program Files',title='Select firefox.exe')

        return firefoxPath
    
    def search_for_edge(self) -> str:
        if os.path.exists(Config.defaultEdgeBinaryPath):
            return Config.defaultEdgeBinaryPath

        messagebox.showinfo('Edge binary not found', "Couldn't find msedge.exe.\nPlease make sure that Edge is installed.")

        edgePath = filedialog.askopenfilename(defaultextension='.exe',filetypes=[("Edge", "msedge.exe")],initialdir='C:\\Program Files',title='Select msedge.exe')

        return edgePath

    def search_for_firefox_profile(self) -> str:

        defaultProfilesPath = "C:\\Users\\" + os.getlogin() + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"

        profilePath = ''
        if os.path.exists(defaultProfilesPath):
            availableProfiles = os.scandir(defaultProfilesPath)
            profileMaxTime = 0
            for profile in availableProfiles:
                if profile.is_dir():
                    lastEditTime = os.path.getmtime(profile.path)
                    if lastEditTime > profileMaxTime:
                        profilePath = profile.path
                        profileMaxTime = lastEditTime

        if (len(profilePath) <= 0 or not os.path.exists(profilePath)) and eval(self.settings.get(Config.Sections.General, Config.General.CheckProfilePath)):
            searchForProfileQuestion = messagebox.askquestion('Firefox profile not found', "Couldn't find any firefox profile.\nDo you want to select the profile path now?.")

            if searchForProfileQuestion == messagebox.YES:
                messagebox.showinfo(\
                    'Firefox profile',\
                    "You need to select the path of the current Firefox profile.\n" + \
                    "If you want to know where profiles are stored, open Firefox and enter 'about:profiles' in the address bar.\n" + \
                    "You need to select the ROOT path of the standard profile. This is usually located in the \\Roaming directory.")

                if not os.path.exists(defaultProfilesPath):
                    defaultProfilesPath = "C:\\Users\\" + os.getlogin() + "\\AppData\\Roaming"

                profilePath = filedialog.askdirectory(initialdir=defaultProfilesPath, title="Select Firefox profile path")

        return profilePath
    
    def search_for_edge_profile(self) -> str:

        defaultProfilesPath = "C:\\Users\\" + os.getlogin() + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default"

        if not os.path.exists(defaultProfilesPath):
            return ''

        return defaultProfilesPath
    
    def stop_pause(self):
        logging.debug(sys._getframe().f_code.co_name)

        if not self.is_paused:
            self.pause_start_datetime = None
            return

        self.is_paused = False

        if self.pause_start_datetime == None:
            return

        self.pause_accumulated_datetime = datetime.datetime.now() - self.pause_start_datetime
        self.pause_start_datetime = None

    def start_pause(self, startTime:datetime.datetime):
        logging.debug(sys._getframe().f_code.co_name)
        self.pause_start_datetime = startTime
        self.is_paused = True

    def clear_pause(self):
        logging.debug(sys._getframe().f_code.co_name)
        self.is_paused = False
        self.pause_start_datetime = None
        self.pause_accumulated_datetime = datetime.timedelta(0,0,0,0,0,0,0)

    def already_logged_in_today(self) -> bool:

        b = self.last_arrive_datetime != None and \
            self.last_arrive_datetime.day == datetime.datetime.now().day and \
            self.last_arrive_datetime.month == datetime.datetime.now().month

        logging.debug(f'{sys._getframe().f_code.co_name} = {str(b)}')

        return b
    
    def set(self, event:FioriEvent, eventTime:datetime.datetime, approve: bool|None = None, closeInstance:bool|None = None):

        if (approve == None):
            approve = eval(self.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.Approve))

        if closeInstance == None:
            closeInstance = eval(self.settings.get(Config.Sections.General, Config.General.CloseInstance))

        logging.debug(f"Set: {str(event)} at {dtConvert.to_string(eventTime)} | approve = {str(approve)} | closeInstance = {str(closeInstance)}")

        done:bool = self.automatefiori.set_event(
            event,
            eventTime,
            approve,
            closeInstance)

        logging.debug(f"Set succeeded = {str(done)}")

        return done

    def set_leave(self, leaveDateTime: datetime.datetime, approve:bool|None = None, closeInstance:bool|None = None) -> bool:
        logging.debug(sys._getframe().f_code.co_name)

        done, msg = self.set(FioriEvent.Leave, leaveDateTime, approve, closeInstance)

        if not done:
            logging.error(f"Couldn't set leave at {dtConvert.to_string(leaveDateTime)} | approve = {str(approve)} | {msg}")
            set_icon(self._trayIcon, Icons.Error)
            notify(self._trayIcon, f"Couldn't set leave.\n{msg}")
        else:
            logging.info(f"Set leave at {dtConvert.to_string(leaveDateTime)} | approve = {str(approve)}")
            set_icon(self._trayIcon, Icons.ClockedOut)

        self.clear_pause()
        self.last_leave_datetime = leaveDateTime

        return done

    def set_arrive(self, arriveDateTime: datetime.datetime, approve: bool|None = None, closeInstance:bool|None = None) -> bool:
        logging.debug(sys._getframe().f_code.co_name)

        done, msg = self.set(FioriEvent.Arrive, arriveDateTime, approve, closeInstance)

        if not done:
            logging.error(f"Couldn't set arrive at {dtConvert.to_string(arriveDateTime)} | approve = {str(approve)} | {msg}")
            set_icon(self._trayIcon, Icons.Error)
            notify(self._trayIcon, f"Couldn't set arrive now.\n{msg}")
        else:
            logging.info(f"Set arrive at {dtConvert.to_string(arriveDateTime)} | approve = {str(approve)}")
            set_icon(self._trayIcon, Icons.ClockedIn)

        self.clear_pause()
        self.last_arrive_datetime = arriveDateTime

        return done

    def set_pause(self, start:bool, pauseTime:datetime, approve: bool|None = None, closeInstance:bool|None = None):
        logging.debug(sys._getframe().f_code.co_name)

        event = FioriEvent.PauseEnd
        if start:
            event = FioriEvent.PauseStart

        if start and self.is_paused:
            if not messagebox.askyesno("Start pause?", "You already started the pause.\nDo you want to start it again?"):
                return

            logging.info("Starting pause but pause is already started")        
        elif not start and not self.is_paused:
            if not messagebox.askyesno("End pause?", "You already ended the pause.\nDo you want to end it again?"):
                return

            logging.info("Ending pause but has already ended")

        done, msg = self.set(event, pauseTime, approve, closeInstance)

        if not done:
            logging.error(f"Couldn't setPause: start = {str(start)} | approve ={str(approve)} | {msg}")
            set_icon(self.trayIcon, Icons.Error)

            if start:
                notify(self.trayIcon, f"Couldn't start pause.\n{msg}")
            else:
                notify(self.trayIcon, f"Couldn't stop pause.\n{msg}")
        else:
            logging.info(f"Set pause at {dtConvert.to_string(pauseTime)} | start = {str(start)} | approve = {str(approve)}")
            if start:
                set_icon(self.trayIcon, Icons.Paused)
            else:
                set_icon(self.trayIcon, Icons.ClockedIn)

        if start:
            self.start_pause(pauseTime)
        else:
            self.stop_pause()

    def execute_shutdown_command(self, command:Config.General):
        logging.debug(sys._getframe().f_code.co_name)

        commandString = self.settings.get(Config.Sections.General, command)

        if len(commandString) <= 0:
            logging.error("Invalid shutdown command")
            set_icon(self.trayIcon, Icons.Error)
            notify(self.trayIcon, "Shutdown command is invalid.")
            return

        logging.info(f"Shutting down system now with: {commandString}")
        os.system(commandString)

    def get_current_state(self, closeInstance:bool|None = None):
        logging.debug(sys._getframe().f_code.co_name)

        if closeInstance == None:
            closeInstance = eval(self.settings.get(Config.Sections.General, Config.General.CloseInstance))

        done, msg, state = self.automatefiori.get_state(closeInstance)
        
        if len(msg) > 0:
            logging.error(f"Couldn't get current state: {msg}")

        return done, state
    
    def get_icon_image_based_on_state(self) -> Icons:
        if self.is_paused:
            image = Icons.Paused

        elif self.last_arrive_datetime != None and self.last_arrive_datetime.day == datetime.datetime.now().day:
            image = Icons.ClockedIn

        elif self.logged_leave_datetime != None:
            image = Icons.LoggedClockOut

        elif self.last_leave_datetime != None:
            image = Icons.ClockedOut

        else:
            image = Icons.Default

        return image

    def startLogging(self, logFile:str):
            logging.basicConfig(\
            filename=logFile, \
            encoding='utf-8', \
            level=logging.INFO  , \
            format='%(asctime)s -  %(levelname)s - %(message)s')

    def stopLogging(self):
        logging.shutdown()