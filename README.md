[![Circle CI](https://circleci.com/gh/satnet-project/generic-client.svg?style=shield)](https://circleci.com/gh/satnet-project/generic-client)
[![Build Status](https://travis-ci.org/satnet-project/generic-client.svg?branch=master)](https://travis-ci.org/satnet-project/generic-client)
[![Coverage Status](https://coveralls.io/repos/satnet-project/generic-client/badge.svg?branch=master&service=github)](https://coveralls.io/github/satnet-project/generic-client?branch=master)
[![Code Health](https://landscape.io/github/satnet-project/generic-client/master/landscape.svg?style=flat)](https://landscape.io/github/satnet-project/generic-client/master)

### Generic client for SATNet project.

This repository contains the source code for a generic client of the 
SATNet network. 

This is the code for a GS with a TNC to demodulate/modulate the frames 
which are being received/sent from/to the satellite.

#### Installation

Steps to install the generic client for the SATNet network:

1. To install the dependencies run, from the Scripts folder:

`./setup.sh -i`

You will need root privileges.

#### Dependencies

Before starting the script should be activate the corresponding virtualenv to satisfy the required dependencies.

    source .venv/bin/activate

#### Normal operation

To run this script you have the following options:

1. If you want to enter data connection from the user interface.

    `python client_amp.py`

2. To start a serial connection directly from the command line will have to enter 
the parameters as follows:

    `python client_amp.py -g -n username -p userpassword -t slot -c serial -s serialport -b baudrate`
    
3. For a UDP connection you must set an ip and a port: 

    `python client_amp.py -g -n username -p userpassword -t slot -c udp -i ip -u ipport`

For help about script usage enter:

	`python client_amp -help`

#### Other resources

A basic client-server implementation of the AMP protocol for Java and 
Python can be found at [this repository](https://github.com/xcrespo/Twisted-AMP-bidirectional)
