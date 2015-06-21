# Creates an executable when 'setup.py build' is executed

import sys

from cx_Freeze import setup, Executable


# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('key_ferry.py', base=base)
]

setup(name='KeyFerry',
      version='0.1',
      description='Sample cx_Freeze Tkinter script',
      executables=executables
      )
