#!/bin/bash
script_path="$( cd "$( dirname "$0" )" && pwd )"
project_path=$( readlink -e "$script_path/.." )
venv_path="$project_path/.venv"

# Install required packages
sudo apt-get install build-essential -f 
sudo apt-get install python-pip -f
sudo apt-get install python-dev -f
sudo apt-get install python-twisted

# Create a virtualenv
virtualenv $venv_path
source "$venv_path/bin/activate"
pip install -r "$project_path/requirements-tests.txt"