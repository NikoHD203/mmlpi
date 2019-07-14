echo ====================
echo Running apt update
echo ====================
apt update
echo ====================
echo Installing Dependencies
echo ====================
apt install git libalut0 libalut-dev -y
apt install mesa-utils -y
echo ====================
echo Installing Java, Python3
echo ====================
apt install python3 python3-pip openjdk-8-jre-headless -y
echo ====================
echo Clonning Repo...
echo ====================
git clone https://github.com/Marekkon5/mmlpi mmlpi/
cd mmlpi/
echo ====================
echo Installing Dependencies
echo ====================
pip3 install -r requirements.txt
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