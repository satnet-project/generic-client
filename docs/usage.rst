====================================
How to use the client's application.
====================================

| The program setup process can be done in three different ways.
| 1. Passing settings through the command line.
| 2. Entering the values directly in the application interface.
| 3. 


Tags
************************************

| * [-u <username>] # Set SATNET username to login
| * [-p <password>] # Set SATNET user password to login
| * [-t <slot_ID>] # Set the slot id corresponding to the pass.
| * [-c <connection>] # Set the type of interface with the GS.
| * [-s <serialport>] # Set serial port.
| * [-b <baudrate>] # Set serial port baudrate
| * [-i <ip>] # Set ip direction.
| * [-u <udpport>] # Set udp port.

Examples
************************************

| Example for serial config: 
| * Python client_amp.py -g -u crespo -p cre.spo -t 2 
|   -c serial -s /dev/ttyS1 -b 115200
| Example for udp config: 
| * python client_amp.py -g -u crespo -p cre.spo -t 2 
|   -c udp -i 127.0.0.1 -u 5001

Configuration file
************************************
| As previously mentioned configuration values can be stored in a 
| configuration file called config.ini. By selecting the appropriate 
| option in the program will be loaded at the beginning of each run.

| [User]
| username: crespo
| password: cre.spo
| slot_id: 2
| connection: udp
| [Serial]
| serialport: /dev/ttyUSB0
| baudrate: 9600
| [UDP]
| ip: 127.0.0.1
| udpport: 5005
