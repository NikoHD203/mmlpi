import os
import subprocess
import time
import sys
import platform

if 'arm' not in os.uname()[4] and 'aarch' not in os.uname()[4]:
    print('Not ARM! Exiting...')
    sys.exit(1)

def dependencies(tkinter=False):
    print('========================================')
    print('Installing Dependencies....')
    print('========================================')

    rc = subprocess.call(['which', 'apt-get'], stdout=open(os.devnull, 'wb'))
    if rc == 0:
        print('Installing Dependencies Using apt-get...')
        subprocess.call(['apt-get', 'install', 'wget', 'mesa-utils', 'libalut0', 'libalut-dev', '-qq'])
        subprocess.call(['apt-get', 'install', 'python3-pip', 'python3-tk', '-qq'])
        
    else:
        rc = subprocess.call(['which', 'emerge'], stdout=open(os.devnull, 'wb'))
        if rc == 0:
            print('Installing Dependencies Using emerge...')
            if tkinter:
                print('Need To Install Tkinter. This will take a long time!')
                time.sleep(5)
                f = open('/etc/portage/make.conf', 'r')
                content = f.read()
                f.close()
                ver = sys.version_info
                vers = f'{ver[0]}.{ver[1]}'
                content = content.replace('USE="', f'USE="dev-lang/python:{vers} tk')
                f = open('/etc/portage/make.conf', 'w')
                f.write(content)
                f.close()
                subprocess.call(['emerge', '--oneshot', '--newuse', f'dev-lang/python:{vers}'])
            
    if os.path.isfile('/etc/gentoo-release'):
        subprocess.call(['python3', '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])
        subprocess.call(['python3', '-m', 'pip', 'install', '--user', 'git+https://github.com/nicmcd/vcgencmd.git'])
        subprocess.call(['python3', '-m', 'pip', 'install', '--user', 'tqdm', 'requests'])
    else:
        subprocess.call(['python3', '-m', 'pip', 'install', '-r', 'requirements.txt'])
        subprocess.call(['python3', '-m', 'pip', 'install', 'git+https://github.com/nicmcd/vcgencmd.git'])
        subprocess.call(['python3', '-m', 'pip', 'install', 'tqdm', 'requests'])

def step2():
    print('\n')
    print('========================================')
    print('Installing Oracle Java....')
    print('========================================')

    rc = subprocess.call(['which', 'java'], stdout=open(os.devnull, 'wb'))
    if rc == 0:
        ch = input('Java is Already Installed. Overwrite with Oracle Java? [y/n] ').lower()
        if 'y' in ch:
            rc = 9

    if rc != 0:
        bits = platform.architecture()[0]
        if os.path.isfile('/etc/gentoo-release'):

            print('Preparing...')
            try:
                os.makedirs('/etc/portage/package.use/')
                os.makedirs('/etc/portage/package.license/')
            except Exception:
                pass

            f = open('/etc/portage/package.license/java', 'w')
            f.write('dev-java/oracle-jdk-bin Oracle-BCLA-JavaSE')
            f.close()

            f = open('/etc/portage/package.use/java', 'w')
            f.write('dev-java/oracle-jdk-bin headless-awt')
            f.close()

            subprocess.call(['emerge', 'dev-java/oracle-jdk-bin:1.8'])

            print('Downloading Java...')
            if bits == '64bit':
                url = 'https://www.dropbox.com/s/49qutc81bls8fyp/jdk-8u202-linux-arm64-vfp-hflt.tar.gz?dl=1'
            else:
                url = 'https://www.dropbox.com/s/jk8up5w3g2n0vfg/jdk-8u202-linux-arm32-vfp-hflt.tar.gz?dl=1'
            f = '/usr/portage/distfiles/jdk-8u202-linux-arm64-vfp-hflt.tar.gz'
            pbar = tqdm(unit='B', unit_scale=True, desc='Java')
            r = requests.get(url, stream=True)
            with(open(f, 'ab')) as file:
                for c in r.iter_content(chunk_size=1024):
                    if c:
                        file.write(c)
                        pbar.update(1024)
                file.close()

            pbar.close()
            print('Installing Java...')
            subprocess.call(['emerge', 'dev-java/oracle-jdk-bin:1.8'])
            subprocess.call(['java-config', '--set-system-vm', 'oracle-jdk-bin-1.8'])
            print('Oracle Java Installed!')
            
        else:
            print('Downloading Java...')
            if (bits == '64bit'):
                url = 'https://www.dropbox.com/s/g5q7bh2r7et5ym8/jdk-8u221-linux-arm64-vfp-hflt.tar.gz?dl=1'
            else:
                url = 'https://www.dropbox.com/s/p4mt1r2cbhv2obf/jdk-8u221-linux-arm32-vfp-hflt.tar.gz?dl=1'
            pbar = tqdm(unit='B', unit_scale=True, desc='Java')
            r = requests.get(url, stream=True)
            f = 'java.tar.gz'
            with(open(f, 'ab')) as file:
                for c in r.iter_content(chunk_size=1024):
                    if c:
                        file.write(c)
                        pbar.update(1024)
            pbar.close()
            print('Installing Java...')
            try:
                os.makedirs('/usr/lib/jvm')
            except Exception:
                pass
            subprocess.call(['tar', 'zxf', f, '-C', '/usr/lib/jvm'])
            os.system('update-alternatives --install "/usr/bin/java" "java" "/usr/lib/jvm/jdk1.8.0_221/bin/java" 0')
            os.system('update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/jvm/jdk1.8.0_221/bin/javac" 0')
            #subprocess.call(['update-alternatives', '--install', '"/usr/bin/java"', 'java', '/usr/lib/jvm/jdk1.8.0_221/bin/java', '0'])
            #subprocess.call(['update-alternatives', '--install', '"/usr/bin/javac"', 'javac', '/usr/lib/jvm/jdk1.8.0_221/bin/javac', '0'])
            subprocess.call(['update-alternatives', '--set', 'java', '/usr/lib/jvm/jdk1.8.0_221/bin/java'])
            subprocess.call(['update-alternatives', '--set', 'javac', '/usr/lib/jvm/jdk1.8.0_221/bin/java'])
            os.remove(f)
            print('Oracle Java Installed!')

    print('Permissions...')
    subprocess.call(['chmod', '-R', '777', '../mmlpi'])
    subprocess.call(['chmod', '+x', 'mmlpi.py'])
    print('\n')
    print('========================================')
    print('Done!')
    print('Start mmlpi by running:')
    print('python3 mmlpi.py')
    print('========================================')


if (len(sys.argv) > 1):
    try:
        import requests
        from tqdm import tqdm
        step2()
    except Exception:
        print('Missing Dependencies...')
        sys.exit(1)

else:
    try:
        from tkinter import *
        dependencies()
    except Exception:
        dependencies(tkinter=True)