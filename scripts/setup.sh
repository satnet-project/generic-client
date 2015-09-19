#!/bin/bash
script_path="$( cd "$( dirname "$0" )" && pwd )"
project_path=$( readlink -e "$script_path/.." )
venv_path="$project_path/.venv"

# Install required packages
sudo apt install python-qt4

# Create a virtualenv
virtualenv $venv_path
source "$venv_path/bin/activate"
pip install -r "$script_path/requirements.txt"

# Downloading packages for GUI
# Needed to install SIP first
cd $venv_path
mkdir build && cd build
wget http://downloads.sourceforge.net/project/pyqt/sip/sip-4.16.9/sip-4.16.9.tar.gz
tar xzvf sip-4.16.9.tar.gz
cd sip-4.16.9
python configure.py
make
sudo make install
cd ../ && rm -r -f sip*

# PyQt4 installation.
wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
cd PyQt-x11-gpl-4.11.4
python ./configure.py -q /usr/bin/qmake-qt4
make
# Bug. Needed ldconfig, copy it from /usr/sbin
cp /sbin/ldconfig ../../bin/
sudo ldconfig
sudo make install
cd ../ && rm -r -f PyQt*