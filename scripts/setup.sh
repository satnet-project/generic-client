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
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.8/sip-4.16.8.tar.gz
tar xvzf sip-4.16.8.tar.gz
python sip-4.16.8/configure.py --incdir="$virtualenv/include/python2.7"
make
make install
rm sip-4.16.8.tar.gz
rm -R sip-4.16.8

# This hook is run after a new virtualenv is activated.
# ~/.virtualenvs/postmkvirtualenv
# Source (@jlesquembre): https://gist.github.com/jlesquembre/2042882

libs=( PyQt4 sip.so )
 
python_version=python$(python -c "import sys; print (str(sys.version_info[0])+'.'+str(sys.version_info[1]))")
var=( $(which -a $python_version) )
 
get_python_lib_cmd="from distutils.sysconfig import get_python_lib; print (get_python_lib())"
lib_virtualenv_path=$(python -c "$get_python_lib_cmd")
lib_system_path=$(${var[-1]} -c "$get_python_lib_cmd")
 
# for lib in ${libs[@]}
# do
#     ln -s $lib_system_path/$lib $lib_virtualenv_path/$lib 
# done