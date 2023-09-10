# How to Run the Program
## Desktop
1. Click on the icon for "launcher.sh" on the desktop
2. Select the option to "run in the terminal" when prompted

## Terminal
1. Open the terminal by clicking on the icon of a black screen with a ">_" on it. 
2. Type  `sh launcher.sh` into the interface and hit enter.
3. The program should run

# Setting up a new device for the first time
## Installing the OS onto the Raspberry PI 
Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Select Raspberry Pi OS (32 Bit) for the operating system and for Storage select the SD card you plan to use.  Write the OS to the SD card and eject it safely.

## Starting up the device 
Insert the SD into the Raspberry Pi and plug it in. Pick your preferred settings language, keyboard, etc. Connect to a WiFi network in the setup window to install the packages for upcoming steps. 

## Connecting to the internet
This program requires internet to function properly. To connect to the right network at the location this device is currently deployed at, the default network settings for Raspbian do not work. This can be fixed with the following process:
1. Install network-manager by running `sudo apt install network-manager` in the terminal
2. Run raspi-config, and go to advanced options
3. Select Network Config and choose "NetworkManager" for the network configuration
4. Reboot the device for the change to take effect
5. Configure the network by right clicking on the icon with two computers on the taskbar, and add new network
6. When configuring the network, make sure that the authentication setting is set correctly for the network.
## Installing dependencies
I used pip to install most of the dependencies for this project. They currently are:
    pandas
    gspread
    oauth2client
    pygame
In addition, run `sudo apt get pil.imagetk` to install PIL. Once you have installed the dependencies, clone the  repository and refer to the google sheets set up markdown to set up the google sheets integration. 

## Creating a launcher script
A launcher script simplifies the process for launching the program. One can be created using the following steps:
1. Create the file using `touch`
2. In it, add the following
`
#!/usr/bin/env
python [absolute path to python file]
`
3. Run `chmod u+x [name of shell]` to make the script executable
This can be assigned as a cron job to make the script run on boot. I am still trying to figure out the process for setting that up.
