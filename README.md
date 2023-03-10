# QuickFioriTimeEvents
Windows-Taskbar tool to quickly add time events in SAP Fiori.

My employer uses a SAP Fiori tool to track our time events (working hours). That means that we have to open the appropiate website and clock in and out. Cause I found this relatively annoying I created this small tool for the (Windows) taskbar with which you can quickly clock in and out.

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

## Installation
The tool does not need to be installed just run it.
When run for the first time, you will be asked weather to use Edge or Firefox.
On the first start, you also need to define the url for *Fiori*. Open a browser navigate to your Fiori website and copy the address into the shown window.<br/>
<img src="/Readme_Images/FioriUrl.PNG" alt="taskbar icon"/>

### Autostart
In order to start the tool with Windows, it needs to be put into the *Startup* directory. To open the *Startup* directory, hit the keys Win+R, type <code>shell:startup</code> into the opened form (window) and click ok. Afterwards create a shortcut of the *QuickFioriTimeEvents.exe* (right click on the exe and select *Create shortcut*) and copy the just created shortcut to the *Startup* directory. From now on the tool will be started when Windows is started.

## Using the application
You mainly interact with the tool trough the taskbar icon <img src="/Icons/default.ico" alt="taskbar icon" width="20" height="20"/>. Right click on it and perform one of the actions.

### Commands
#### Quit
Closes the application.

#### Arrive
Adds an arrive or clock in event to your time events in Fiori. The time in *[ArriveLeave]ArriveOffset* will be added to the current time.

#### Leave
Adds a leave or clock out event to your time events in Fiori. The time in *[ArriveLeave]LeaveOffset* will be added to the current time.

