# scratchClient created by Gerhard Hepp

scratchClient is a client software for scratch1.4 remote sensor protocol

Quick install guide: Open a terminal and execute the following lines.

```  
cd
git clone https://github.com/Naohiro2g/scratchClient.git

cd scratchClient/
sudo apt-get update
sudo apt-get install python-pip  python-dev  python-smbus 
sudo apt-get install python3-pip python3-dev python3-smbus 
sudo pip  install tornado mako==1.0.6 spidev pyserial intelhex
sudo pip3 install tornado mako==1.0.6 spidev pyserial intelhex

python3 src/scratchClient.py -version
pip3 freeze | grep tornado

sudo pip3 uninstall tornado
sudo pip3 install tornado==4.5.3

cp RobohandSet/to_Desktop/RoboHand.desktop ~/Desktop/
cp RobohandSet/to_home/scratchClientRoboHand.py ~
cp RobohandSet/to_Scratch\ Project/ROBOHAND_template.sb  ~/Documents/Scratch\ Projects/
chmod 755 ../scratchClientRoboHand.py

```
