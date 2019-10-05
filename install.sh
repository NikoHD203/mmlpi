if [[ ! -z $(which apt-get) ]]; then
    echo ====================
    echo Running apt update
    echo ====================
    apt update
    echo ====================
    echo Installing Python3, Git
    echo ====================
    apt install git python3 -y

echo ====================
echo Clonning Repo...
echo ====================
git clone https://github.com/Marekkon5/mmlpi mmlpi/
cd mmlpi/
chmod +x installer.py
python3 installer.py
python3 installer.py step2
