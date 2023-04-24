import datetime
import tkinter
from tkinter import messagebox
from pystray import MenuItem as item
from pystray import Menu
import pystray
from PIL import Image
import Config
import logging
import sys
import DatetimeConverters as dtConvert
from TrayApplication import TrayApplication
from TrayApplicationIcon import Icons, set_icon, notify
import os

#######################################
# Tray methods (for user interaction) #
#######################################
def tray_quit(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    app.ping()
    app.stopLogging()
    app.trayIcon.stop()
    window.destroy()
    exit()

def tray_show_work_time(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    app.ping()

    if app.last_arrive_datetime == None or app.last_arrive_datetime.day != datetime.datetime.now().day:
        messagebox.showinfo('Not arrived', "You haven't logged in with this tool yet.")
        return

    hereTime = datetime.datetime.now() - app.last_arrive_datetime    

    msg:str = f"You are here since: {dtConvert.timedelta_to_string(hereTime)}"

    if app.pause_accumulated_datetime != None and app.pause_accumulated_datetime.total_seconds() > 0:

        now = datetime.datetime.now()
        if (app.is_paused):
            now = app.pause_start_datetime

        workTime = now - app.last_arrive_datetime - app.pause_accumulated_datetime
        msg = f"{msg}\nWorked for: {dtConvert.timedelta_to_string(workTime)}"

    messagebox.showinfo('Working', msg)

def tray_arrive(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    arriveTime:datetime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.ArriveOffset)))
    app.logged_leave_datetime = None

    if app.already_logged_in_today() and not messagebox.askyesno("Arrive again?", "You already ckocked in.\nDo you want to clock in again?"):
        logging.info("Can't arrive, cause already arrived today.")
        return

    app.set_arrive(arriveTime)
    app.ping()

def tray_leave(icon, item):
    logging.debug(sys._getframe().f_code.co_name)

    if not app.already_logged_in_today() and not messagebox.askyesno("Leave again?", "You already clocked out.\nDo you want to clock out again?"):
        logging.info("Can't leave: Not logged in today.")
        return

    leaveTime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.LeaveOffset)))
    app.set_leave(leaveTime)
    app.ping()

def tray_pause_start(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    pauseTime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.StartPauseOffset)))
    app.set_pause(True, pauseTime)
    app.ping()

def tray_pause_start_and_shutdown(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    logging.debug(sys._getframe().f_code.co_name)
    pauseTime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.StartPauseOffset)))
    app.set_pause(True, pauseTime)
    app.ping()
    app.execute_shutdown_command(Config.General.PauseStartCommand)

def tray_pause_end(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    pauseTime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.EndPauseOffset)))
    app.set_pause(False, pauseTime)
    app.ping()

def tray_leave_and_shutdown(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    app.logged_leave_datetime = None

    if not app.already_logged_in_today() and not messagebox.askyesno("Leave again?","You already clocked out.\nDo you want to clock out again?"):
        logging.info("Can't leave: Not logged in today.")
        return

    leaveTime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.LeaveOffset)))
    if not app.set_leave(leaveTime):
        logging.error("Can't leave and therefore won't shutdown.")
        icon.notify("Can't leave and therefore won't shutdown.")
        return

    app.ping()
    app.execute_shutdown_command(Config.General.ShutdownCommand)

def tray_leave_logged_and_arrive(icon, item):
    logging.debug(sys._getframe().f_code.co_name)

    if app.logged_leave_datetime == None or app.logged_leave_datetime == datetime.datetime.min:
        logging.info(f"No leave date logged. {Config.State.LoggedLeaveDateTime.value} isn't set.")
        set_icon(app.trayIcon, Icons.Default)
        notify(app.trayIcon, "No leave date logged.")
        return

    if not app.set_leave(app.logged_leave_datetime):
        msg = f"Couldn't leave at logged time ({dtConvert.to_string(app.logged_leave_datetime)}). And will therefore not arrive."
        logging.error(msg)
        set_icon(app.trayIcon, Icons.Error)
        notify(app.trayIcon, msg)
        return

    arriveTime:datetime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.ArriveOffset)))

    if app.already_logged_in_today() and not messagebox.askyesno("Arrive again?","You already clocked in.\nDo you want to clock in again?"):
        logging.info("Can't arrive, cause already arrived today.")
        return

    if not app.set_arrive(arriveTime):
        msg = f"Couldn't arrive at {dtConvert.to_string(arriveTime)} after setting logged leave time ({dtConvert.to_string(app.logged_leave_datetime)})."
        logging.error(msg)
        set_icon(app.trayIcon, Icons.Error)
        notify(app.trayIcon, msg)

    app.logged_leave_datetime = None
    app.ping()

