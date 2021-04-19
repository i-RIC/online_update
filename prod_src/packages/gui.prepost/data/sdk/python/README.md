# README

This document describes about how to setup an environment to develop and run
solvers for iRIC in Python.

## Use the environment that iRIC installer prepares

iRIC installer installs Python 3.8 using Miniconda. It also creates venv named "iric".
Please use that environment with the following steps.

1. Launch "Anaconda Prompt (Miniconda3)" from start menu.
2. Type the following command, to activate "iric" environment.

```
conda activate iric
```

## Use your own python environment

If you've setup your own python environment by yourself, and want to use that for
developing iRIC solvers, you need to install iric module by yourself.

You can do that with the following steps:

1. Make sure where the environment you are using exists. For example, if you are using anaconda,
   It will be under (Anaconda rootdir)\envs\(envname)

2. Make sure about the python version. You can do that with the following command below:
```
python --version
```

3. Copy iric.py to Lib\site-packages folder under the folder you've identified in step 1.
4. Rename _iric_pythonXX.pyd to _iric.pyd, and copy that to Lib\site-packages folder.
   For example, if python version was 3.8.6, you should use _iric_python38.pyd.
5. Copy the following files in the parent folder (i. e. "prepost" folder), to
   Lib\site-packages folder.

   * cgnsdll.dll
   * iriclib.dll
   * hdf5.dll
   * szip.dll
   * zlib.dll

5. Install numpy. When you are using Anaconda, you can do this with the following command:
```
conda install numpy
```

6. Launch python in the environment you've installed iric, and make sure it works,
   by inputting the following:

```
import iric
```

