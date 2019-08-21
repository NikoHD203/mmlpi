echo ====================
echo Installing Dependencies
echo ====================
apt install wget mesa-utils libalut0 libalut-dev -y
apt install python3 python3-pip python3-tk -y
pip3 install -r requirements.txt
pip3 install git+https://github.com/nicmcd/vcgencmd.git
echo ====================
echo Installing Java
echo ====================

if [ $(which java) ]; then echo 'Java Already Installed!'; fi
if [ ! $(which java) ]; then bash installJava.sh arm32; fi
# arm32 can be changed to arm64

echo ====================
echo Creating Shortcut
echo ====================
USER_HOME=$(eval echo ~${SUDO_USER})
echo "[Desktop Entry]" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Name=MMLPI" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Comment=Minecraft Launcher" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Exec=python3 $(pwd)/mmlpi.py" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Path=$(pwd)" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Icon=" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Terminal=true" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Type=Application" >> ${USER_HOME}/Desktop/mmlpi.desktop
echo "Encoding=UTF-8" >> ${USER_HOME}/Desktop/mmlpi.desktop
chmod +x ${USER_HOME}/Desktop/mmlpi.desktop
echo ====================
echo Permissions...
echo ====================
chmod -R 777 ../mmlpi
chmod +x mmlpi.py
echo ====================
echo Done!
echo Start with Desktop Shortcut or
echo cd mmlpi
echo python3 mmlpi.py
echo ====================
