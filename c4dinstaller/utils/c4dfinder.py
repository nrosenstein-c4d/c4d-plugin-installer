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
"""
Find Cinema 4D installations on Windows and Mac OS.
"""

import os
import pipes
import shlex
import subprocess
import re

if os.name == 'nt':
  from . import winreg

C4D_PATTERN = r'cinema\s*4d\s*r(\d{2})([^\\/]*)'


def __find_installations_windows():
  paths = []
  try:
    value = shlex.split(winreg.get('HKEY_CURRENT_USER\\SOFTWARE\\Classes\\CINEMA 4D Document\\shell\\open\\command').value)
  except WindowsError as exc:
    pass
  else:
    if value and value[0].lower().endswith('cinema 4d.exe'):
      value = os.path.dirname(value[0])
      if value not in paths and os.path.isdir(value):
        paths.append(value)
  try:
    for value in winreg.enum('HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store'):
      if value.name.lower().endswith('cinema 4d.exe'):
        dirname = os.path.dirname(value.name)
        if dirname not in paths and os.path.isdir(dirname):
          paths.append(dirname)
  except WindowsError as exc:
    pass

  versions = []
  for path in paths:
    match = re.search(C4D_PATTERN, path, re.I)
    if match:
      name = 'Cinema 4D R' + match.group(1) + match.group(2)
      versions.append((name, path))
    else:
      versions.append(('Cinema 4D ({})'.format(path), path))

  return versions


def __find_installations_mac():
  # Currently our only method is looking for common installation paths.
  result = []
  paths = ['/Applications', '/Applications/MAXON', '~/Applications', '~/Applications/MAXON']
  for path in paths:
    path = os.path.expanduser(path)
    if not os.path.isdir(path): continue
    for item in os.listdir(path):
      match = re.match(C4D_PATTERN, item, re.I)
      if match and os.path.exists(os.path.join(path, item, 'CINEMA 4D.app')):
        result.append((item, os.path.join(path, item)))

  return result


def find_installations():
  if os.name == 'nt':
    return __find_installations_windows()
  else:
    return __find_installations_mac()


if __name__ == '__main__':
  print("Searching for Cinema 4D installations ...")
  for name, path in find_installations():
    print('{}: {}'.format(name, path))
