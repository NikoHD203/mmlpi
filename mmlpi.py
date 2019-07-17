import requests
import os
import shutil
import time
import json
import inquirer
import subprocess
import re
import sys

import distutils.dir_util
import cli_ui

from packaging import version
from psutil import virtual_memory
from bs4 import BeautifulSoup
from zipfile import ZipFile

ROOTDIR = 'minecraft/'

def downloadVersion(vid, lwjgl3=False):

    # vid = index of version in version_manifest.json
    # lwjgl3 = for versions above 1.12

    r = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    version = requests.get(r.json()['versions'][vid]['url']).json()

    assetsURL = version['assetIndex']['url']
    downloadAssets(assetsURL, version["id"])
    
    if lwjgl3:
        libPaths = downloadLibraries(version['libraries'], lwjgl3=True)
        downloadLWJGL3Natives()
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives/LWJGL3/'))
    else:
        downloadRPiNatives()
        libPaths = downloadLibraries(version['libraries'])
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives/'))

    clientPath = os.path.abspath(os.path.join(ROOTDIR, f'versions/{version["id"]}'))
    if not os.path.isdir(clientPath):
        os.makedirs(clientPath)
    
    f = open(os.path.join(clientPath, f"{version['id']}.jar"), 'wb')
    f.write(requests.get(version['downloads']['client']['url']).content)
    f.close()

    f = open(os.path.join(clientPath, f'{version["id"]}.json'), 'w')
    f.write(json.dumps(version))
    f.close()

    cli_ui.info(f"Downloaded {version['id']}.jar")

    cli_ui.info('Done!')
    input('Press Enter To Continue...')

def downloadLibraries(lol, lwjgl3=False, lwjgl3arch='arm32'): #List of Libraries
    libsPath = os.path.abspath(os.path.join(ROOTDIR, 'libraries/'))
    if not os.path.isdir(libsPath):
        os.makedirs(libsPath)
    counter = 0

    libs = []
    for i in lol:
        if 'artifact' in i['downloads']:
            path = os.path.join(libsPath, i['downloads']['artifact']['path'])
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            f = open(path, 'wb')
            url = i['downloads']['artifact']['url']
            f.write(requests.get(url).content)
            f.close()
            libs.append(path)

        if 'classifiers' in i['downloads'] and 'natives-linux' in i['downloads']['classifiers']:
            path = os.path.join(libsPath, i['downloads']['classifiers']['natives-linux']['path'])
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            f = open(path, 'wb')
            if not lwjgl3:
                url = i['downloads']['classifiers']['natives-linux']['url']
            else:
                module = i['name'].split(':')[-2]
                url = f'https://build.lwjgl.org/nightly/bin/{module}/{module}-natives-linux-{lwjgl3arch}.jar'
                if requests.get(url).status_code != 200:
                    url = i['downloads']['classifiers']['natives-linux']['url']
            f.write(requests.get(url).content)
            f.close()

        # TODO: Native arm32 updater
        cli_ui.info_count(counter, len(lol), f"Downloaded {i['name']}")
        counter+=1
        cli_ui.info_progress('Libraries', counter, len(lol))

    return libs
def downloadAssets(url, v):
    r = requests.get(url)
    
    aiPath = os.path.abspath(os.path.join(ROOTDIR, 'assets/indexes'))
    if not os.path.isdir(aiPath):
        os.makedirs(aiPath)
    f = open(os.path.join(aiPath, f'{v}.json'), 'w')
    f.write(r.text)
    f.close()

    assets = r.json()

    assetsPath = os.path.abspath(os.path.join(ROOTDIR, 'assets/objects'))
    if not os.path.isdir(assetsPath):
        os.makedirs(assetsPath)
    counter = 0
    for i in assets['objects'].keys():
        h = assets['objects'][i]['hash']
        folder = os.path.join(assetsPath, h[0:2])
        if not os.path.isdir(folder):
            os.makedirs(folder)
        f = open(os.path.join(folder, h), 'wb')
        url = f'http://resources.download.minecraft.net/{h[0:2]}/{h}'
        f.write(requests.get(url).content)
        f.close()

        counter += 1
        cli_ui.info_count(counter, len(assets['objects'].keys()), f'Downloaded {i}')
        cli_ui.info_progress('Assets', counter, len(assets['objects'].keys()))

