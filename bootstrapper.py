# C4D Installer
# Copyright (C) 2016  Niklas Rosenstein
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import os
import subprocess
import sys
import traceback

try:
  from PyQt5.QtWidgets import QApplication, QMessageBox
except ImportError:
  QApplication = QMessageBox = None

def fatal(message):
  if QMessageBox:
    try:
      app = QApplication(sys.argv)
      QMessageBox.critical(None, 'Error', str(message))
    except BaseException as exc:
      print('fatal:', message)
      print('during handling of the above error, following error occured')
      print('fatal:', exc)
  else:
    print('fatal:', message)
  sys.exit(1)

if sys.version < '3.3':
  fatal('Python Version must be >= 3.3, have {}'.format(sys.version[:3]))

# Change to the directory that contains the unpacked resource files if
# available. _MEIPASS is set by the PyInstaller bootstrapper.
if hasattr(sys, '_MEIPASS'):
  print('note: changing to _MEI directory:', sys._MEIPASS)
  os.chdir(sys._MEIPASS)
elif getattr(sys, 'frozen', False):
  fatal('frozen environment has no sys._MEIPASS')


def is_admin():
  try:
    return os.getuid() == 0
  except AttributeError:
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def main():
  try:
    if not is_admin():
      if sys.platform.startswith('darwin'):
        print('note: no admin privileges, using osascript ...')
        cmd = [
          '/usr/bin/osascript', '-e',
          'do shell script "{} {} 2>&1" with administrator privileges'
            .format(sys.executable, sys.argv[0])
          ]
        return subprocess.call(cmd)
      elif sys.platform.startswith('win'):
        print('note: no admin privileges, not sure what to do on windows!')
        raise NotImplementedError('Admin switch not implemented on Windows')

    import c4dinstaller
    res = c4dinstaller.main()
  except Exception as exc:
    traceback.print_exc()
    fatal(traceback.format_exc())
    raise
  else:
    sys.exit(res)

if __name__ == '__main__':
  main()
