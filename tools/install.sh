#!/bin/sh

# This is the directory for this repo and then other used repos
repo="$HOME/voron-2-300"
kiauh="$HOME/kiauh"
klipper="$HOME/klipper"
katapult="$HOME/katapult"
network="/etc/systemd/network"
udev="/etc/udev"
printerdata="$HOME/printer_data"


# Update the system and ready it for Kiauh
sudo apt-get update && sudo apt-get install git -y

# Setup the canbus network ready for the Octopus canbus bridge
sudo cp ${repo}/network/* ${network}/
# Add udev rules
sudo cp ${repo}/udev/* ${udev}/

if [ ! -d "$kiauh" ]; then
    cd ~ && git clone https://github.com/dw-0/kiauh.git
    ./kiauh/kiauh.sh
fi

# Get a placeholder to make a unique folder
backupfolder=$(date +%Y%m%d_%H%M%S)

# Dump current contents of config and copy the linked printer.cfg
mkdir -p ${repo}/config/printer_data/backup/${backupfolder}
cp ${printerdata}/config/*.cfg ${repo}/config/printer_data/backup/${backupfolder}

# Setup the printer config files
cp ${repo}/config/printer_data/install/printer.cfg ${printerdata}/config
cp ${repo}/config/printer_data/moonraker/moonraker.cfg ${printerdata}/config
