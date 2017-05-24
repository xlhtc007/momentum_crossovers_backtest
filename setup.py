# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "includes": ['matplotlib.backends.backend_tkagg', 'FileDialog'],

    "packages": ["Tkinter",
                 "tkFileDialog"],

    "excludes": ['collections.abc'],

    "include_files": ['data/index_300.csv',
                      'data/index_500.csv',
                      'data/index_800.csv',
                      'data/price.csv',
                      'data/price_origin.csv']}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'


setup(name='Momentum and Crossovers Backtest',
      version='0.1',
      description='Momentum and Crossovers Backtest Tool',
      options={"build_exe": build_exe_options},
      executables=[Executable("Main.py", base=base)]
      )
