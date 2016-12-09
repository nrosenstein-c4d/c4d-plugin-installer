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

from PyQt5.QtWidgets import QApplication

import collections
import json
import sys
import os

if sys.platform.startswith('win'):
  PLATFORM = 'windows'
  APP_SUFFIX = '.exe'
elif sys.platform.startswith('mac'):
  PLATFORM = 'osx'
  APP_SUFFIX = '.app'
else:
  raise EnvironmentError('unsupported platform: {}'.format(sys.platform))


def read_config():
  # We need to read JSON objects ordered for the "features" section.
  decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
  with open('data/config.json') as fp:
    return decoder.decode(fp.read())


def read_strings(lang_code='en'):
  with open('data/strings/{}.json'.format(lang_code)) as fp:
    return json.load(fp)


def main():
  app = QApplication(sys.argv)
  if os.getenv('UNINSTALLER', '') == 'true':
    from .uninstaller import Uninstaller as wnd_class
  else:
    from .installer import Installer as wnd_class
  wnd = wnd_class(read_config(), read_strings())
  wnd.show()
  return app.exec_()
