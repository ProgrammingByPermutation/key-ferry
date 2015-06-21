# Creates an executable when 'setup.py build' is executed

import sys
import site
import os

from cx_Freeze import setup, Executable





# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

site_packages = next((x for x in site.getsitepackages() if 'site-packages' in x), None)
print(os.path.join(site_packages, "pyHook", "_cpyHook.pyd"))
print(os.path.join("pyHook", "_cpyHook.pyd"))

build_exe_options = {
    "zip_includes": [(os.path.join(site_packages, "pyHook", "_cpyHook.pyd"), os.path.join("pyHook", "_cpyHook.pyd"))],
    "include_files": [os.path.join(site_packages, "pyHook")]
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('key_ferry.py')
]

setup(name='KeyFerry',
      version='0.1',
      description='Automation testing shit show.',
      executables=executables,
      options={"build_exe": build_exe_options},
      )
