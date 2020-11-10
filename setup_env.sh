#!/usr/bin/env bash
# sets up the environment for task planning w/ common-sense project

echo "****************************"
echo "sourcing the Python 3 virtual env"
echo "****************************"
source ./py36_venv/bin/activate

echo "****************************"
echo "updating the PYTHONPATH to include packages"
echo "****************************"
SIM="/media/adaruna3/melodic/RSR/rail_tasksim/simulation:"
OTHER="/media/adaruna3/melodic/RSR:"
SELF="${PWD}:"
export PYTHONPATH="$SIM$OTHER$SELF$PYTHONPATH"
