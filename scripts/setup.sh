#!/bin/bash

if [ $1 == '-i' ];
then
	script_path="$( cd "$( dirname "$0" )" && pwd )"
	project_path=$( readlink -e "$script_path/.." )
	venv_path="$project_path/.venv"

	# Install required packages
	sudo apt --assume-yes install build-essential 
	sudo apt --assume-yes install virtualenv
	sudo apt --assume-yes install python-qt4
	sudo apt --assume-yes install libqt4-dev 
	sudo apt --assume-yes install unzip
	sudo apt --assume-yes install python-pip
	sudo apt --assume-yes install python-dev

	# Create a virtualenv
	virtualenv $venv_path
	source "$venv_path/bin/activate"
	pip install -r "$project_path/requirements.txt"

	# Downloading packages for GUI
	# Needed to install SIP first
	cd $venv_path
	mkdir build && cd build
	pip install SIP --allow-unverified SIP --download="."
	unzip sip*
	cd sip*
	# python configure.py
	# echo yes | python configure.py
	python configure.py
	make
	sudo make install
	cd ../ && rm -r -f sip*

	# PyQt4 installation.
	wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
	tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
	cd PyQt-x11-gpl-4.11.4
	python ./configure.py --confirm-license -q /usr/bin/qmake-qt4
	make
	# Bug. Needed ldconfig, copy it from /usr/sbin
	cp /sbin/ldconfig ../../bin/
	sudo ldconfig
	sudo make install
	cd ../ && rm -r -f PyQt*

	# man page creation
	source "$venv_path/bin/activate"
	cd "$project_path/docs"
	make man
	cp _build/man/satnetclient.1 ../
	deactivate

elif [ $1 == '-t' ];
then
	# script_path="$( cd "$( dirname "$0" )" && pwd )"
	# project_path=$( readlink -e "$script_path/.." )
	# venv_path="$project_path/.venv_test"

	# Install required packages
	sudo apt-get install build-essential -f 
	sudo apt-get install python-pip -f
	sudo apt-get install python-dev -f
	sudo apt-get install python-twisted

	# Create a virtualenv
	# virtualenv $venv_path
	# source "$venv_path/bin/activate"
	pip install -r "$project_path/requirements-tests.txt"

	# cd $venv_path
	mkdir build && cd build
	pip install SIP --allow-unverified SIP --download="."
	unzip sip*
	cd sip*
	# python configure.py
	# echo yes | python configure.py
	python configure.py
	make
	sudo make install
	cd ../ && rm -r -f sip*

	# PyQt4 installation.
	wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
	tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
	cd PyQt-x11-gpl-4.11.4
	python ./configure.py --confirm-license -q /usr/bin/qmake-qt4
	make
	# Bug. Needed ldconfig, copy it from /usr/sbin
	cp /sbin/ldconfig ../../bin/
	sudo ldconfig
	sudo make install
	cd ../ && rm -r -f PyQt*

fi




