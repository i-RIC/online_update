"""
Script to build dev installer.

To run this script, copy qt_ifw_path.template.py to qt_ifw_path.py,
and modify the path to fit your environment.
"""

import subprocess
import os
import sys
import shutil
import requests

from qt_ifw_path import QT_IFW_PATH

MINICONDA_PATH = 'dev_src/packages/miniconda/data'

MINICONDA_URLs = [
    "https://anaconda.org/conda-forge/intel-openmp/2020.3/download/win-64/intel-openmp-2020.3-h57928b3_311.tar.bz2",
    "https://anaconda.org/conda-forge/libblas/3.8.0/download/win-64/libblas-3.8.0-21_mkl.tar.bz2",
    "https://anaconda.org/conda-forge/libcblas/3.8.0/download/win-64/libcblas-3.8.0-21_mkl.tar.bz2",
    "https://anaconda.org/conda-forge/liblapack/3.8.0/download/win-64/liblapack-3.8.0-21_mkl.tar.bz2",
    "https://anaconda.org/conda-forge/mkl/2020.4/download/win-64/mkl-2020.4-hb70f87d_311.tar.bz2",
    "https://anaconda.org/conda-forge/numpy/1.19.4/download/win-64/numpy-1.19.4-py38h0cc643e_1.tar.bz2"
]

def download(url, fname):
    resp = requests.get(url)
    with open(fname, 'wb') as f:
        for chunk in resp.iter_content(100000):
            f.write(chunk)

def download_for_offline():
    for URL in MINICONDA_URLs:
        fullpath = os.path.join(MINICONDA_PATH, os.path.basename(URL))
        if not os.path.exists(fullpath):
            print("Downloading {0}...".format(URL))
            download(URL, fullpath)

def delete_file_for_online():
    for URL in MINICONDA_URLs:
        fullpath = os.path.join(MINICONDA_PATH, os.path.basename(URL))
        if os.path.exists(fullpath):
            os.remove(fullpath)

def print_usage():
    print('Usage: python build_dev_installer.py MODE')
    print('  MODE: "offline" or "online"')

def setup_miniconda_setting(mode):
    src_path = 'dev_src/packages/miniconda/meta/installscript_{0}.qs'.format(mode)
    tgt_path = 'dev_src/packages/miniconda/meta/installscript.qs'

    shutil.copyfile(src_path, tgt_path)

    if mode =='offline':
        download_for_offline()

    elif mode == 'online':
        delete_file_for_online()

def build_installer(mode):
    """Run binarycreator to build online installer"""

    binc = QT_IFW_PATH + '\\bin\\binarycreator.exe'
    installer_name = 'iRIC_Installer_dev_{0}'.format(mode)

    #cmd = binc + ' --{0}-only -c dev_src/config/config.xml'.format(mode)
    cmd = binc + ' --{0}-only -c dev_src/config/config.xml'.format('offline')
    cmd += ' -p dev_src\\packages ' + installer_name

    print('building installer {0}.exe...'.format(installer_name))

    subprocess.check_output(cmd)

if len(sys.argv) < 2:
    print_usage()
    exit()

mode = sys.argv[1]

if not (mode == "online" or mode == "offline"):
    print('Wrong MODE %1'.format(mode))
    print_usage()
    exit()

setup_miniconda_setting(mode)
build_installer(mode)
