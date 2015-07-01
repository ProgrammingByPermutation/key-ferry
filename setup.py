# Creates an executable when 'setup.py build' is executed

import sys
import site
import os

from cx_Freeze import setup, Executable

site_packages = next((x for x in site.getsitepackages() if 'site-packages' in x), None)

# There is an error in the way cx_freeze grabs dependencies, for whatever reason it misses _cpyHook.pyd. Technically,
# the following "zip_includes" doesn't work. I just added it for fun. The "include_files" on the other hand does work.
build_exe_options = {
    "zip_includes": [(os.path.join(site_packages, "pyHook", "_cpyHook.pyd"), os.path.join("pyHook", "_cpyHook.pyd"))],
    "include_files": [os.path.join(site_packages, "pyHook"), "keyboard-space.ico"]
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    # Executable('key_ferry.py', base=base) # Uncomment as soon as we figure out why the error output ruins the program
    Executable('key_ferry.py', icon='keyboard-space.ico'),
    Executable('python_executor.py', icon='keyboard-space.ico')
]

setup(name='KeyFerry',
      version='0.1',
      description='Automation testing shit show.',
      executables=executables,
      options={"build_exe": build_exe_options},
      )
