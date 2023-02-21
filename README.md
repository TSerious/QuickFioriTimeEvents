# QuickFioriTimeEvents
Windows-Taskbar tool to quickly add time events in SAP Fiori.

My employer uses a SAP Fiori tool to track our time events (working hours). That means that we have to open the appropiate website and clock in and out. Cause I found this relatively annoying I created this small tool for taskbar with which you can quickly clock in and out.

The tool is shown as a small icon <img src="/Icons/default.ico" alt="taskbar icon" width="20" height="20"/> in the taskbar. A right click opens a menu that let you perform some actions quickly.

## Features
- Arrive (clock in)
- Leave (clock out)
- Leave and shutdown the PC (sleep and hybernate are also possible)
- Start a pause
- Start a pause and shutdown the PC (sleep and hybernate are also possible)
- End a pause
- Show the time you are clocked in and the work time (clock in time minus pause time)
- Log a leave event: The clock out time is only logged and not submitted to SAP Fiori. This is useful, as an offset time can be added to the leave event and events in the future might be blocked.
- Log a leave event and shutdown (sleep and hybernate are also possible)
- Submit logged leave event and arrive afterwards
- Get the current work time from SAP Fiori

## Disclaimer
So far this is a Windows only tool. It uses [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) and requires [Firefox](https://www.mozilla.org/de/firefox/new/) to interact with the Fiori website.

## Installation
To use the tool [Firefox](https://www.mozilla.org/de/firefox/new/) needs to be installed. The tool does not need to be installed just run it.
When run for the first time, you need to define the url for *Fiori*.
![taskbar icon](/Icons/default.ico "taskbar icon")

When run for the first time, the tool searches for the Firefox. B

### Autostart
In order to start the tool with Windows, it needs to be put into the *Startup* directory. To open the *Startup* directory, hit the keys Win+R, type <code>shell:startup</code> into the opened form (window) and click ok. Afterwards create a shortcut of the *QuickFioriTimeEvents.exe* (right click on the exe and select *Create shortcut*) and copy the just created shortcut to the *Startup* directory. From now on the tool will be started when Windows is started.

## 
