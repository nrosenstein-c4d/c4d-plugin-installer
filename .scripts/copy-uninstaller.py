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
This script is run after the uninstaller is built to copy it into the
data/uninstaller directory.
"""

import os
import json
import shutil

with open('data/config.json') as fp:
  config = json.load(fp)

name = config['uninstaller']['name'] + ('.exe' if os.name == 'nt' else '.app')
source = os.path.join('build/dist', name)
dest = os.path.join('data/uninstaller', name)

print("Copying {} to {} ...".format(source, dest))
dirname = os.path.dirname(dest)
if not os.path.isdir(dirname):
  os.makedirs(dirname)
shutil.copyfile(source, dest)
