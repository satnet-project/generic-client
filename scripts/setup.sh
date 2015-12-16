#!/bin/bash

#    Copyright 2015 Samuel Góngora García

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# :Author:
#     Samuel Góngora García (s.gongoragarcia@gmail.com)

# __author__ = 's.gongoragarcia@gmail.com'

script_path="$( cd "$( dirname "$0" )" && pwd )"
project_path=$( readlink -e "$script_path/.." )

if [ $1 == '-install' ];
then
	venv_path="$project_path/.venv"

	# Enable serial access
	currentUser=$(whoami)
	sudo usermod -a -G dialout $currentUser 

	# Install required packages
	sudo apt --assume-yes install build-essential 
	sudo apt --assume-yes install virtualenv
	sudo apt --assume-yes install python-qt4
	sudo apt --assume-yes install libqt4-dev 
	sudo apt --assume-yes install unzip
	sudo apt --assume-yes install python-pip
	sudo apt --assume-yes install python-dev
	sudo apt --assume-yes install libffi-dev
	sudo apt --assume-yes install libssl-dev
 	sudo apt --asumme-yes install libcanberra-gtk-module
 	sudo apt --assume-yes install shc

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
	python configure.py
	make
	sudo make install
	cd ../ && rm -r -f sip*

	# PyQt4 installation.
	wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
	tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
	cd PyQt-x11-gpl-4.11.4
	python ./configure.py --confirm-license --no-designer-plugin -q /usr/bin/qmake-qt4 -e QtGui -e QtCore
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
	
	# binary creation
	cd ../scripts
	sudo shc -f satnet.sh
	sudo chmod 777 satnet.sh.x
	sudo chown $currentUser satnet.sh.x
	mv satnet.sh.x satnet

	mkdir ~/bin/
	mkdir ~/.satnet/
	mkdir ~/.satnet/client/

	sudo mkdir /opt/satnet/

	pwd
	sudo cp logo.png /opt/satnet/

	cp satnet.desktop ~/Escritorio
	cp satnet.destkop ~/Desktop

	mv satnet ~/bin/
	cp -r -f ../ ~/.satnet/client/ 
	cd ../

	# Deactivate virtualenv
	deactivate
fi

if [ $1 == '-circleCI' ];
then
    mkdir key
    # 1: Generate a Private Key
    echo '>>> Generating a private key'
    openssl genrsa -des3 -passout pass:satnet -out key/test.key 1024
    # 2: Generate a CSR (Certificate Signing Request)
    echo '>>> Generating a CSR'
    openssl req -new -key key/test.key -passin pass:satnet -out key/test.csr -subj /CN=example.humsat.org/ 
    # 3: Remove Passphrase from Private Key
    echo '>>> Removing passphrase from private key'
    openssl rsa -in key/test.key -passin pass:satnet -out key/test.key
    # 4: Generating a Self-Signed Certificate
    echo '>>> Generating a public key (certificate)'
    openssl x509 -req -days 365 -in key/test.csr -signkey key/test.key -out key/test.crt

    echo '>>> Generating key bundles'
    # 5: Generate server bundle (Certificate + Private key)
    cat key/test.crt key/test.key > key/server.pem
    # 6: Generate clients bundle (Certificate)
    cp key/test.crt key/public.pem

    mv key ../tests
    echo '>>> Python modules installation'
	pip install -r "$project_path/requirements-tests.txt"

	echo '>>> SIP installation'
	mkdir build && cd build
	pip install SIP --allow-unverified SIP --download="."
	unzip sip*
	cd sip*
	python configure.py
	make
	make install
	sudo make install
	cd ../ && rm -r -f sip*

	echo '>>> PyQt4 installation'
	wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
	tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
	cd PyQt-x11-gpl-4.11.4
 	python ./configure.py --confirm-license --no-designer-plugin -q /usr/bin/qmake-qt4 -e QtGui -e QtCore

	make
	# Bug. Needed ldconfig, copy it from /usr/sbin
	cp /sbin/ldconfig ../../bin/

	sudo ldconfig
	sudo make install
	make install
	cd ../ && rm -r -f PyQt*
fi

