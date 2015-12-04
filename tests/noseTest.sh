
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

sudo apt-get install python-twisted
cp ../.gitmodules .
sed -i 's/git@github.com:/https:\/\/github.com\//' .gitmodules
git submodule update --init --recursive
cd ../protocol
git checkout jrpc_if
cd ../
mv protocol/ tests/
cd tests
virtualenv .venv_nosetest && source .venv_nosetest/bin/activate

echo '>>> Requirements installation'
pip install coveralls coverage nose
pip install -r ../requirements-tests.txt

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