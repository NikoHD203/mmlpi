# MMLPi

### Minecraft Modern (Java Edition) Launcher For Raspberry Pi

#### Install:
```curl https://raw.githubusercontent.com/Marekkon5/mmlpi/master/install.sh | sudo bash```

#### Manual Installation:

    sudo apt install git libalut0 libalut-dev mesa-utils python3 python3-pip openjdk-8-jre-headless -y
    git clone https://github.com/Marekkon5/mmlpi mmlpi/
    cd mmlpi/
    sudo pip3 install -r requirements.txt
    python3 mmlpi.py


If you get Assistive Technology not found: org.GNOME.Accessibility.AtkWrapper error:

    sed -i -e '/^assistive_technologies=/s/^/#/' /etc/java-*-openjdk/accessibility.properties

Source: https://askubuntu.com/questions/695560/assistive-technology-not-found-awterror

#### Credits:
- rpiMike for LWJGL2 Raspberry Pi Natives

#### Tested Versions (RPi 4 4GB):

|Version | Works | OptiFine | Forge|
|:------:|:-----:|:--------:|:----:|
|1.14.3| :heavy_check_mark: | :x: | :heavy_check_mark: |
|1.13.2| :x: |||
|1.12.2| :heavy_check_mark: | :heavy_check_mark: *| :x: |
|1.11.2| :heavy_check_mark: | :heavy_check_mark: *| :x: |
|1.10.2| :heavy_check_mark: | :heavy_check_mark: *| :x: |
|1.9.4| :heavy_check_mark: | :heavy_check_mark: *| :x: |
|1.8.9| :x: |||
|1.7.10| :x: |||
|1.6.4| :heavy_check_mark: | :heavy_minus_sign: | :heavy_minus_sign: |
|1.5.2| :heavy_check_mark: | :heavy_check_mark: | :x: |
|1.4.7| :heavy_check_mark: | :heavy_minus_sign: | :heavy_check_mark: |
|1.4.5| :heavy_check_mark: | :heavy_check_mark: | :x: |
|1.3.2| :heavy_check_mark: | :o: | :heavy_check_mark: |
&ast; - Needs patched launchwrapper (Tools > Fix LaunchWrapper)
- :heavy_check_mark: - Works
- :x: - Not Working
- :heavy_minus_sign: - Doesn't Exist
- :o: - Other Error

#### Known Issues:

1. Versions 1.8.9, 1.7.10 - Malformed JSON error. Reinstall, Clean Install doesn't work

2. Forge and OptiFine (<1.14) has missing launchwrapper. Dirty (partial) fix is in Tools > Fix LaunchWrapper