if [ $1 == '-travisCI' ];
then
    mkdir key

    # 1: Generate a Private Key
    echo '>>> Generating a private key'
    openssl genrsa -des3 -passout pass:satnet -out key/test.key 1024
    # 2: Generate a CSR (Certificate Signing Request)
    echo '>>> Generating a CSR'
    openssl req -new -key key/test.key -passin pass:satnet -out key/test.csr -subj /CN=example.humsat.org/ 
    # 3: Remove Passphrase from Private Key
    echo '>>> Removing passphrase from private key'
    openssl rsa -in key/test.key -passin pass:satnet -out key/test.key
    # 4: Generating a Self-Signed Certificate
    echo '>>> Generating a public key (certificate)'
    openssl x509 -req -days 365 -in key/test.csr -signkey key/test.key -out key/test.crt

    echo '>>> Generating key bundles'
    # 5: Generate server bundle (Certificate + Private key)
    cat key/test.crt key/test.key > key/server.pem
    # 6: Generate clients bundle (Certificate)
    cp key/test.crt key/public.pem

    cp -r key ../
	cp -r key ../tests

    cd ../../
    echo '>>> Python modules installation'
    pip install coveralls
    pip install coverage
    pip install nose
	pip install -r "$project_path/requirements-tests.txt"
fi

if [ $1 == '-local' ];
then
	venv_path="$project_path/.venv_test"

	mkdir key
	# 1: Generate a Private Key
	echo '>>> Generating a private key'
	openssl genrsa -des3 -passout pass:satnet -out key/test.key 1024
	# 2: Generate a CSR (Certificate Signing Request)
	echo '>>> Generating a CSR'
	openssl req -new -key key/test.key -passin pass:satnet -out key/test.csr -subj /CN=example.humsat.org/ 
	# 3: Remove Passphrase from Private Key
	echo '>>> Removing passphrase from private key'
	openssl rsa -in key/test.key -passin pass:satnet -out key/test.key
	# 4: Generating a Self-Signed Certificate
	echo '>>> Generating a public key (certificate)'
	openssl x509 -req -days 365 -in key/test.csr -signkey key/test.key -out key/test.crt

	echo '>>> Generating key bundles'
	# 5: Generate server bundle (Certificate + Private key)
	cat key/test.crt key/test.key > key/server.pem
	# 6: Generate clients bundle (Certificate)
	cp key/test.crt key/public.pem
	mv key ../tests

	# Create a virtualenv
	virtualenv $venv_path
	source "$venv_path/bin/activate"
	pip install -r "$project_path/requirements.txt"

	echo '>>> SIP installation'
	mkdir build && cd build
	pip install SIP --allow-unverified SIP --download="."
	unzip sip*
	cd sip*
	python configure.py
	make
	sudo make install
	cd ../ && rm -r -f sip*

	echo '>>> PyQt4 installation'
	wget http://downloads.sourceforge.net/project/pyqt/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
	tar xvzf PyQt-x11-gpl-4.11.4.tar.gz
	cd PyQt-x11-gpl-4.11.4
	python ./configure.py --confirm-license --no-designer-plugin -q /usr/bin/qmake-qt4
	make
	# Bug. Needed ldconfig, copy it from /usr/sbin
	cp /sbin/ldconfig ../../bin/
	sudo ldconfig
	sudo make install
	cd ../ && rm -r -f PyQt*
fi

if [ $1 == '-uninstall' ];
then
	sudo apt --assume-yes remove build-essential 
	sudo apt --assume-yes remove virtualenv
	sudo apt --assume-yes remove python-qt4
	sudo apt --assume-yes remove libqt4-dev 
	sudo apt --assume-yes remove unzip
	sudo apt --assume-yes remove python-pip
	sudo apt --assume-yes remove python-dev
	sudo apt --assume-yes remove libffi-dev
	sudo apt --assume-yes remove libssl-dev
 	sudo apt --asumme-yes remove libcanberra-gtk-module
 	sudo apt --assume-yes remove shc

 	echo '>>> Do you wish to remove all program files?'

 	echo '>>> do you with to remove configuration files?'
fi

if [ $1 == '-help' ];
then
	echo '>>> No argument'
fi




