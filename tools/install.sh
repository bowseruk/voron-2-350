#!/bin/sh

# This is the directory for this repo and then other used repos
repo="$HOME/voron-2-300"
klipper="$HOME/klipper"
katapult="$HOME/katapult"
network="/etc/network/interfaces.d"
printerdata="$HOME/printer_data"

# Setup the canbus network ready for the Octopus canbus bridge
sudo cp ${repo}/network/* ${network}

# Get a placeholder to make a unique folder
backupfolder=$(date +%Y%m%d_%H%M%S)

# Dump current contents of config and copy the linked printer.cfg
mkdir -p ${repo}/config/printer_data/backup/${backupfolder}
cp ${printerdata}/config/* ${repo}/config/printer_data/backup/${backupfolder}

# Setup the printer config files
cp ${repo}/config/printer_data/install/printer.cfg ${printerdata}/config
cp ${repo}/config/printer_data/moonraker/moonraker.cfg ${printerdata}/config
