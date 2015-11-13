Working procedure
=========================================

Startup process of the graphical interface.

| | +---------------------------+
| | |    Opens client_amp.py    |
| | +-------------+-------------+
| |               I
| |               I
| | +-------------V-------------+ -- help argument  +-----------------+
| | |      Checks arguments     | ----------------> | Launch man page |
| | +-------------+-------------+                   +-----------------+
| |               I 
| |               I
| |               I - No arguments
| |               I
| |               I
| | +-------------V-------------+
| | |    Redirects sys.stdout   |
| | +-------------+-------------+
| |               I
| |               I
| | +-------------V-------------+
| | |  Launchs the application  |
| | +---------------------------+
| |               I
| |               I
| | +-------------V-------------+
| | | Creates the main window   |
| | +-------------+-------------+
| |               I
| |               I
| | +-------------V-------------+
| | |   Shows the main window   |
| | +-------------+-------------+
| |               I 
| |               I
| | +-------------V-------------+
| | | Install the corresponding |
| | |   reactor, pyqt4reactor   |
| | +-------------+-------------+
| |               I
| |               I
| | +-------------V-------------+
| | |     Starts the reactor    |
| V +---------------------------+







Creates the main window 

Shows the main window

Installs the corresponding reactor called pyqt4reactor


Starts the reactor.