#!/bin/sh
#color
B='\033[0;34m'
G='\033[1;32m'
W='\033[1;37m'

chmod +x $HOME/EasY_HaCk/*
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
echo $W "Pleas accept........"
sleep 3
termux-setup-storage
sleep 6
mkdir /sdcard/EasY_HaCk
mkdir $HOME/EasY_HaCk-results
echo $W" Downloding start up .................."$G
sleep 3
echo " " $G
pip install --upgrade pip
pip install wordlist
mkdir $PREFIX/share/apache2/default-site/htdocs/zaki
mv $HOME/EasY_HaCk/.modules/Algeria.gif $PREFIX/share/apache2/default-site/htdocs/
mv $HOME/EasY_HaCk/.modules/index.html $PREFIX/share/apache2/default-site/htdocs/
cat $HOME/EasY_HaCk/.modules/zaki.tar.gza* > $HOME/EasY_HaCk/zaki.tar  
tar -zxvf $HOME/EasY_HaCk/zaki.tar
cd  $HOME/EasY_HaCk/
rm -rf zaki.tar
rm -rf zaki.tar.gza*
mv -f $HOME/EasY_HaCk/zaki.txt $HOME/EasY_HaCk/.modules/
mv -f zaki.txt $PREFIX/share/EasY_HaCk/.modules/
mv -v $HOME/zaki.txt $PREFIX/share/EasY_HaCk/.modules/
rm -rf $PREFIX/share/apache2/default-site/htdocs/index.html
rm -rf $HOME/EasY_HaCk/,modules/index.html 
rm -rf $HOME/EasY_HaCk/,modules/Algeria.gif
mv -f $HOME/EasY_HaCk/EasY_HaCk $PREFIX/bin/
mv -f $HOME/EasY_HaCk $PREFIX/share/
gcc $PREFIX/share/EasY_HaCk/.modules/.xerxes/xerxes.c -o xerxes 
mv $PREFIX/share/EasY_HaCk/xerxes $PREFIX/share/EasY_HaCk/.modules/.xerxes/
chmod +x $PREFIX/share/EasY_HaCk/*
chmod +x $PREFIX/bin/EasY_HaCk
chmod +x $PREFIX/share/EasY_HaCk/.modules/.*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.Infoga/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.theHarvester/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.CMSeeK/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.RED_HAWK/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.metagoofil/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.recon-ng/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.Python-Hash-Cracker/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.torshammer/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.slowloris/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.xerxes/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.sqlmap/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.theHarvester/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.metagoofil/*
chmod +x $PREFIX/share/EasY_HaCk/.modules/.Hash*
sleep 3
clear
pip install -r $PREFIX/share/EasY_HaCk/.modules/.Infoga/requirements.txt
sleep 3
pip2 install -r $PREFIX/share/EasY_HaCk/.modules/.recon-ng/REQUIREMENTS
sleep 3
pip install PySocks
sleep 3
python3 $PREFIX/share/EasY_HaCk/.modules/.slowloris/setup.py build
python3 $PREFIX/share/EasY_HaCk/.modules/.slowloris/setup.py install
clear
clear
figlet -f small "   DONE!"
echo "Now Type in new terminal ————>  EasY_HaCk"
sleep 3
EasY_HaCk


