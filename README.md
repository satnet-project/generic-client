[![Circle CI](https://circleci.com/gh/satnet-project/client.svg?style=shield)](https://circleci.com/gh/satnet-project/client)
[![Coverage Status](https://coveralls.io/repos/satnet-project/client/badge.svg?branch=master)](https://coveralls.io/r/satnet-project/client?branch=master)


client
======

This repository contains the source code for a generic client of the 
SATNet network. 
This is the code for a GS with a TNC to demodulate/modulate the frames 
which are being received/sent from/to the satellite.

In the file INSTALL you will find detailed installation instructions.

To run this script you have the following options:
1) ```python client_amp.py```
2) ```python client_amp.py -g -u username -p userpassword -t slot -c serial -s serialport -b baudrate```

Other resources
---------------
A basic client-server implementation of the AMP protocol for Java and 
Python can be found at [this repository](https://github.com/xcrespo/Twisted-AMP-bidirectional)
