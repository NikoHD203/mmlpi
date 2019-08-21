echo ====================
echo Running apt update
echo ====================
apt update
echo ====================
echo Installing Git
echo ====================
apt install git -y
echo ====================
echo Clonning Repo...
echo ====================
git clone https://github.com/Marekkon5/mmlpi mmlpi/
cd mmlpi/
chmod +x localInstall.sh
bash localInstall.sh

