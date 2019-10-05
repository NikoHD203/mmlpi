import requests
import os
import shutil
import time
import json
import subprocess
import re
import sys

import distutils.dir_util

from tqdm import tqdm
from packaging import version
from zipfile import ZipFile

ROOTDIR = 'minecraft/'
MCLAUNCHER = os.path.abspath('.mclauncher')

def downloadVersion(vid, forceAssets=False, lwjglver=2, archbits=32, progressCallback=None, forceLibraries=False, finishCallback=None):

    print('Please Wait...')

    # vid = index of version in version_manifest.json
    r = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
    version = requests.get(r.json()['versions'][vid]['url']).json()

    assetsURL = version['assetIndex']['url']
    downloadAssets(assetsURL, version["id"], forceAssets, progressCallback=progressCallback)
    lwjgl3 = True if lwjglver == 3 else False
    downloadLibraries(version['libraries'], lwjgl3=lwjgl3, lwjgl3arch=f'arm{archbits}', progressCallback=progressCallback, redownload=forceLibraries)
    downloadNatives(lwjglver, archbits, progressCallback=progressCallback)

    clientPath = os.path.abspath(os.path.join(ROOTDIR, f'versions/{version["id"]}'))
    if not os.path.isdir(clientPath):
        os.makedirs(clientPath)
    
    pbar = tqdm(total=version['downloads']['client']['size'], unit='B', unit_scale=True, unit_divisor=1024)
    r = requests.get(version['downloads']['client']['url'], stream=True)
    with open(os.path.join(clientPath, f"{version['id']}.jar"), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
            pbar.update(1024)
        f.close()
    pbar.close()

    print(f"Downloaded {version['id']}.jar")

    f = open(os.path.join(clientPath, f'{version["id"]}.json'), 'w')
    f.write(json.dumps(version))
    f.close()

    print('Done!')

    if finishCallback != None:
        finishCallback()

def downloadLibraries(lol, lwjgl3=False, lwjgl3arch='arm32', progressCallback=None, redownload=False): #List of Libraries
    libsPath = os.path.abspath(os.path.join(ROOTDIR, 'libraries/'))
    if not os.path.isdir(libsPath):
        os.makedirs(libsPath)
    
    pbar = tqdm(total=len(lol))

    for i in lol:

        if 'artifact' in i['downloads']:
            path = os.path.join(libsPath, i['downloads']['artifact']['path'])
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            url = i['downloads']['artifact']['url']
            if not os.path.isfile(path) or redownload:
                f = open(path, 'wb')
                f.write(requests.get(url).content)
                f.close()

        if 'classifiers' in i['downloads'] and 'natives-linux' in i['downloads']['classifiers']:
            path = os.path.join(libsPath, i['downloads']['classifiers']['natives-linux']['path'])
            folder = os.path.dirname(path)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            if not os.path.isfile(path) or redownload:
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

        pbar.update(1)
        if progressCallback != None:
            per = int((lol.index(i)/len(lol))*100)
            progressCallback(per)
    pbar.close()

def downloadAssets(url, v, force=False, progressCallback=None):
    r = requests.get(url)
    
    aiPath = os.path.abspath(os.path.join(ROOTDIR, 'assets/indexes'))
    if not os.path.isdir(aiPath):
        os.makedirs(aiPath)
    f = open(os.path.join(aiPath, f'{v}.json'), 'w')
    f.write(r.text)
    f.close()

    assets = r.json()

    totalSize = 0
    for i in assets['objects'].keys():
        totalSize += assets['objects'][i]['size']
    pbar = tqdm(total=totalSize, unit='B', unit_scale=True, unit_divisor=1024)

    assetsPath = os.path.abspath(os.path.join(ROOTDIR, 'assets/objects'))
    if not os.path.isdir(assetsPath):
        os.makedirs(assetsPath)
    
    for i in assets['objects'].keys():
        h = assets['objects'][i]['hash']
        folder = os.path.join(assetsPath, h[0:2])
        if not os.path.isdir(folder):
            os.makedirs(folder)

        if os.path.isfile(os.path.join(folder, h)) and not force:
            pbar.update(assets['objects'][i]['size'])
        else:
            f = open(os.path.join(folder, h), 'wb')
            url = f'http://resources.download.minecraft.net/{h[0:2]}/{h}'
            f.write(requests.get(url).content)
            f.close()
            pbar.update(assets['objects'][i]['size'])
                
            if progressCallback != None:
                per = int((list(assets['objects'].keys()).index(i)/len(assets['objects'].keys()))*100)
                progressCallback(per)
    pbar.close()

def downloadNatives(ver, bits, progressCallback=None):
    #Downloads Natives
    #Ver = 2 or 3
    #Bits = 32 or 64

    nativesPath = os.path.abspath(os.path.join(ROOTDIR, f'bin/natives/lwjgl{ver}/arm{bits}/'))
    if not os.path.isdir(nativesPath):
        os.makedirs(nativesPath)

    if (ver == 2):
        url = f'https://github.com/Marekkon5/mmlpilibraries/raw/master/lwjgl2/arm{bits}/'
        files = ['liblwjgl.so', 'libopenal.so']
    
    if (ver == 3):
        url = f'https://build.lwjgl.org/nightly/linux/arm{bits}/'
        files = ['liblwjgl.so', 'libopenal.so', 'libglfw.so', 'liblwjgl_opengl.so', 'liblwjgl_stb.so']

    pbar = tqdm(total=len(files))
    for i in files:
        u = url + i
        data = requests.get(u).content
        if (bits == 32 and ver == 3):
            path = os.path.join(nativesPath, i.replace('.so', '32.so'))
        else:
            path = os.path.join(nativesPath, i)
        f = open(path, 'wb')
        f.write(data)
        f.close()

        pbar.update(1)
        if progressCallback != None:
            per = int((files.index(i)/(len(files)-1))*100)
            progressCallback(per)
    pbar.close()

def installLegacyOptifineOrForge(ver, url):

    # Repack minecraft.jar with zip from url

    mod = requests.get(url)

    old = os.getcwd()
    os.chdir(os.path.join(ROOTDIR, f'versions/{ver}'))

    f = open('mod.jar', 'wb')
    f.write(mod.content)
    f.close()

    print('Download Successful')

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

    print('Patch Succesful')

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
    # also creates the base folders

    p = os.path.abspath(os.path.join(ROOTDIR, 'versions/'))
    if not os.path.isdir(p):
        os.makedirs(p)
    
    p = os.path.abspath(os.path.join(ROOTDIR, 'launcher_profiles.json'))
    if not os.path.isfile(p):
        f = open(p, 'w')
        f.write(json.dumps({
            'profiles': {}
        }))
        f.close()
    
    if not os.path.isfile(MCLAUNCHER): #Safe 
        f = open(MCLAUNCHER, 'w')
        f.write(json.dumps({
            'auth': {
                'username': '',
                'email': '',
                'password': ''
            }
        }))
        f.close()

def launch(ver, ram=1024, javabin='java', arch=32, createScript=False):

    # Starts the game

    data = json.loads(open(MCLAUNCHER, 'r').read())
    a = auth(data['auth']['username'], data['auth']['email'], data['auth']['password'])
    versionInfo = json.loads(open(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/{ver}.json'))).read())
    
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
        else:
            if (name[-2] == 'launchwrapper'):
                print('Downloading LaunchWrapper...')
                os.makedirs(os.path.abspath(os.path.join(ROOTDIR, f'libraries/{path}')))
                url = 'https://github.com/Marekkon5/mmlpilibraries/raw/master/launchwrapper-1.12.jar'
                r = requests.get(url)
                fi = open(f, 'wb')
                fi.write(r.content)
                fi.close()
                libs.append(f)    
                print('Done')
            else:
                url = ''
                if 'url' in lib.keys():
                    if (lib['url'][-4:] == '.jar'):
                        url = lib['url']
                    else:
                        baseurl = lib['url']
                else:
                    baseurl = 'https://libraries.minecraft.net/'
                if (url == ''):
                    url = f'{baseurl}{name[0].replace(".", "/")}/{name[1]}/{name[2]}/{name[1]}-{name[2]}.jar'
                r = requests.get(url)
                if (r.status_code == 200):
                    os.makedirs(os.path.abspath(os.path.join(ROOTDIR, f'libraries/{path}')))
                    fi = open(f, 'wb')
                    fi.write(r.content)
                    fi.close()
                    libs.append(f)
                    print(f'Downloaded {lib["name"]}')
                else:
                    print(f'Missing Library: {lib["name"]}')
                    print('In cases of -platform libraries this can be ignored.')

        if (name[-2] == 'lwjgl' and version.parse(name[-1]) >= version.parse('3.0.0')):
            lwjgl3 = True
    libs.append(os.path.abspath(os.path.join(ROOTDIR, f'versions/{ver}/{ver}.jar')))
    classPath = ':'.join(libs)

    # Get together launch command
    cmd = [javabin, '-Xmn128M', f'-Xmx{ram}M',
            '-XX:+UseConcMarkSweepGC',
            '-XX:+CMSIncrementalMode',
            '-XX:-UseAdaptiveSizePolicy']
    if (lwjgl3):
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, f'bin/natives/lwjgl3/arm{arch}'))
    else:
        nativesPath = os.path.abspath(os.path.join(ROOTDIR, f'bin/natives/lwjgl2/arm{arch}'))
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
            ('${user_properties}', '{}'),
            ('${version_type}', versionInfo['type'])]

    for arg in argList:
        if (type(arg) == str):
            for i in argum:
                arg = arg.replace(i[0], i[1])
            cmd.append(arg)

    if not createScript:
        subprocess.Popen(cmd)

    else:
        path = os.path.abspath('.')
        script = f'cd {path};\n{" ".join(cmd)}'
        f = open(f'{ver}.sh', 'w')
        f.write(script)
        f.close()
