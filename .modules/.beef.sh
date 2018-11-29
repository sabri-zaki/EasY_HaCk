#!/bin/bash
clear
#variable
beef=/data/data/com.termux/files/usr/share/beef-xss

#banner


echo "       ______    _______   _______   _______  "
echo "      (  ___ \  (  ____ \ (  ____ \ (  ____ \ "
echo "      | (   ) ) | (    \/ | (    \/ | (    \/ "
echo "      | (__/ /  | (__     | (__     | (__    "
echo "      |  __ (   |  __)    |  __)    |  __)   "
echo "      | (  \ \  | (       | (       | (      "
echo "      | )___) ) | (____/\ | (____/\ | )      "
echo "      |/ \___/  (_______/ (_______/ |/       "
echo 


#code                                 
if [ -d $beef ];
then
echo " You All read Have Beeeef on Your TERMUX "
else
echo "setup BeeF Repository ......."
sleep 4
pkg updates -y
sleep 1
pkg upgrade -y
sleep 1
pkg install dirmngr -y
sleep 1
apt-key adv --keyserver pool.sks-keyservers.net --recv 45F2964132545795
sleep 1
rm -rf $PREFIX/etc/apt/sources.list 
sleep 0.5
touch $PREFIX/etc/apt/sources.list 
sleep 0.5
clear
sleep 0.5
echo "deb https://termux.net stable main" > $PREFIX/etc/apt/sources.list 
sleep 1
echo "deb https://termux-x11.ml x11 main" >> $PREFIX/etc/apt/sources.list 
sleep 1
echo "deb [trusted=yes] https://hax4us.github.io/termux-tools/ extras main" >> $PREFIX/etc/apt/sources.list
sleep 1
pkg updates -y
sleep 1
pkg upgrade -y
sleep 1
clear
echo " BeeF Framework Installation..."
pkg install beef-xss -y
echo "done"
fi
