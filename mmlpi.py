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

from psutil import virtual_memory
from bs4 import BeautifulSoup
from zipfile import ZipFile

ROOTDIR = 'minecraft/'

def downloadVersion(vid, optifine):
    r = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    version = requests.get(r.json()['versions'][vid]['url']).json()

    assetsURL = version['assetIndex']['url']
    downloadAssets(assetsURL, version["id"])
    downloadLibraries(version['libraries'])
    downloadRPiNatives()

    clientPath = os.path.abspath(os.path.join(ROOTDIR, f'versions/{version["id"]}'))
    if not os.path.isdir(clientPath):
        os.makedirs(clientPath)
    
    f = open(os.path.join(clientPath, f"{version['id']}.jar"), 'wb')
    f.write(requests.get(version['downloads']['client']['url']).content)
    f.close()

    cli_ui.info(f"Downloaded {version['id']}.jar")

    if optifine:
        of = getOptifineURL(version['id'])
        if not of:
            cli_ui.warning('No Optifine')
        else:
            installOptifine(version['id'], of)

    getStartScript(version["id"], version['mainClass'])

def downloadLibraries(lol): #List of Libraries
    libsPath = os.path.abspath(os.path.join(ROOTDIR, 'libraries/'))
    if not os.path.isdir(libsPath):
        os.makedirs(libsPath)
    counter = 0
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

        if 'classifiers' in i['downloads'] and 'natives-linux' in i['downloads']['classifiers']:
            path = os.path.join(libsPath, i['downloads']['classifiers']['natives-linux']['path'])
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            f = open(path, 'wb')
            url = i['downloads']['classifiers']['natives-linux']['url']
            f.write(requests.get(url).content)
            f.close()

        cli_ui.info_count(counter, len(lol), f"Downloaded {i['name']}")
        counter+=1
        cli_ui.info_progress('Libraries', counter, len(lol))

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

def downloadNatives(arch='arm32'):
    natives = ['libjinput-linux.so', 'liblwjgl.so', 'libopenal.so', 'libglfw.so', 'liblwjgl_opengl.so',
    'liblwjgl_stb.so']

    nativesPath = os.path.abspath(os.path.join(ROOTDIR, 'bin/natives'))
    if not os.path.isdir(nativesPath):
        os.makedirs(nativesPath)

    for i in natives:
        #url = f'https://build.lwjgl.org/release/3.2.2/linux/{arch}/{i}'
        url = f'https://build.lwjgl.org/nightly/linux/{arch}/{i}'
        path = os.path.join(nativesPath, i)
        f = open(path, 'wb')
        f.write(requests.get(url).content)
        f.close()
        print(f'Saved {i}')

def downloadRPiNatives():
    natives = ['https://dl.dropboxusercontent.com/s/4oxcvz3ky7a3x6f/liblwjgl.so',
                'https://dl.dropboxusercontent.com/s/m0r8e01jg2og36z/libopenal.so']

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
        cli_ui.info(f'Downloaded {os.path.basename(i)}')
        cli_ui.info_progress(f'ARM Libraries', counter, len(natives))
        
def getStartScript(v, mainClass):
    libs = []
    for r, d, f in os.walk(os.path.abspath(os.path.join(ROOTDIR, 'libraries/'))):
        for i in f:
            if 'natives' not in i and '.jar' in i:
                libs.append(os.path.join(r, i))

    mcjar = os.path.abspath(os.path.join(ROOTDIR, f'versions/{v}/{v}.jar'))
    libs = ':'.join(libs) + f':{mcjar}'

    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    cur = json.loads(open(p, 'r').read())
    cur['versions'].append({
        'mainClass': mainClass,
        'gameDir': os.path.abspath(ROOTDIR),
        'cp': libs,
        'version': v
    })
    f = open(p, 'w')
    f.write(json.dumps(cur))
    f.close()

    cli_ui.info('Added to Launcher')


def installOptifine(ver, url):
    
    optifine = requests.get(url)
    libPath = os.path.abspath(os.path.join(ROOTDIR, f'libraries/optifine/OptiFine/{ver}/'))
    if not os.path.isdir(libPath):
        os.makedirs(libPath)
    f = open(os.path.join(libPath, 'Optifine.jar'), 'wb')
    f.write(optifine.content)
    f.close()

    old = os.getcwd()
    os.chdir(os.path.join(ROOTDIR, f'versions/{ver}'))

    f = open('optifine.jar', 'wb')
    f.write(optifine.content)
    f.close()

    cli_ui.info('Downloaded Optifine')

    with ZipFile(f'{ver}.jar') as z:
        z.extractall('mc/')
    os.remove(f'{ver}.jar')

    with ZipFile(os.path.join('optifine.jar')) as z:
        z.extractall('optifine/')
    os.remove('optifine.jar')

    distutils.dir_util.copy_tree('optifine/', 'mc/')
    shutil.rmtree(os.path.join('mc', 'META-INF'))

    zipf = ZipFile(f'{ver}.jar', 'w')
    os.chdir('mc/')
    for r, d, f in os.walk('.'):
        for i in f:
            zipf.write(os.path.join(r, i))
    zipf.close()

    os.chdir('../')

    shutil.rmtree('mc/')
    shutil.rmtree('optifine/')
    
    os.chdir(old)

    cli_ui.info('Patched with Optifine')


def getOptifineURL(v):
    try:
        r = requests.get('https://optifine.net/downloads').text
        soup = BeautifulSoup(r, 'html.parser')
        o = []
        for link in soup.findAll('a'):
            if (f'//optifine.net/adloadx?f=OptiFine_{v}' in link.get('href')):
                o.append(link.get('href'))
        o.sort()
        r = requests.get(o[-1]).text
        soup = BeautifulSoup(r, 'html.parser')
        for link in soup.findAll('a'):
            if (f'downloadx?f=OptiFine_' in link.get('href')):
                return 'https://optifine.net/' + link.get('href')
    except:
        return False

