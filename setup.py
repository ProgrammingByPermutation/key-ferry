# Creates an executable when 'setup.py build' is executed

import os
import site
import sys

import os

os.environ['TCL_LIBRARY'] = r"C:\Software\Python\Python3.6.2\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Software\Python\Python3.6.2\tcl\tk8.6"

from cx_Freeze import setup, Executable

site_packages = next((x for x in site.getsitepackages() if 'site-packages' in x), None)

# There is an error in the way cx_freeze grabs dependencies, for whatever reason it misses _cpyHook.pyd. Technically,
# the following "zip_includes" doesn't work. I just added it for fun. The "include_files" on the other hand does work.
build_exe_options = {
    # "packages": ["PIL", "win32gui"],
    "packages": ["win32gui"],
    "zip_includes": [(os.path.join(site_packages, "pyHook", "_cpyHook.cp36-win32.pyd"), os.path.join("pyHook", "_cpyHook.cp36-win32.pyd"))],
    "include_files": [os.path.join(site_packages, "pyHook"), "keyboard-space.ico", r"C:\Software\Python\Python3.6.2\DLLs\tcl86t.dll",
                      r"C:\Software\Python\Python3.6.2\DLLs\tk86t.dll", r"C:\Software\Python\Python3.6.2\Lib\site-packages\pywin32_system32\pythoncom36.dll",
                      r"C:\Software\Python\Python3.6.2\Lib\site-packages\pywin32_system32\pywintypes36.dll",]
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    # Uncomment as soon as we figure out why the error output ruins the program.
    # There is currently a bug between cx_Freeze and multiprocessing where launching a subprocess doesn't set the
    # sys.stdout and sys.stderr so the user gets a nasty pop-up when you close the application. Tried setting them
    # to file output myself but it didn't work.
    # # Executable('key_ferry.py', icon='keyboard-space.ico', base=base)
    Executable('key_ferry.py', icon='keyboard-space.ico'),
    Executable('python_executor.py', icon='keyboard-space.ico')
]

setup(name='KeyFerry',
      version='0.1',
      description='Definitely not the NSA...',
      executables=executables,
      options={"build_exe": build_exe_options}, requires=['pyHook']
      )
