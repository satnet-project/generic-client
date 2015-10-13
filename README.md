[![Circle CI](https://circleci.com/gh/satnet-project/client.svg?style=shield)](https://circleci.com/gh/satnet-project/client)
[![Coverage Status](https://coveralls.io/repos/satnet-project/client/badge.svg?branch=master)](https://coveralls.io/r/satnet-project/client?branch=master)


### Generic client for SATNet project.


This repository contains the source code for a generic client of the 
SATNet network. 

This is the code for a GS with a TNC to demodulate/modulate the frames 
which are being received/sent from/to the satellite.

In the file INSTALL you will find detailed installation instructions.

#### Dependencies

Before starting the script should be activate the corresponding virtualenv to satisfy the required dependencies.

    source .venv/bin/activate

#### Normal operation

To run this script you have the following options:

1. If you want to enter data connection from the user interface.

    `python client_amp.py`

2. To start a serial connection directly from the command line will have to enter 
the parameters as follows:

    `python client_amp.py -g -u username -p userpassword -t slot -c serial -s serialport -b baudrate`
    
3. For a UDP connection you must set an ip and a port: 

    `python client_amp.py -g -u username -p userpassword -t slot -c udp -i ip -u ipport`

#### Installation

Steps to install the generic client for the SATNet network:

1. To install the dependencies run, from the Scripts folder:

`./setup.sh`

You will need root privileges.

#### Other resources

A basic client-server implementation of the AMP protocol for Java and 
Python can be found at [this repository](https://github.com/xcrespo/Twisted-AMP-bidirectional)