#### Leave and hybernate
Does the same as [Leave](#leave) and executes the *[General]ShutdownCommand* afterwards.

#### Start Pause
Adds a pause start event to your time events in Fiori. The time in *[ArriveLeave]StartPauseOffset* will be added to the current time.

#### Start Pause and hybernate
Does the same as [Start Pause](#start-pause) and executes the *[General]PauseStartCommand* afterwards.

#### End Pause
Adds a pause end event to your time events in Fiori. The time in *[ArriveLeave]EndPauseOffset* will be added to the current time.

#### Arriv (submit Leave)
Before doing the same as [Arrive](#arrive), the currently logged leave (or clock out) time is added to time events in Fiori. The added leave time is the logged leave time plus *[ArriveLeave]LeaveLogOffset*.

#### Log Leave
Log the current time as the leave (clock out) time but do not submit this to Fiori.

#### Log Leave and hybernate
Does the same as [Log Leave](#log-leave) and executes the *[General]ShutdownCommand* afterwards.

#### Update state
Gets the current state (if you are logged in and the pause time) from Fiori.

#### Reset icon
Resets the icon to the default one.

#### Open config file
Open the *config.ini* file.

#### Open documentation
Opens the pdf version of this documentation. (You are probably reading it)

#### Show work time
Shows the time (hours:minutes:seconds) since you clocked in. It also shows the *time since clock in* minus the *pause time*. This is the time you have worked.
By default this can be executed with a left click on the icon, if *[General]ShowWorkTimeOnLeftClick* is "True".

### Icon state
The current state is indicated by the taskbar icon. It can be in the following states:
<ul>
    <li>
        <img src="/Icons/default.ico" alt="taskbar icon" width="20" height="20"/> Default icon.
    </li>
    <li>
        <img src="/Icons/clockedIn.ico" alt="taskbar icon" width="20" height="20"/> You are clocked in and working.
    </li>
    <li>
        <img src="/Icons/clockedOut.ico" alt="taskbar icon" width="20" height="20"/> You are clocked out.
    </li>
    <li>
        <img src="/Icons/clockOutLogged.ico" alt="taskbar icon" width="20" height="20"/> A leave or clock out event has ben logged (but not submitted).
    </li>
    <li>
        <img src="/Icons/paused.ico" alt="taskbar icon" width="20" height="20"/> You are clocked in but currently in a pause (and not working).
    </li>
    <li>
        <img src="/Icons/error.ico" alt="taskbar icon" width="20" height="20"/> An error has occured.
    </li>
</ul>

## Configuring the application
You can customize what is shown in the right click menu ([see here](#menu-elements)) and other stuff.

Right now the application can only be configured via the config.ini file. The file is seperated into different sections. In order to change the settings of the application you have to edit the config.ini file. The settings of each section are described in the tables below.

### ArriveLeave
<table>
    <tbody>
        <tr>
            <th>Setting</th>
            <th>Default value</th>
            <th>Desciption</th>
        </tr>
        <tr>
            <td>[ArriveLeave]Approve</td>
            <td>True</td>
            <td>A value indicating whether the event shall be approved. Only approved events are stored in fiori. Set to False to approve manually.</td>
        </tr>
        <tr>
            <td>[ArriveLeave]ArriveOffset</td>
            <td>-5</td>
            <td>Minutes that will be added to the arrive time. Negative values are possible.</td>
        </tr>
        <tr>
            <td>[ArriveLeave]LeaveOffset</td>
            <td>0</td>
            <td>Minutes that will be added to the leave time. Negative values are possible.</td>
        </tr>
        <tr>
            <td>[ArriveLeave]LeaveLogOffset</td>
            <td>5</td>
            <td>Minutes that will be added to the leave time. Negative values are possible.</td>
        </tr>
        <tr>
            <td>[ArriveLeave]StartPauseOffset</td>
            <td>0</td>
            <td>Minutes that will be added to the pause start time. Negative values are possible.</td>
        </tr>
        <tr>
            <td>[ArriveLeave]EndPauseOffset</td>
            <td>0</td>
            <td>Minutes that will be added to the pause end time. Negative values are possible.</td>
        </tr>
    </tbody>
</table>

### General
<table>
    <tbody>
        <tr>
            <th>Setting</th>
            <th>Default value</th>
            <th>Desciption</th>
        </tr>
        <tr>
            <td>[General]MinLogLevel</td>
            <td></td>
            <td>The minimum level of log entries.<br/>CRITICAL = 50, ERROR = 40, WARNING = 30,<br/>INFO = 20, DEBUG = 10, NOTSET = 0</td>
        </tr>
        <tr>
            <td>[General]ClearLog</td>
            <td>True</td>
            <td>A value indicating whether the log shall be deleted,<br/>each time the software starts.</td>
        </tr>
        <tr>
            <td>[General]WaitTimeAfterPageLoad</td>
            <td>10</td>
            <td>The time in seconds to wait after the initial page<br/>is loaded in the browser instance.</td>
        </tr>
        <tr>
            <td>[General]Url</td>
            <td></td>
            <td>The (base) url of Fiori.</td>
        </tr>
        <tr>
            <td>[General]UrlHome</td>
            <td>#Shell-home</td>
            <td>The path to the 'Home' page.</td>
        </tr>
        <tr>
            <td>[General]UrlTime</td>
            <td>?appState=lean#TimeEntry-change</td>
            <td>The path to the 'Time' page.</td>
        </tr>
        <tr>
            <td>[General]Driver</td>
            <td></td>
            <td>The browser (or driver) that is used to interact with SAP Fiori.<br/>Currently <code>Edge</code> or <code>Firefox</code> are supported.</td>
        </tr>
        <tr>
            <td>[General]ProfilePath</td>
            <td></td>
            <td>The path where the profile of the used browser (driver) is stored.</td>
        </tr>
        <tr>
            <td>[General]BinaryPath</td>
            <td></td>
            <td>The path where the executable of the used browser (driver) us located.</td>
        </tr>
        <tr>
            <td>[General]CheckProfilePath</td>
            <td>True</td>
            <td>A value whether to check if [General]ProfilePath is set.</td>
        </tr>
        <tr>
            <td>[General]ArriveEvent</td>
            <td>P10</td>
            <td>The arrive event indentifier.</td>
        </tr>
        <tr>
            <td>[General]LeaveEvent</td>
            <td>P20</td>
            <td>The leave event indentifier.</td>
        </tr>
        <tr>
            <td>[General]PauseStartEvent</td>
            <td>P15</td>
            <td>The pause start event indentifier.</td>
        </tr>
        <tr>
            <td>[General]PauseEndEvent</td>
            <td>P25</td>
            <td>The pause end event indentifier.</td>
        </tr>
        <tr>
            <td>[General]PauseStartCommand</td>
            <td>shutdown.exe /h</td>
            <td>The shutdown command. '/h' means hybernate<br/>instead of normal shutdown.</td>
        </tr>
        <tr>
            <td>[General]ShutdownCommand</td>
            <td>shutdown.exe /h</td>
            <td>The shutdown command. '/h' means hybernate<br/>instead of normal shutdown.</td>
        </tr>
        <tr>
            <td>[General]CloseInstance</td>
            <td>True</td>
            <td>A value indicating whether the browser instance should be quit<br/>after the event has been created.</td>
        </tr>
        <tr>
            <td>[General]ShowWorkTimeOnLeftClick</td>
            <td>True</td>
            <td>A value indicating whether a left click on the icon<br/>shows the current work time.</td>
        </tr>
        <tr>
            <td>[General]Order</td>
            <td>
                <p style="word-wrap:break-word;width:500px">
                Quit|---|Arrive|Leave|LeaveAndShutdown|---|StartPause|StartPauseAndShutdown|EndPause|---|LeaveLoggedAndArrive|LogLeave|LogLeaveAndShutdown|---|GetCurrentState|SetDefaultIcon|OpenConfig|OpenReadme|---|ShowWorkTime
                </p>
            </td>
            <td>
                <p>
                The order of the elemnts in the right click menu of the icon.</br>
                Each element is seperated with '|'.<br/>
                Possible elements are listed in <a href="##menu-elements">Menu Elements</a>.
                </p>
            </td>
        </tr>
    </tbody>
</table>
</div>

#### Menu Elements
The following elements can be added to *[General]Order* to customize the right click menu.
<ul>
<li><code>---</code> A seperator line</li>
<li><code>Quit</code> <a href="#squit">Quit</a></li>
<li><code>Arrive</code> <a href="#arrive">Arrive</a></li>
<li><code>Leave</code> <a href="#leave">Leave</a></li>
<li><code>StartPause</code> <a href="#start-pause">StartPause</a></li>
<li><code>StartPauseAndShutdown</code> <a href="#start-pause-and-hybernate">StartPauseAndShutdown</a></li>
<li><code>EndPause</code> <a href="#end-pause">EndPause</a></li>
<li><code>ShowWorkTime</code> <a href="#show-work-time">ShowWorkTime</a></li>
<li><code>LeaveLoggedAndArrive</code> <a href="#arriv-submit-leave">LeaveLoggedAndArrive</a></li>
<li><code>LeaveAndShutdown</code> <a href="#leave-and-hybernate">LeaveAndShutdown</a></li>
<li><code>LogLeave</code> <a href="#log-leave">Log Leave</a></li>
<li><code>LogLeaveAndShutdown</code> <a href="#log-leave-and-hybernate">LogLeaveAndShutdown</a></li>
<li><code>GetCurrentState</code> <a href="#state">GetCurrentState</a></li>
<li><code>SetDefaultIcon</code> <a href="#reset-icon">SetDefaultIcon</a></li>
<li><code>OpenConfig</code> <a href="#open-config-file">OpenConfig</a></li>
<li><code>OpenReadme</code> <a href="#open-documentation">OpenReadme</a></li>
</ul>

### State
These settings doesn't need to be edited as they are only used to save the state of the application. So they will change on each run.
<table>
    <tbody>
        <tr>
            <th>Setting</th>
            <th>Default value</th>
            <th>Desciption</th>
        </tr>
        <tr>
            <td>[State]LastArriveDateTime</td>
            <td></td>
            <td>The date and time the arrive event was set the last time</td>
        </tr>
        <tr>
            <td>[State]LastPing</td>
            <td></td>
            <td>The date and time of the last interaction with the software.</td>
        </tr>
        <tr>
            <td>[State]IsPause</td>
            <td>False</td>
            <td>A value indicating whether you are currently in a pause.</td>
        </tr>
        <tr>
            <td>[State]LastPauseDateTime</td>
            <td></td>
            <td>The date and time of the last pause start event.</td>
        </tr>
        <tr>
            <td>[State]AccumulatedPauseTime</td>
            <td>0</td>
            <td>The time in seconds the user has been in a pause.</td>
        </tr>
        <tr>
            <td>[State]LoggedLeaveDateTime</td>
            <td></td>
            <td>The date and time of the leave event that will be created when using LeaveAndArrive.</td>
        </tr>
    </tbody>
</table>

