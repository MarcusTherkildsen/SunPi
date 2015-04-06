# SunPi 
Python script for streaming live data to plot.ly from a solar panel by means of a raspberry pi.
Live datafeed from SunPi here https://plot.ly/~marcus.therkildsen/221/sunpi/

# Installing everything needed for the raspberry pi

+ Activate i2c from sudo raspi-config

Go to sudo nano /etc/modules and add

i2c-bcm2708
i2c-dev


Then install these

sudo apt-get update
sudo apt-get install -y python-smbus i2c-tools


Restart and check if working 
lsmod | grep i2c_


Test hardware (remember to plug hardware in)
sudo i2cdetect -y 1

* Download and move the files for the current sensor
https://github.com/scottjw/subfact_pi_ina219


*Install plotly 
sudo apt-get install python-dev
sudo apt-get install python-pip (not sure if this is necessary)
sudo pip install plotly 

Grab a copy of the example file 
https://github.com/plotly/raspberrypi/archive/master.zip

Open and transfer to SunPi
remove adc stuff and insert username, api, token

*To start script on boot 
sudo crontab -e

and add 

@reboot (sleep 10; python /home/pi/SunPi/SunPi_Test.py) &

(& makes it run in the background)
