client
======

This repository contains the source code for a client of the SATNet network. This is the code for a GS with a TNC to demodulate/modulate the frames which are being received/sent from/to the satellite.

To install the dependencies execute:
```pip install -r requirements.txt```

The execute this script execute:
```python client_amp.py -u crespo -p cre.spo -s /dev/ttyUSB0 -b 115200 -i 2```
