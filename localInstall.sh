echo 
echo ========================================
echo Installing Dependencies
echo ========================================
echo

# Install Basic Dependencies
if [[ ! -z $(which apt-get) ]]; then
    apt-get install wget mesa-utils libalut0 libalut-dev -y
    apt-get install python3 python3-pip python3-tk -y
else
    echo "WARNING: Can't find apt! Some dependencies couldn't be installed!"
fi

# Check if gentoo
if [ -f "/etc/gentoo-release" ]; then
    PIPPARAMS="--user"

    python3 -c 'from tkinter import *'
    if [ $? -ne 0 ]; then
        echo "Installing Tkinter for Gentoo"
        PV=$(python3 -c "import sys;v = sys.version_info;print(f'{v[0]}.{v[1]}')")
        sed -i -e "s/USE=\"/USE=\"dev-lang\/python:$PV tk/g" /etc/portage/make.conf
        emerge --oneshot --newuse dev-lang/python:$PV
    fi
    
else
    PIPPARAMS=""
fi

# Install Python/Pip dependencies
if [[ ! -z $(which pip3) ]]; then
    pip3 install $PIPPARAMS -r requirements.txt
    pip3 install $PIPPARAMS git+https://github.com/nicmcd/vcgencmd.git

elif [[ ! -z $(which python3) ]]; then
    python3 -m pip install $PIPPARAMS -r requirements.txt
    python3 -m pip install $PIPPARAMS git+https://github.com/nicmcd/vcgencmd.git

else
    echo "Python3 PIP Not Found! Aborting!"
    exit 1;
fi

# Java
echo
echo ========================================
echo Installing Java
echo ========================================
echo

if [ $(which java) ]; then 
    echo 'Java Already Installed!'; 
    read -p "Do you want to force install Oracle Java 8? (Y/n) " -n 1 -r
    echo 
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo 'Installing Java...'
        bash installJava.sh arm$(getconf LONG_BIT)
    fi
fi
if [ ! $(which java) ]; then bash installJava.sh arm$(getconf LONG_BIT); fi

read -p "Create Desktop Shortcut? (Y/n) " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo
    echo ========================================
    echo Creating Shortcut
    echo ========================================
    echo
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
fi
echo
echo ========================================
echo Permissions...
echo ========================================
echo
chmod -R 777 ../mmlpi
chmod +x mmlpi.py
echo
echo ========================================
echo Done!
echo Start with Desktop Shortcut or
echo cd mmlpi
echo python3 mmlpi.py
echo ========================================
echo