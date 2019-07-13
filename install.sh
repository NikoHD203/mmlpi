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
echo "[Desktop Entry]" >> ~/Desktop/mmlpi.desktop
echo "Name=MMLPI" >> ~/Desktop/mmlpi.desktop
echo "Comment=Minecraft Launcher" >> ~/Desktop/mmlpi.desktop
echo "Exec=python3 $(pwd)/mmlpi.py" >> ~/Desktop/mmlpi.desktop
echo "Path=$(pwd)" >> ~/Desktop/mmlpi.desktop
echo "Icon=" >> ~/Desktop/mmlpi.desktop
echo "Terminal=true" >> ~/Desktop/mmlpi.desktop
echo "Type=Application" >> ~/Desktop/mmlpi.desktop
echo "Encoding=UTF-8" >> ~/Desktop/mmlpi.desktop
chmod +x ~/Desktop/mmlpi.desktop
echo ====================
echo Done, Starting
echo ====================
python3 mmlpi.py