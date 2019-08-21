# MMLPi

### Minecraft Modern (Java Edition) Launcher For Raspberry Pi

### Version 1.1 Now with GUI!

#### Install:
```curl https://raw.githubusercontent.com/Marekkon5/mmlpi/master/install.sh | sudo bash```

NOTE: If you want to update, remove the old version: ```rm -rf mmlpi```

#### Manual Installation:

    sudo apt update
    sudo apt install -y git
    git clone https://github.com/Marekkon5/mmlpi
    cd mmlpi
    sudo bash localInstall.sh


#### Credits:
- rpiMike and jdonald - for testing and help with LWJGL3 and Java
- http://rogerallen.github.io/jetson/2014/07/31/minecraft-on-jetson-tk1/


#### Tested Versions (RPi 4 4GB, Raspbian Buster arm32):

|Version | Works | OptiFine | Forge|
|:------:|:-----:|:--------:|:----:|
|1.12.2| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.11.2| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.10.2| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.9.4| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.8.9| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.7.10| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
|1.6.4| :heavy_check_mark: | :heavy_minus_sign: | :heavy_minus_sign: |
|1.5.2| :heavy_check_mark: | :heavy_check_mark: | :x: |
|1.4.7| :heavy_check_mark: | :heavy_minus_sign: | :heavy_check_mark: |
|1.4.5| :heavy_check_mark: | :heavy_check_mark: | :x: |
|1.3.2| :heavy_check_mark: | :o: | :heavy_check_mark: |

- :heavy_check_mark: - Works
- :x: - Not Working
- :heavy_minus_sign: - Doesn't Exist
- :o: - Other Error

NOTE: LWJGL3 Versions (1.13 and above) are currently NOT WORKING!


#### Scripts:
- ```install.sh``` - Clones the Repo and starts localInstall.sh
- ```localInstall.sh``` - Installs dependencies and mmlpi
- ```installJava.sh``` - Installs Oracle Java. ```bash installJava.sh <arm32|arm64>```
- ```mmlpi.py``` - MMLPi Launcher
- ```mmlpiCore.py``` - Install, Launch functions
- ```mmlpiGUI.py``` - GUI
- ```mmlpiMonitor.py``` - Monitor Window. Can be launched standalone ```python3 mmlpiMonitor.py```

#### 3rd Party Natives and Libraries Sources:
- https://github.com/Marekkon5/mmlpilibraries
- https://www.lwjgl.org/browse/nightly/linux/


