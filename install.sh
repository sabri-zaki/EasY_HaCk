#!/bin/sh
#color

dir=/data/data/com.termux/files/home
server=/data/data/com.termux/files/usr/share/apache2/default-site/htdocs

cd $dir
chmod +700 EasY_HaCk/*
clear
apt-get update -y
clear
apt upgrade -y
clear
pkg install figlet -y
clear
figlet -f small installation
sleep 1
figlet -f small '0f'
sleep 1
figlet -f small EasY HaCk
sleep 1
figlet -f small Framwork
sleep 1
echo $W "Installing requirements........"$G
apt-get install curl -y
apt-get install tor -y
apt-get install perl -y
apt-get install git -y
apt-get install hydra -y
apt-get install python -y
apt-get install python2 -y
apt-get install php -y
apt-get install nmap -y
apt-get install apache2 -y 
apt-get install cowsay -y
apt-get install ruby -y
echo "Pleas accept........"
sleep 3
termux-setup-storage
sleep 6
mkdir /sdcard/EasY_HaCk
cd $dir
mkdir EasY_HaCk-results
cd $dir
pip install -r EasY_HaCk/.modules/.Infoga/requirements.txt
clear
sleep 1
pip2 install -r EasY_HaCk/.modules/.recon-ng/REQUIREMENTS
clear
sleep 1
pip install PySocks
clear
sleep 1
python3 EasY_HaCk/.modules/.slowloris/setup.py build
clear
python3 EasY_HaCk/.modules/.slowloris/setup.py install
clear
clear
echo " Downloding start up .................."
sleep 1
echo " " $G
pip install --upgrade pip
pip install wordlist
mkdir $PREFIX/share/apache2/default-site/htdocs/zaki
cd $dir
rm -rf $server/index.html
mv EasY_HaCk/.modules/Algeria.gif $server/
mv EasY_HaCk/.modules/index.html $server/
rm -rf EasY_HaCk/.modules/index.html 
rm -rf EasY_HaCk/.modules/Algeria.gif
cat EasY_HaCk/.modules/zaki.tar.gza* > EasY_HaCk/zaki.tar  
tar -zxvf EasY_HaCk/zaki.tar
mv zaki.txt EasY_HaCk/.modules/
cd $dir
gcc EasY_HaCk/.modules/.xerxes/xerxes.c -o xerxes 
mv EasY_HaCk/xerxes EasY_HaCk/.modules/.xerxes/
chmod +x EasY_HaCk/*
chmod +x EasY_HaCk/.modules/.*
chmod +x EasY_HaCk/.modules/*
chmod +x EasY_HaCk/.modules/.Infoga/*
chmod +x EasY_HaCk/.modules/.theHarvester/*
chmod +x EasY_HaCk/.modules/.CMSeeK/*
chmod +x EasY_HaCk/.modules/.RED_HAWK/*
chmod +x EasY_HaCk/.modules/.metagoofil/*
chmod +x EasY_HaCk/.modules/.recon-ng/*
chmod +x EasY_HaCk/.modules/.Python-Hash-Cracker/*
chmod +x EasY_HaCk/.modules/.torshammer/*
chmod +x EasY_HaCk/.modules/.slowloris/*
chmod +x EasY_HaCk/.modules/.xerxes/*
chmod +x EasY_HaCk/.modules/.sqlmap/*
chmod +x EasY_HaCk/.modules/.theHarvester/*
chmod +x EasY_HaCk/.modules/.metagoofil/*
chmod +x EasY_HaCk/.modules/.Hash*
cd $dir
rm -rf EasY_HaCk/zaki.tar
rm -rf EasY_HaCk/zaki.tar.gza*
rm -rf EasY_HaCk/.modules/zaki.tar.gza*
mv -f EasY_HaCk/zaki.txt EasY_HaCk/.modules/
mv -f EasY_HaCk/EasY_HaCk $PREFIX/bin/
mv -f EasY_HaCk $PREFIX/share/
cd $dir
rm -rf $HOME/EasY_HaCk
sleep 3
clear
figlet -f small "   DONE!"
echo "Now Type in new terminal ————>  EasY_HaCk"
sleep 3
EasY_HaCk


