import os
import requests
import json
import subprocess
import _thread
import re
import platform
import time

import mmlpiCore

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk

from psutil import virtual_memory

ROOTDIR = 'minecraft/'

def ui():

    # Main window
    window = Tk()
    window.title('MMLPi GUI')
    window.resizable(False, False)

    n0 = ttk.Notebook(window)
    playF = ttk.Frame(n0)
    playF.grid()
    installF = ttk.Frame(n0)
    installF.grid()
    loginF = ttk.Frame(n0)
    loginF.grid()
    modsF = ttk.Frame(n0)
    modsF.grid()
    toolsF = ttk.Frame(n0)
    toolsF.grid()
    n0.add(playF, text='Play')
    n0.add(installF, text='Install')
    n0.add(loginF, text='Login')
    n0.add(modsF, text='Mods')
    n0.add(toolsF, text='Tools')
    n0.grid()

    # Play window
    playF.columnconfigure(1, weight=1)
    title = Label(playF, text='Welcome to mmlpi!')
    title.config(font=("Courier Bold", 18))
    title.grid(columnspan=3)
    Label(playF, text='Created by Me, Version: 1.1').grid(columnspan=3)
    la0 = Label(playF, text='Select Version:')
    la0.grid(column=0)
    lba0 = Listbox(playF)
    def refreshInstalledVersions():
        Iversions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions')))
        Iversions.sort()
        lba0.delete(0, END)
        lba0.insert(END, *Iversions)
    refreshInstalledVersions()
    lba0.grid(column=0, rowspan=10)
    lb0 = Label(playF, text='Options:',)
    lb0.grid(column=1, columnspan=2, row=2)
    
    lb1 = Label(playF, text='RAM:')
    lb1.grid(column=1, row=3)
    eb0 = Entry(playF, width=6)
    eb0.insert(END, '1024')
    eb0.grid(column=2, row=3)

    lb2 = Label(playF, text='Java Binary:')
    lb2.grid(column=1, row=4)
    eb1 = Entry(playF, width=12)
    eb1.insert(END, 'java')
    eb1.grid(column=2, row=4)

    cba0v = IntVar()
    cba0 = Checkbutton(playF, text='Use arm64 Natives', variable=cba0v)
    cba0.grid(column=1, columnspan=2, row=5)

    def startGame():
        a = json.loads(open(mmlpiCore.MCLAUNCHER, 'r').read())
        if (a['auth']['username'] == ''):
            messagebox.showerror('No Username!', 'Please set Username in the Login Tab')
        else:
            print('Please Wait...')
            version = lba0.get(lba0.curselection())
            ram = eb0.get()
            java = eb1.get()
            arch = 32 if cba0v.get() == 0 else 64
            _thread.start_new_thread(mmlpiCore.launch, (version, ram, java, arch))

    bb0 = Button(playF, text='Play!', command=startGame)
    bb0.grid(column=1, columnspan=2, row=7)
    def killjava():
        os.system('pkill java')
    bb1 = Button(playF, text='Kill Java', command=killjava)
    bb1.grid(column=1, columnspan=2, row=8)
    bb2 = Button(playF, text='Refresh Versions', command=refreshInstalledVersions)
    bb2.grid(column=1, columnspan=2, row=9)

    # Install Window
    lc0 = Label(installF, text='Install')
    lc0.config(font=("Courier Bold", 18))
    lc0.grid(columnspan=2)

    lc1 = Label(installF, text='Select Version:')
    lc1.grid(column=0, row=1)
    lbc0 = Listbox(installF)
    lbc0.grid(column=0, rowspan=10)

    lc2 = Label(installF, text='Filters:')
    lc2.grid(column=1, row=1)
    cc1v = IntVar()
    cc1 = Checkbutton(installF, text='Snapshots', variable=cc1v)
    cc1.grid(column=1, row=2)
    cc2v = IntVar()
    cc2 = Checkbutton(installF, text='LWJGL3 Versions', variable=cc2v)
    cc2.grid(column=1, row=3)

    def refreshversions():
        v = getVersions(snapshots=cc1v.get(), lwjgl3=cc2v.get())
        lbc0.delete(0, END)
        lbc0.insert(END, *v)

    bc0 = Button(installF, text='Refresh', command=refreshversions)
    bc0.grid(column=1, row=4)
    lc3 = Label(installF, text='Options:')
    lc3.grid(column=1, row=5)
    cc3v = IntVar()
    cc3 = Checkbutton(installF, text='Force Re-Download Assets', variable=cc3v)
    cc3.grid(column=1, row=6)
    cc4v = IntVar()
    cc4 = Checkbutton(installF, text='Force Re-Download Libraries', variable=cc4v)
    cc4.grid(column=1, row=7)
    cc5v = IntVar()
    cc5 = Checkbutton(installF, text='Install ARM64 Natives', variable=cc5v)
    cc5.grid(column=1, row=8)

    pbc0v = DoubleVar()
    def progressbarUpdate(cur):
        pbc0v.set(cur)
        window.update_idletasks()

    def finishCallback():
        messagebox.showinfo('Done', 'Download Finished!')
        pbc0v.set(0)
        refreshInstalledVersions()
        window.update_idletasks()

    def installButton():
        versions = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json').json()['versions']
        version = lbc0.get(lbc0.curselection())
        vid = versions.index(next(i for i in versions if i["id"] == version))
        forceAssets = True if cc3v.get() == 1 else False
        lwjgl3ver = versions.index(next(i for i in versions if i["id"] == "17w43a"))
        lwjgl = 2 if vid > lwjgl3ver else 3
        archbits = 32 if cc5v.get() == 0 else 64
        forceLibs = True if cc4v.get() == 1 else False
        _thread.start_new_thread(mmlpiCore.downloadVersion, (vid, forceAssets, lwjgl, archbits, progressbarUpdate, forceLibs, finishCallback))

    bc1 = Button(installF, text='Install', command=installButton)
    bc1.grid(column=1, row=9)
    
    pbc0 = ttk.Progressbar(installF, variable=pbc0v, maximum=100, length=300)
    pbc0.grid(columnspan=2, sticky=S)

    #Login Window
    loginF.columnconfigure(1, weight=1)

    ld0 = Label(loginF, text='Login')
    ld0.config(font=("Courier Bold", 18))
    ld0.grid(columnspan=2, row=0, sticky="NWE")

    ld1 = Label(loginF, text='Username:')
    ld1.grid(row=1, column=0, sticky=W)
    ed0 = Entry(loginF)
    ed0.grid(row=1, column=1, sticky=E)

    ld2 = Label(loginF, text='Email:')
    ld2.grid(row=2, sticky=W)
    ed1 = Entry(loginF)
    ed1.grid(row=2, column=1, sticky=E)

    ld3 = Label(loginF, text='Password:')
    ld3.grid(row=3, sticky=W)
    ed2 = Entry(loginF, show='*')
    ed2.grid(row=3, column=1, sticky=E)

    ld4 = Label(loginF, text='UUID:')
    ld4.grid(row=4, column=0, sticky=W)
    ld5v = StringVar()
    ld5v.set('xxx')
    ld5 = Label(loginF, textvariable=ld5v)
    ld5.grid(row=4, column=1, sticky=E)
    ld6 = Label(loginF, text='Access Token:')
    ld6.grid(row=5, column=0, sticky=W)
    ld7v = StringVar()
    ld7v.set('xxx')
    ld7 = Label(loginF, textvariable=ld7v)
    ld7.grid(row=5, column=1, sticky=E)

    def check(ret=False):
        username = ed0.get()
        email = ed1.get()
        password = ed2.get()
        a = mmlpiCore.auth(username, email, password)
        ld5v.set(a[1])
        if (a[0] != 'xxx'):
            ld7v.set(a[0][0:8] + '***')
        else:
            ld7v.set('xxx')
        if ret:
            return a
    def save():
        cur = json.loads(open(mmlpiCore.MCLAUNCHER, 'r').read())
        cur['auth']['username'] =  ed0.get()
        cur['auth']['email'] =  ed1.get()
        cur['auth']['password'] =  ed2.get()
        f = open(mmlpiCore.MCLAUNCHER, 'w')
        f.write(json.dumps(cur))
        f.close()

    bd0 = Button(loginF, text='Check', command=check)
    bd0.grid(column=0, row=6, sticky=W)
    bd1 = Button(loginF, text='Save', command=save)
    bd1.grid(column=1, row=6, sticky=E)

    # Mods Window:
    modsF.columnconfigure(0, weight=1)

    le0 = Label(modsF, text='OptiFine, Forge, Modding')
    le0.config(font=("Courier Bold", 18))
    le0.grid(row=0, sticky="NWE")
    le1 = Label(modsF, text='Due to ToS OptiFine and Forge\nhave to be installed manually.')
    le1.grid()

    def openwebsite(url):
        devnull = open(os.devnull, 'wb')
        subprocess.Popen(['chromium-browser', url], stdout=devnull, stderr=devnull)
    def optifinewebsite():
        openwebsite('https://optifine.net/downloads')
    def forgewebsite():
        openwebsite('https://files.minecraftforge.net/')

    be0 = Button(modsF, text='Open OptiFine Website', command=optifinewebsite)
    be0.grid()
    be1 = Button(modsF, text='Open Forge Website', command=forgewebsite)
    be1.grid()
    le2 = Label(modsF, text='To Download Forge Click the Installer Button!')
    le2.grid()
    le3 = Label(modsF, text='You can install manually:\njava -jar Optifine_xxx.jar')
    le3.grid()
    p = os.path.abspath(ROOTDIR)
    le4 = Label(modsF, text=f'IMPORTANT: Change the path to:\n {p}')
    le4.grid()
    def openjar():
        f = filedialog.askopenfile(
            initialdir='~',
            title='Select .jar',
            filetypes=(('JAR File', '*.jar'),))
        messagebox.showinfo('Change Path!', f'Change the install path to: {p}')
        subprocess.check_output(['java', '-jar', f.name])
        refreshInstalledVersions()
    be2 = Button(modsF, text='Open .jar', command=openjar)
    be2.grid()

    #Tools Window
    toolsF.columnconfigure(0, weight=1)
    toolsF.columnconfigure(1, weight=1)

    lf0 = Label(toolsF, text='Tools')
    lf0.config(font=("Courier Bold", 18))
    lf0.grid(row=0, sticky="NWE", columnspan=2)
    
    try:
        pi = open('/sys/firmware/devicetree/base/model', 'r').read().replace('\x00', '')
        import vcgencmd
        gpumem = f"{vcgencmd.get_mem('gpu')/(1024*1024)}MB"
    except Exception:
        pi = 'Not a Raspberry Pi!'
        gpumem = 'Not a Raspberry Pi'

    ram = round(virtual_memory().total/(1024*1024))

    lf1 = Label(toolsF, text=f'Your Pi:\n{pi}')
    lf1.grid(columnspan=2)
    lf2 = Label(toolsF, text='RAM:')
    lf2.grid(row=2, column=0)
    lf3 = Label(toolsF, text=f'{ram}MB')
    lf3.grid(row=2, column=1)
    lf4 = Label(toolsF, text='GPU Memory:')
    lf4.grid(row=3, column=0)
    lf5 = Label(toolsF, text=gpumem)
    lf5.grid(row=3, column=1)
    lf6 = Label(toolsF, text='Arch:')
    lf6.grid(row=4, column=0)
    arch = f'{platform.machine()} ({platform.architecture()[0]})'
    lf7 = Label(toolsF, text=arch)
    lf7.grid(row=4, column=1)
    lf8 = Label(toolsF, text='Java: ')
    lf8.grid(row=5, column=0)
    java = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT).decode('utf-8').split('\n')[0]
    lf9 = Label(toolsF, text=java)
    lf9.grid(row=5, column=1)
    lf10 = Label(toolsF, text='You can change GPU Memory and Driver by running:\nsudo raspi-config')
    lf10.grid(row=6, columnspan=2)
    def tempmon():
        subprocess.Popen([sys.executable, 'mmlpiMonitor.py'])

    bf1 = Button(toolsF, text='Open Monitor Tool', command=tempmon)
    bf1.grid(row=7, columnspan=2)
    def makestartscript():
        top = Toplevel()
        tl0 = Label(top, text='Select Version:')
        tl0.grid(row=0, columnspan=2)
        Iversions = os.listdir(os.path.abspath(os.path.join(ROOTDIR, 'versions')))
        Iversions.sort()
        tcb0 = ttk.Combobox(top, values=Iversions)
        tcb0.grid(row=1, columnspan=2)
        tl1 = Label(top, text='RAM (MB):')
        tl1.grid(row=2, column=0)
        te0 = Entry(top, width=6)
        te0.grid(row=2, column=1)
        te0.insert(END, '1024')
        tl2 = Label(top, text='Java Binary:')
        tl2.grid(row=3, column=0)
        te1 = Entry(top, width=8)
        te1.grid(row=3, column=1)
        te1.insert(END, 'java')
        tcboxv = IntVar()
        tcbox = Checkbutton(top, text='ARM64 Natives', variable=tcboxv)
        tcbox.grid(row=4, columnspan=2)
        def createscript():
            ver = tcb0.get()
            ram = te0.get()
            java = te1.get()
            arch = 64 if tcboxv.get() == 1 else 32
            mmlpiCore.launch(ver, ram=ram, javabin=java, arch=arch, createScript=True)
            messagebox.showinfo('Script Saved', f'Saved as: {os.path.abspath(f"{ver}.sh")}')
            top.destroy()

        tb0 = Button(top, text='Create Script', command=createscript)
        tb0.grid(row=5, columnspan=2)

        top.mainloop()

    bf2 = Button(toolsF, text='Create Standalone Launch Script', command=makestartscript)
    bf2.grid(row=8, columnspan=2)

    window.mainloop()


def getVersions(lwjgl3=False, snapshots=False):
    versions = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json').json()['versions']
    lwjgl3ver = versions.index(next(i for i in versions if i["id"] == "17w43a"))
    if not lwjgl3:
        versions = versions[lwjgl3ver+1:]
    if not snapshots:
        versions = [v for v in versions if v['type'] != 'snapshot']
    return [v['id'] for v in versions]

