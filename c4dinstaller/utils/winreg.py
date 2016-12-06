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
Utilities to read from the Windows Registry.
"""

import collections
import contextlib
import winreg

Key = collections.namedtuple('winreg_key', 'name value type')

@contextlib.contextmanager
def open(key):
  key, sub_key = key.replace('/', '\\').split('\\', 1)
  key = getattr(winreg, key)
  handle = winreg.OpenKey(key, sub_key)
  try:
    yield handle
  finally:
    handle.Close()

def get(key, value_name=''):
  if value_name == '(Default)':
    value_name = ''
  with open(key) as handle:
    return Key(value_name or '(Default)', *winreg.QueryValueEx(handle, value_name))

def enum(key):
  with open(key) as handle:
    index = 0
    while True:
      try:
        yield Key(*winreg.EnumValue(handle, index))
        index += 1
      except WindowsError:
        break
