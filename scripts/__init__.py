from pathlib import Path

import glob
import os
import fpclib
import time
import shutil

import tkinterweb
import tkinter
import PIL

PROJECT_DIR = Path(__file__).parent.parent

def rm(file):
    pfile = Path(file)
    if pfile.is_dir():
        shutil.rmtree(pfile)
    elif pfile.exists():
        pfile.unlink(True)

def rmpycache():
    for f in glob.glob("**/__pycache__", recursive=True):
        rm(f)

def update_defs():
    rmpycache()
    os.chdir(PROJECT_DIR / "sites")
    x = sorted(f for f in glob.glob("*.py"))
    x.insert(0, str(time.time()))
    fpclib.write("defs.txt", x)

def build():
    clean()
    os.system(f'pyinstaller fpcurator.py --onedir' + #' --upx-dir=upx' +
              f' --add-data="icon.png{os.pathsep}icon.png"' +
              f' --add-data="{tkinter.__path__[0]}{os.pathsep}tkinter"' +
              f' --add-data="{tkinterweb.__path__[0]}{os.pathsep}tkinterweb"' +
              f' --add-data="{PIL.__path__[0]}{os.pathsep}PIL"')

def clean():
    rmpycache()
    rm(PROJECT_DIR / "build")
    rm(PROJECT_DIR / "dist")