def auth(username, email, password):
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
    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))

    if not os.path.isfile(p): #Safe 
        f = open(p, 'w')
        f.write(json.dumps({
            "versions": [],
            'auth': {
                'username': '',
                'email': '',
                'password': ''
            }
        }))
        f.close()

def launch(vid):

    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    data = json.loads(open(p, 'r').read())
    
    a = auth(data['auth']['username'], data['auth']['email'], data['auth']['password'])

    cmd = ['java', '-Xmn128M', '-Xmx1024M',
            '-XX:+UseConcMarkSweepGC',
            '-XX:+CMSIncrementalMode',
            '-XX:-UseAdaptiveSizePolicy',
            f'-Djava.library.path={data["versions"][vid]["gameDir"]}/bin/natives/',
            '-cp', data["versions"][vid]['cp'],
            data["versions"][vid]['mainClass'],
            '--username', data['auth']['username'],
            '--uuid', a[1],
            '--version', data["versions"][vid]['version'],
            '--userProperties', '{}',
            '--gameDir', data["versions"][vid]["gameDir"],
            '--assetsDir', f'{data["versions"][vid]["gameDir"]}/assets',
            '--assetIndex', data["versions"][vid]['version'],
            '--accessToken', a[0],
            '--tweakClass', 'optifine.OptiFineTweaker']

    subprocess.run(cmd)

def launcherUI():
    home = os.path.expanduser("~")
    p = os.path.abspath(os.path.join(home, '.mclauncher'))
    data = json.loads(open(p, 'r').read())

    os.system('clear')
    cli_ui.info('Welcome to', cli_ui.red, cli_ui.bold, 'Raspberry Pi', cli_ui.green, 'Minecraft', cli_ui.reset, 'Launcher!')
    cli_ui.info('Created by Me\n')

    ch = ['Play', 'Install', 'Login', 'Troubleshooting', 'Exit']
    c = inquirer.prompt([inquirer.List('menu', message='Select an Option:', choices=ch)])
    c = ch.index(c['menu'])

    if (c == 0):
        os.system('clear')

        if data['auth']['username'] == '':
            cli_ui.warning('You Must Set Username To Play!')
            inquirer.prompt([inquirer.Text(name='a', message='Press Enter To Continue')])
            launcherUI()

        versions = [i['version'] for i in data['versions']]
        versions.append('Main Menu')
        ch = inquirer.prompt([inquirer.List('version', message='Select Version', choices=versions)])
        version = versions.index(ch['version'])

        if (version == len(versions)-1):
            launcherUI()
        else:
            os.system('clear')
            cli_ui.info(f'Staring Version {ch["version"]}')
            launch(version)

    if (c == 1):
        os.system('clear')
        versions = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json').json()['versions']
        releases = []
        snapshots = []
        for i in range(121, 274):
            if (versions[i]['type'] == 'release'):
                releases.append(versions[i]['id'])
            else:
                snapshots.append(versions[i]['id'])

        sn = inquirer.prompt([inquirer.Confirm('snapshots', message="Show Snapshots", default=False)])['snapshots']
        if sn:
            v = inquirer.prompt([inquirer.List('version', message='Select Version', choices=releases+snapshots)])['version']
        else:
            v = inquirer.prompt([inquirer.List('version', message='Select Version', choices=releases)])['version']

        ver = versions.index(next(i for i in versions if i['id'] == v))
        
        cli_ui.info('Selected Version:', cli_ui.bold, v, cli_ui.reset, 'ID:', cli_ui.bold, ver)
        op = inquirer.prompt([inquirer.Confirm('op', message="Install Optifine (If Available)", default=True)])['op']

        downloadVersion(ver, op)
        launcherUI()

    if (c == 2):
        os.system('clear')
        cli_ui.info("Email And Password Can Be Invalid If You Wish To Play Offline")
        login = inquirer.prompt([
            inquirer.Text(name='username', message='Enter Username'),
            inquirer.Text(name='email', message='Enter Email'),
            inquirer.Password(name='password', message='Enter Password')
        ])

        def cont():
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
                cont()
            
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
        cont()

    if (c == 3):
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

        os.system('clear')
        cli_ui.info(cli_ui.bold, 'Model:', cli_ui.reset, model)
        cli_ui.info(cli_ui.bold, 'RAM:', cli_ui.reset, str(ram)+'MB')
        cli_ui.info(cli_ui.bold, 'GPU Memory', cli_ui.reset, str(gpuram)+'MB\n')
        
        recmem = 64
        if (ram > 1024):
            recmem = 128
        if (ram > 3500):
            recmem = 256

        cli_ui.info('Recommended GPU Memory: ', cli_ui.bold, str(recmem)+'MB')
        cli_ui.info_2('You can change this by running:')
        cli_ui.info_3('sudo raspi-config')
        cli_ui.info_3('7 Advanced Options, A3 Memory Split')
        cli_ui.info_3('Then Reboot')
        cli_ui.info_2('It is also recommended to change the GL Driver')
        cli_ui.info_3('sudo raspi-config')
        cli_ui.info_3('7 Advanced Options, A7 GL Driver, G2 GL (Fake KMS)')
        cli_ui.info_3('Then Reboot')

        ch = ['Menu']
        choice = ch.index(inquirer.prompt([inquirer.List('c', message='Options', choices=ch)])['c'])

        if (choice == 0):
            launcherUI()

    if (c == 4):
        os.system('clear')
        cli_ui.info('Thank You!')
        sys.exit(0)

createLauncherSettings()
launcherUI()

# TODO: USERNAME IS A MUST