def tray_log_leave_datetime(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    app.logged_leave_datetime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.LeaveLogOffset)))
    set_icon(app.trayIcon, Icons.LoggedClockOut)
    app.ping()

def tray_log_leave_datatime_and_shutdown(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    app.logged_leave_datetime = datetime.datetime.now() + datetime.timedelta(minutes=int(app.settings.get(Config.Sections.ArriveLeave, Config.ArriveLeave.LeaveLogOffset)))
    set_icon(app.trayIcon, Icons.LoggedClockOut)
    app.ping()
    app.execute_shutdown_command(Config.General.ShutdownCommand)

def tray_get_current_state(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    success, state = app.get_current_state()

    if not success:
        msg = "Couldn't get current state."
        logging.error(msg)
        set_icon(app.trayIcon, Icons.Error)
        notify(app.trayIcon, msg)
        return
    
    if state.IsArrived:
        app.last_arrive_datetime = state.ArriveDateTime

    if state.IsLeft:
        app.last_leave_datetime = state.LeaveDateTime

    app.is_paused = state.IsPaused
    app.pause_accumulated_datetime = datetime.timedelta(0,state.AccumulatedPauseSeconds,0,0,0,0,0)
    app.pause_start_datetime = state.PauseStartTime

    set_icon(app.trayIcon, app.get_icon_image_based_on_state())

def tray_set_default_icon(icon, item):
    logging.debug(sys._getframe().f_code.co_name)
    logging.debug("clearError")
    set_icon(app.trayIcon, Icons.Default)

def tray_open_config(icon, item):
    app.settings.open_file()

def tray_open_readme(icon, item):
    os.startfile("README.pdf")

###################################
# Create menu and run application #
###################################

logFile = 'appLog.log'

# change title bar icon
window = tkinter.Tk()
window.iconbitmap('Icons\default.ico')
window.withdraw()

app = TrayApplication(logFile)
app.ping()

image = Image.open(app.get_icon_image_based_on_state().value)

menuItemsOrder = app._settings.get(Config.Sections.General, Config.General.Order).split(Config.Order.Seperator.value)
menuItems = []

for i in range(len(menuItemsOrder)):

    if menuItemsOrder[i] == Config.Order.Line.value:
        menuItems.append(Menu.SEPARATOR)

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.Quit):
        menuItems.append(item(Config.Order.Quit.value, tray_quit))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.ShowWorkTime):
        menuItems.append( \
            item( \
                Config.Order.ShowWorkTime.value, \
                tray_show_work_time, \
                default = eval(app._settings.get(Config.Sections.General, Config.General.ShowWorkTimeOnLeftClick))))
        
    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.Arrive):
        menuItems.append(item(Config.Order.Arrive.value, tray_arrive))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.Leave):
        menuItems.append(item(Config.Order.Leave.value, tray_leave))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.StartPause):
        menuItems.append(item(Config.Order.StartPause.value, tray_pause_start))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.StartPauseAndShutdown):
        menuItems.append(item(app.append_shutdown_command(Config.Order.StartPauseAndShutdown), tray_pause_start_and_shutdown))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.EndPause):
        menuItems.append(item(Config.Order.EndPause.value, tray_pause_end))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.LeaveAndShutdown):
        menuItems.append(item(app.append_shutdown_command(Config.Order.LeaveAndShutdown), tray_leave_and_shutdown))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.LeaveLoggedAndArrive):
        menuItems.append(item(Config.Order.LeaveLoggedAndArrive.value, tray_leave_logged_and_arrive))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.LogLeave):
        menuItems.append(item(Config.Order.LogLeave.value, tray_log_leave_datetime))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.LogLeaveAndShutdown):
        menuItems.append(item(app.append_shutdown_command(Config.Order.LogLeaveAndShutdown), tray_log_leave_datatime_and_shutdown))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.GetCurrentState):
        menuItems.append(item(Config.Order.GetCurrentState.value, tray_get_current_state))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.SetDefaultIcon):
        menuItems.append(item(Config.Order.SetDefaultIcon.value, tray_set_default_icon))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.OpenConfig):
        menuItems.append(item(Config.Order.OpenConfig.value, tray_open_config))

    elif menuItemsOrder[i] == Config.Order.get_name(Config.Order.OpenReadme):
        menuItems.append(item(Config.Order.OpenReadme.value, tray_open_readme))

menu = tuple(menuItems)
app.trayIcon = pystray.Icon("name", image, "QuickFioriTimeEvents", menu)
app.trayIcon.run_detached()
window.mainloop()
os._exit(0)