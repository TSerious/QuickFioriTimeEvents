import logging
from enum import Enum
import pystray
from PIL import Image
import sys

class Icons(Enum):
    Default = "Icons\default.ico"
    Error = "Icons\error.ico"
    Paused = "Icons\paused.ico"
    ClockedIn = "Icons\clockedIn.ico"
    ClockedOut = "Icons\clockedOut.ico"
    LoggedClockOut = "Icons\clockOutLogged.ico"

def set_icon(trayIcon:pystray.Icon, i:Icons):
    logging.debug(sys._getframe().f_code.co_name)

    if (trayIcon == None):
        logging.error("Instance of trayIcon is None!")
        return

    image = Image.open(i.value)
    trayIcon.icon = image
    logging.debug("Icon set to " + str(i.value))

def notify(trayIcon:pystray.Icon, msg:str):
    logging.debug(sys._getframe().f_code.co_name)

    if (trayIcon == None):
        logging.error("Instance of trayIcon is None!")
        return

    trayIcon.notify(msg)