def downloadLWJGL3Natives(arch='arm32'):
    # Downloads LWJGL3 Natives from nightly official builds
    # All natives must be saved as name and name32 otherwise it gives an error

    natives = ['liblwjgl.so', 'libopenal.so', 'libglfw.so', 'liblwjgl_opengl.so', 'liblwjgl_stb.so']

    nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives/LWJGL3'))
    if not os.path.isdir(nativesPath):
        os.makedirs(nativesPath)

    counter = 0
    for i in natives:
        url = f'https://build.lwjgl.org/nightly/linux/{arch}/{i}'
        path = os.path.join(nativesPath, i)
        data = requests.get(url).content
        f = open(path, 'wb')
        f.write(data)
        f.close()
        path = os.path.join(nativesPath, i.replace('.so', '32.so'))
        f = open(path, 'wb')
        f.write(data)
        f.close()
        counter += 1
        cli_ui.info_count(counter, len(natives), f'Downloaded {i}')
        cli_ui.info_progress('Natives', counter, len(natives))

def downloadRPiNatives():

    # Custom build of libjwgl.so and libopenal.so
    natives = ['https://raw.githubusercontent.com/Marekkon5/mmlpi/master/liblwjgl.so',
                'https://raw.githubusercontent.com/Marekkon5/mmlpi/master/libopenal.so']

    nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives'))
    if not os.path.isdir(nativesPath):
        os.makedirs(nativesPath)
    counter = 0
    for i in natives:
        
        p = os.path.abspath(os.path.join(ROOTDIR, f'bin/natives/{os.path.basename(i)}'))
        r = requests.get(i)
        f = open(p, 'wb')
        f.write(r.content)
        f.close()

        counter += 1
        cli_ui.info_count(counter, len(natives), f'Downloaded {os.path.basename(i)}')
        cli_ui.info_progress(f'ARM Libraries', counter, len(natives))
        

