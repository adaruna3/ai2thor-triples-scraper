#!/usr/bin/env bash
# sets up the repo for task planning w/ common-sense project

# make bash exit if any single command fails
set -e
echo "****************************"
echo "installing some requirements"
echo "****************************"
sudo apt-get update
sudo apt-get install -y virtualenv

echo "****************************"
echo "creating the Python 3 virtual env"
echo "****************************"
virtualenv -p /usr/bin/python3.6 py36_venv
source ./py36_venv/bin/activate

echo "****************************"
echo "installing torch, visdom, & pandas"
echo "****************************"
pip install ai2thor