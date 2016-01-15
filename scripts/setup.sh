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

function create_selfsigned_keys()
{
    [[ -d $keys_dir ]] || {
        echo '>>> Creating keys directory...'
        mkdir -p $keys_dir
    } && {
        echo ">>> $keys_dir exists, skipping..."
    }

    [[ -f $keys_server_pem ]] && [[ -f $keys_public_pem ]] && {
        echo ">>> Keys already exist, skipping key generation..."
        return
    }

    # 1: Generate a Private Key
    echo '>>> Generating a private key'
    openssl genrsa -des3 -passout pass:satnet -out $keys_private 1024
    # 2: Generate a CSR (Certificate Signing Request)
    echo '>>> Generating a CSR'
    openssl req -new -key $keys_private -passin pass:satnet\
    	-out $keys_csr -subj "/CN=$keys_CN"
    # 3: Remove Passphrase from Private Key
    echo '>>> Removing passphrase from private key'
    openssl rsa -in $keys_private -passin pass:satnet -out $keys_private
    # 4: Generating a Self-Signed Certificate
    echo '>>> Generating a public key (certificate)'
    openssl x509 -req -days 365 -in $keys_csr -signkey $keys_private\
    	-out $keys_crt

    echo '>>> Generating key bundles'
    # 5: Generate server bundle (Certificate + Private key)
    cat $keys_crt $keys_private > $keys_server_pem
    # 6: Generate clients bundle (Certificate)
    cp $keys_crt $keys_public_pem
}

function install_packages()
{
	echo ">>> Installing system packages..."
	sudo aptitude update && sudo aptitude dist-upgrade -y
	sudo aptitude install $( cat "$linux_packages" ) -y
}

function uninstall_packages()
{
	echo ">>> Uninstalling system packages..."
	sudo aptitude remove $( cat "$linux_packages" ) -y
}

function install_sip()
{

	cd $venv_dir
	mkdir build && cd build
	wget http://downloads.sourceforge.net/project/pyqt/sip/sip-4.17/sip-4.17.tar.gz	
	tar -xvf sip-4.17.tar.gz
	cd sip-4.17
	python configure.py
	make
	sudo make install
	cd ../ && rm -rf sip-4.17
}

function install_pyqt4()
{

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
}

function install_venv()
{
	[[ -d $venv_dir ]] || {

    	echo ">>> Creating virtual environment..."
    	virtualenv --python=python2.7 $venv_dir
    	source "$venv_dir/bin/activate"
	    pip install -r "$project_path/requirements.txt"
	    deactivate

	} && {
	    echo ">>> Python Virtual environment found, skipping"
	}
}

script_path="$( cd "$( dirname "$0" )" && pwd )"
project_path=$( readlink -e "$script_path/.." )

linux_packages="$script_path/debian.packages"
venv_dir="$project_path/.venv"

_install_venv='true'
_install_packages='true'
_generate_keys='true'
_install_sip='true'
_install_pyqt4='true'

if [ $1 == '-install' ];
then
	# Enable serial access
	currentUser=$(whoami)
	sudo usermod -a -G dialout $currentUser 

	echo '>>> Installing packages'
	[[ $_install_packages == 'true' ]] && install_packages	

	echo '>>> Installing virtualenv'
	[[ $_install_venv == 'true' ]] && install_venv

	echo '>>> SIP installation'
	[[ $_install_sip == 'true' ]] && install_sip

	echo '>>> PyQt4 installation'
	[[ $_install_pyqt4 == 'true' ]] && install_pyqt4

	# man page creation
	source "$venv_dir/bin/activate"
	cd "$project_path/docs"
	make man
	cp _build/man/satnetclient.1 ../

	os=`cat /etc/issue.net`

	if [[ "$os" =~ "Debian" ]]; then
		# binary creation
		cd ../scripts
		sudo shc -f satnet.sh
		sudo rm satnet.sh.x.c
		sudo chmod 777 satnet.sh.x
		sudo chown $currentUser satnet.sh.x
		mv satnet.sh.x satnet

		mkdir ~/bin/
		mkdir ~/.satnet/
		mkdir ~/.satnet/client/

		sudo mkdir /opt/satnet/
		sudo cp ../icono.png /opt/satnet/
		# To-do. Move .desktop file according system language.
		cp satnet.desktop ~/Escritorio
		cp satnet.desktop ~/Desktop

		mv satnet ~/bin/
		cp -r -f ../ ~/.satnet/client/ 
		cd ../
	else
	    echo "Not Debian";
	fi

	# Deactivate virtualenv
	deactivate

	echo ">>> For apply changes you must reboot your system"
	echo ">>> Reboot now? (yes/no)"
	read OPTION
	if [ $OPTION == 'yes' ];
	then
		sudo reboot
	fi

fi

if [ $1 == '-circleCI' ];
then
	[[ $_generate_keys == 'true' ]] && create_selfsigned_keys
    mv key ../tests
    
    echo '>>> Python modules installation'
	pip install -r "$project_path/requirements-tests.txt"

	echo '>>> SIP installation'
	[[ $_install_sip == 'true' ]] && install_sip

	echo '>>> PyQt4 installation'
	[[ $_install_pyqt4 == 'true' ]] && install_pyqt4

fi

if [ $1 == '-travisCI' ];
then
	[[ $_generate_keys == 'true' ]] && create_selfsigned_keys
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
	venv_dir="$project_path/.venv_test"

	[[ $_generate_keys == 'true' ]] && create_selfsigned_keys
	mv key ../tests

	echo '>>> Installing virtualenv'
	[[ $_install_venv == 'true' ]] && install_venv

	echo '>>> SIP installation'
	[[ $_install_sip == 'true' ]] && install_sip

	echo '>>> PyQt4 installation'
	[[ $_install_pyqt4 == 'true' ]] && install_pyqt4
fi

if [ $1 == '-uninstall' ];
then
	echo ">>> Removing program files"
	sudo rm -r -f ~/.satnet/client/

	echo ">>> Removing executables"
	rm ~/bin/satnet

	echo ">>> Removing links"
	rm ~/Desktop/satnet.desktop
	rm ~/Escritorio/satnet.desktop

	echo ">>> Removing dependencies"
	[[ $_install_packages == 'true' ]] && uninstall_packages

 	echo ">>> Do you wish to remove all configuration files? (yes/no)"
 	read OPTION
 	if [ $OPTION == 'yes' ];
 	then
 		rm -r -f ~/.satnet
 	fi
fi