def installOptifine(ver):

    # Installs optifine
    # Legacy versions = versions that aren't on official website
    # Need to be installed by repacking minecraft.jar

    legacyVersions = {
        '1.6.2': 'OptiFine_1.6.2_HD_U_B5',
        '1.5.2': 'OptiFine_1.5.2_HD_U_D5',
        '1.5.1': 'OptiFine_1.5.1_HD_U_D1',
        '1.5.0': 'OptiFine_1.5.0_HD_U_A7',
        '1.4.6': 'OptiFine_1.4.6_HD_U_D5',
        '1.4.5': 'OptiFine_1.4.5_HD_U_D8',
        '1.4.4': 'OptiFine_1.4.4_HD_U_D2',
        '1.4.3': 'OptiFine_1.4.3_HD_U_C1',
        '1.4.2': 'OptiFine_1.4.2_HD_U_B5',
        '1.4.1': 'OptiFine_1.4.1_HD_U_A5',
        '1.4.0': 'OptiFine_1.4.0_HD_U_A3',
        '1.3.2': 'OptiFine 1.3.2_HD_U_B4',
        '1.2.5': 'OptiFine 1.2.5_HD_C6',
        '1.2.3': 'OptiFine 1.2.3_HD_B',
        '1.1': 'OptiFine 1.1_HD_D6',
        '1.0.0': 'OptiFine 1.0.0_HD_D3'
    }
    if (ver in legacyVersions.keys()):
        url = getOptifineURL(f'http://optifine.net/adload.php?f={legacyVersions[ver]}.zip')
        if not url:
            cli_ui.error('Error Downloading OptiFine')
            input("Press Enter To Continue...")
        else:
            cli_ui.info('Installing Legacy OptiFine...')
            installLegacyOptifineOrForge(ver, url)
            cli_ui.info('Done')
    
    else:
        url = findOptifineURL(ver)
        if not url:
            cli_ui.error('No OptiFine Found!')
            input("Press Enter to Continue...")
        else:
            cli_ui.warning('Modern Versions of OptiFine Require Manual Installation!')
            if inquirer.confirm('Continue?', default=True):
                cli_ui.info('Please Wait...')

                f = open(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/optifine.jar')), 'wb')
                f.write(requests.get(url).content)
                f.close()

                f = open(os.path.abspath(os.path.join(ROOTDIR, 'launcher_profiles.json')), 'w')
                f.write(json.dumps({"profiles": {}}))
                f.close()

                cli_ui.info(cli_ui.bold, '===========================')
                cli_ui.info(cli_ui.bold, cli_ui.yellow, 'IMPORTANT:')
                cli_ui.info_1('Change Folder To:')
                cli_ui.info_2(cli_ui.bold, os.path.abspath(ROOTDIR))
                cli_ui.info_1('Then Press Install')
                cli_ui.info(cli_ui.bold, '===========================')

                f = open(os.devnull, "w")
                subprocess.call(['java', '-jar', os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/optifine.jar'))], stdout=f)

                os.remove(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/optifine.jar')))
                os.remove(os.path.abspath(os.path.join(ROOTDIR, 'launcher_profiles.json')))
                
                cli_ui.info('Done!')
                input('Press Enter To Continue...')

def installLegacyOptifineOrForge(ver, url):

    # Repack minecraft.jar with zip from url

    mod = requests.get(url)

    old = os.getcwd()
    os.chdir(os.path.join(ROOTDIR, f'versions/{ver}'))

    f = open('mod.jar', 'wb')
    f.write(mod.content)
    f.close()

    cli_ui.info('Download Successful')

    with ZipFile(f'{ver}.jar') as z:
        z.extractall('mc/')
    os.remove(f'{ver}.jar')

    with ZipFile(os.path.join('mod.jar')) as z:
        z.extractall('mod/')
    os.remove('mod.jar')

    distutils.dir_util.copy_tree('mod/', 'mc/')
    if (os.path.isdir(os.path.join('mc', 'META-INF'))):
        shutil.rmtree(os.path.join('mc', 'META-INF'))

    zipf = ZipFile(f'{ver}.jar', 'w')
    os.chdir('mc/')
    for r, d, f in os.walk('.'):
        for i in f:
            zipf.write(os.path.join(r, i))
    zipf.close()

    os.chdir('../')

    shutil.rmtree('mc/')
    shutil.rmtree('mod/')
    
    os.chdir(old)

    cli_ui.info('Patch Succesful')
    input('Press Enter to Continue...')

def findOptifineURL(v):

    # Scrapper for official OptiFine Website

    try:
        r = requests.get('https://optifine.net/downloads').text
        soup = BeautifulSoup(r, 'html.parser')
        o = []
        for link in soup.findAll('a'):
            if (f'http://optifine.net/adloadx?f=OptiFine_{v}_HD' in link.get('href')):
                o.append(link.get('href'))
        if (len(o) == 0):
            for link in soup.findAll('a'):
                if (f'http://optifine.net/adloadx?f=preview_OptiFine_{v}_HD' in link.get('href')):
                    o.append(link.get('href'))
            if (len(o) > 0):
                cli_ui.info('Using Preview Version of OptiFine')
        o.sort()
        return getOptifineURL(o[-1])
    except Exception:
        return False

def getOptifineURL(n):
    # The download url has random parameter, scrapper
    try:
        r = requests.get(n).text
        soup = BeautifulSoup(r, 'html.parser')
        for link in soup.findAll('a'):
            #download?... = legacy, downloadx?... = modern

            validFileNames = ['download?f=OptiFine_', 'downloadx?f=OptiFine_',
                            'downloadx?f=preview_OptiFine_']

            if any(fn in link.get('href') for fn in validFileNames):
                return 'http://optifine.net/' + link.get('href')
    except:
        return False

def auth(username, email, password):
    # Authentication. If error, returns xxx
    r = requests.post('https://authserver.mojang.com/authenticate', json={
        "agent": {"name": "Minecraft","version": 1},
        "username": email,
        "password": password})
    if 'accessToken' in r.json():
        accessToken = r.json()['accessToken']
    else:
        accessToken = 'xxx'
    r = requests.post('https://api.mojang.com/profiles/minecraft', json=[username])
    try:
        uuid = r.json()[0]['id']
    except Exception:
        uuid = 'xxx'
    return [accessToken, uuid]


def createLauncherSettings():
    # Creates (if doesn't exist) hidden .mclauncher file
    # It stores auth

    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    if not os.path.isfile(p): #Safe 
        f = open(p, 'w')
        f.write(json.dumps({
            'auth': {
                'username': '',
                'email': '',
                'password': ''
            }
        }))
        f.close()

def launch(ver):

    # Starts the game

    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    data = json.loads(open(p, 'r').read())
    a = auth(data['auth']['username'], data['auth']['email'], data['auth']['password'])
    versionInfo = json.loads(open(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/{ver}.json'))).read())
    
    # If more than 3GB RAM then 2GB
    if int(virtual_memory().total / (1024*1024)) > 3072:
        ram = '-Xmx2048M'
    else:
        ram = '-Xmx1024M'

    # Patches for inherited version
    libs = []
    libraryList = versionInfo['libraries']
    verID = versionInfo['id']
    try:
        argList = [i for i in versionInfo['arguments']['game'] if type(i) == str]
    except KeyError:
        argList = versionInfo['minecraftArguments'].split(' ')

    if ('inheritsFrom' in versionInfo.keys()):
        verID = versionInfo['inheritsFrom']
        verInfI = json.loads(open(os.path.abspath(os.path.join(ROOTDIR, f'versions/{verID}/{verID}.json'))).read())
        libraryList.extend(verInfI['libraries'])
        libs.append(os.path.abspath(os.path.join(ROOTDIR, f'versions/{verID}/{verID}.jar')))
        try:
            argList.extend([i for i in verInfI['arguments']['game'] if type(i) == str])
        except:
            argList.extend(verInfI['minecraftArguments'].split(' '))
    argList = list(dict.fromkeys(argList))

    # Get library List
    lwjgl3 = False
    for lib in libraryList:
        #Parse Java Lib Names
        name = lib['name'].split(':')
        path = name[0].replace('.', '/') + '/' + '/'.join(name[1:])
        filename = f"{name[-2]}-{name[-1]}.jar"
        f = os.path.abspath(os.path.join(ROOTDIR, f'libraries/{path}/{filename}'))
        if (os.path.isfile(f)):
            libs.append(f)    
        if (name[-2] == 'lwjgl' and version.parse(name[-1]) >= version.parse('3.0.0')):
            lwjgl3 = True
    libs.append(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/{ver}.jar')))
    classPath = ':'.join(libs)

    # Get together launch command
    cmd = ['java', '-Xmn128M', ram,
            '-XX:+UseConcMarkSweepGC',
            '-XX:+CMSIncrementalMode',
            '-XX:-UseAdaptiveSizePolicy']
    if (lwjgl3):
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives/LWJGL3/'))
    else:
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives/'))
    cmd.append(f'-Djava.library.path={nativesPath}')
    cmd.append('-cp')
    cmd.append(classPath)
    cmd.append(versionInfo['mainClass'])
    
    userType = 'mojang'
    if (a[0] == 'xxx' or a[1] == 'xxx'):
        userType = 'offline'

    # Argument replacer
    argum = [('${auth_player_name}', data['auth']['username']),
            ('${version_name}', versionInfo['id']),
            ('${game_directory}', os.path.abspath(ROOTDIR)),
            ('${assets_root}', os.path.abspath(os.path.join(ROOTDIR, 'assets/'))),
            ('${assets_index_name}', verID),
            ('${auth_uuid}', a[1]),
            ('${auth_access_token}', a[0]),
            ('${auth_session}', a[0]),
            ('${game_assets}', os.path.abspath(os.path.join(ROOTDIR, 'assets/'))),
            ('${user_type}', userType),
            ('${version_type}', versionInfo['type'])]

    for arg in argList:
        if (type(arg) == str):
            for i in argum:
                arg = arg.replace(i[0], i[1])
            cmd.append(arg)

    subprocess.run(cmd)
    input('Press Enter To Continue...')
    launcherUI()

def launcherUI():

    # CLI UI

    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    data = json.loads(open(p, 'r').read())

    os.system('clear')
    cli_ui.info('Welcome to', cli_ui.red, cli_ui.bold, 'Raspberry Pi', cli_ui.green, 'Minecraft', cli_ui.reset, 'Launcher!')
    cli_ui.info('Created by Me\n')

    ch = ['Play', 'Install', 'Login', 'Tools', 'Exit']
    c = inquirer.prompt([inquirer.List('menu', message='Select an Option', choices=ch)])
    c = ch.index(c['menu'])

    if (c == 0): #Play
        os.system('clear')

        if data['auth']['username'] == '':
            cli_ui.warning('You Must Set Username To Play!')
            input("Press Enter to Continue...")
            launcherUI()

        versions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions')))
        versions.sort()
        versions.append('Main Menu')
        ch = inquirer.prompt([inquirer.List('version', message='Select Version', choices=versions)])
        version = ch['version']

        if (versions.index(version) == len(versions)-1):
            launcherUI()
        else:
            os.system('clear')
            cli_ui.info(f'Staring Version {version}')
            launch(version)

    if (c == 1): # Install
        os.system('clear')
        versions = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json').json()['versions']

        cli_ui.warning('LWJGL3 Versions Are Poorly Optimized and Buggy!')

        ch = ['Snapshots', 'Experimental (LWJGL3)']
        c = inquirer.prompt([inquirer.Checkbox('c', message='Filters:', choices=ch)])['c']
        
        lwjgl3ver = versions.index(next(i for i in versions if i["id"] == "1.12.2"))  
        if (ch[1] in c):
            firstVer = 0
        else:
            firstVer = lwjgl3ver
        
        releases = []
        snapshots = []
        for i in range(firstVer, len(versions)-1):
            if (versions[i]['type'] == 'release'):
                releases.append(versions[i]['id'])
            else:
                snapshots.append(versions[i]['id'])
        
        if (ch[0] in c):
            v = inquirer.prompt([inquirer.List('version', message='Select Version', choices=releases+snapshots)])['version']
        else:
            v = inquirer.prompt([inquirer.List('version', message='Select Version', choices=releases)])['version']

        ver = versions.index(next(i for i in versions if i['id'] == v))
        cli_ui.info('Selected Version:', cli_ui.bold, v, cli_ui.reset, 'ID:', cli_ui.bold, ver)

        downloadVersion(ver, lwjgl3=(int(ver) < lwjgl3ver))
        launcherUI()

    if (c == 2): #Login
        os.system('clear')
        cli_ui.info("Email And Password Can Be Invalid If You Wish To Play Offline")
        login = inquirer.prompt([
            inquirer.Text(name='username', message='Enter Username'),
            inquirer.Text(name='email', message='Enter Email'),
            inquirer.Password(name='password', message='Enter Password')
        ])

        def __cont():
            choices = ['Test', 'Save', 'Discard']
            choice = choices.index(inquirer.prompt([inquirer.List('ch', message='Select Option', choices=choices)])['ch'])

            if (choice == 0):
                os.system('clear')
                a = auth(login['username'], login['email'], login['password'])
                if (a[0] == 'xxx'):
                    cli_ui.error('Invalid Email/Password')
                else:
                    cli_ui.info(cli_ui.bold, cli_ui.green, 'Login OK')
                if (a[1] == 'xxx'):
                    cli_ui.error('Invalid Username')
                else:
                    cli_ui.info(cli_ui.bold, cli_ui.green, 'Username Valid')
                __cont()
            
            if (choice == 1):
                cdata = json.loads(open(p, 'r').read())
                cdata['auth'] = login
                f = open(p, 'w')
                f.write(json.dumps(cdata))
                f.close()
                data = json.loads(open(p, 'r').read())
                launcherUI()
            
            if (choice == 2):
                launcherUI()

        os.system('clear')
        __cont()

    if (c == 3): #Tools
        # For Recursion
        def __toolsUI():
            try:
                model = open('/sys/firmware/devicetree/base/model', 'r').read().replace('\x00', '')
            except Exception:
                model = 'Not Raspberry Pi'
            ram = int(virtual_memory().total / (1024*1024))
            try:
                gpuram = subprocess.check_output(['vcgencmd', 'get_mem', 'gpu']).decode('utf-8')
                gpuram = re.findall(r'\d+', gpuram)[0]
            except Exception:
                gpuram = 0

            recmem = 64
            if (ram > 1024):
                recmem = 128
            if (ram > 3500):
                recmem = 256

            os.system('clear')
            cli_ui.info('Model:', cli_ui.bold, model)
            cli_ui.info('RAM:', cli_ui.bold, str(ram)+'MB')
            cli_ui.info('GPU Memory:', cli_ui.bold, str(gpuram)+'MB', cli_ui.reset, 'Recommended:', cli_ui.bold, str(recmem)+'MB\n')
            
            ch = ['Set Recommended GPU Memory', 'Set New GL Driver', 'Install OptiFine', 
            'Fix LaunchWrapper' ,'Install Forge', 'Update System (apt upgrade)', 'Menu']
            choice = ch.index(inquirer.prompt([inquirer.List('tools', message='Tools', choices=ch)])['tools'])
            
            if (choice == 0): #GPU Memory
                if os.path.isfile('/boot/config.txt'):
                    bootconfig = open('/boot/config.txt', 'r').read()
                    bootconfig = bootconfig.replace('gpu_mem=', '#gpu_mem=')
                    bootconfig += f'\ngpu_mem={recmem}'
                    
                    try:
                        f = open('/boot/config.txt', 'w')
                        f.write(bootconfig)
                        f.close()
                    except PermissionError:
                        cli_ui.error('You Need To Start This Script as Root!')

                    if inquirer.confirm('To Apply Changes You Need To Reboot. Reboot Now?', default=True):
                        os.system('sudo reboot')
                else:
                    cli_ui.error('/boot/config.txt Not Found, Not a Raspberry Pi')
                
            if (choice == 1): #GL Driver
                if os.path.isfile('/boot/config.txt'):
                    bootconfig = open('/boot/config.txt', 'r').read()
                    bootconfig = bootconfig.replace('dtoverlay=vc4-fkms-v3d', '#dtoverlay=vc4-fkms-v3d')
                    bootconfig += '\ndtoverlay=vc4-fkms-v3d'
                    
                    try:
                        f = open('/boot/config.txt', 'w')
                        f.write(bootconfig)
                        f.close()
                    except PermissionError:
                        cli_ui.error('You Need To Start This Script as Root!')

                    if inquirer.confirm('To Apply Changes You Need To Reboot. Reboot Now?', default=True):
                        os.system('sudo reboot')
                else:
                    cli_ui.error('/boot/config.txt Not Found, Not a Raspberry Pi')
            
            if (choice == 2): #Install Optifine
                os.system('clear')
            
                versions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions/')))
                versions.sort()
                ver = inquirer.prompt([inquirer.List('ver', message='Select Version', choices=versions)])['ver']
                installOptifine(ver)

            if (choice == 3):
                versions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions/')))
                versions.sort()
                ver = inquirer.prompt([inquirer.List('ver', message='Select Version', choices=versions)])['ver']
                fixLaunchWrapper(ver)

            if (choice == 4):
                os.system('clear')
                versions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions/')))
                versions.sort()
                ver = inquirer.prompt([inquirer.List('ver', message='Select Version', choices=versions)])['ver']
                installForge(ver)

            if (choice == 5): #apt upgrade
                subprocess.Popen(['sudo', 'apt', 'upgrade', '-y'])
            
            if (choice == 6): #Menu
                if (os.getuid() == 0):
                    os.system('clear')
                    cli_ui.warning('Running as Root! You Need To Restart The Script!')
                    sys.exit(0)
                launcherUI()

            __toolsUI() #On task done
        __toolsUI()


    if (c == 4):
        os.system('clear')
        cli_ui.info('Thank You!')
        sys.exit(0)

def installForge(ver):

    # Website scrapper for official Forge Website

    cli_ui.info('Please Wait...')
    url = f'https://files.minecraftforge.net/maven/net/minecraftforge/forge/index_{ver}.html'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    versions = []
    for link in soup.find_all('a'):
        l = link.get('href')
        if l != None:
            if f'forge-{ver}' in l and '-installer.jar' in l:
                versions.append(l)
    versions.sort()

    if (len(versions) != 0):
        url = f'https://files.minecraftforge.net{versions[-1]}'
        cli_ui.warning('Modern Versions of Forge Require Manual Installation!')
        if inquirer.confirm('Continue?', default=True):
            cli_ui.info('Please Wait...')
            r = requests.get(url).content
            f = open('forge.jar', 'wb')
            f.write(r)
            f.close()

            f = open(os.path.abspath(os.path.join(ROOTDIR, 'launcher_profiles.json')), 'w')
            f.write(json.dumps({"profiles": {}}))
            f.close()

            cli_ui.info(cli_ui.bold, '===========================')
            cli_ui.info(cli_ui.bold, cli_ui.yellow, 'IMPORTANT:')
            cli_ui.info_1('Change Folder To:')
            cli_ui.info_2(cli_ui.bold, os.path.abspath(ROOTDIR))
            cli_ui.info_1('Then Press OK')
            cli_ui.info(cli_ui.bold, '===========================')

            f = open(os.devnull, "w")
            subprocess.call(['java', '-jar', 'forge.jar'], stdout=f)
            
            os.remove('forge.jar')
            os.remove(os.path.abspath(os.path.join(ROOTDIR, 'launcher_profiles.json')))
            if (os.path.isfile('forge.jar.log')):
                os.remove('forge.jar.log')
            modsF = os.path.abspath(os.path.join(ROOTDIR, 'mods/'))
            if not os.path.isdir(modsF):
                os.mkdir(modsF)
            cli_ui.info('Done!')
            input('Press Enter To Continue...')
    else:
        versions = []
        for link in soup.find_all('a'):
            l = link.get('href')
            if l != None:
                if f'forge-{ver}' in l and '-universal.zip' in l:
                    versions.append(l)
        versions.sort()

        if (len(versions) == 0):
            cli_ui.info(cli_ui.red, cli_ui.bold, 'ERROR: No Forge Versions Found!')
            input('Press Enter to Continue...')
        else:
            url = f'https://files.minecraftforge.net{versions[-1]}'
            installLegacyOptifineOrForge(ver, url)
            modsF = os.path.abspath(os.path.join(ROOTDIR, 'mods/'))
            if (os.path.isdir(modsF)):
                os.mkdir(modsF)
            cli_ui.info('Done!')

def fixLaunchWrapper(ver):

    # Some versions of OptiFine (and Forge) don't download launchwrapper library
    # This downloads it and updates.

    path = os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/{ver}.json'))
    verjson = json.loads(open(path, 'r').read())

    for lib in verjson['libraries']:
        if (lib['name'].split(':')[-2] == 'launchwrapper'):
            Lpath = lib['name'].split(':')[0].replace('.', '/')
            Lpath += '/' + 'launchwrapper/1.12/launchwrapper-1.12.jar'
            Lpath = os.path.abspath(os.path.join(ROOTDIR, f'libraries/{Lpath}'))
            if not os.path.isdir(os.path.dirname(Lpath)):
                os.makedirs(os.path.dirname(Lpath))
            url = 'https://download.uskarian.net/mirrors/libraries.minecraft.net/net/minecraft/launchwrapper/1.12/launchwrapper-1.12.jar'
            r = requests.get(url)
            f = open(Lpath, 'wb')
            f.write(r.content)
            f.close()
            n = verjson['libraries'].index(lib)
            l = lib['name'].split(':')
            l[-1] = '1.12'
            l = ':'.join(l)
            verjson['libraries'][n] = {'name': l}
            f = open(path, 'w')
            f.write(json.dumps(verjson))
            f.close()
            cli_ui.info('Updated LaunchWrapper')
    input('Press Enter to Continue...')


createLauncherSettings()
launcherUI()
