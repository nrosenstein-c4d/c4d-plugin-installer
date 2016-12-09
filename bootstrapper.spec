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

import os
import sys
import json
import fnmatch

def recursive_data_files(path, target_dir, exclude=()):
  result = []
  path = os.path.abspath(path)
  for root, dirs, files in os.walk(path):
    arcdir = os.path.relpath(root, path)
    if arcdir == '.':
      arcdir = target_dir
    else:
      arcdir = os.path.join(target_dir, arcdir)
    if any(fnmatch.fnmatch(arcdir, p) for p in exclude):
      continue
    for filename in files:
      result.append((os.path.join(root, filename), arcdir))
  return result

is_mac = sys.platform.startswith('darwin')
is_installer = os.getenv('UNINSTALLER', '') != 'true'

with open('data/config.json') as fp:
  config = json.load(fp)['installer' if is_installer else 'uninstaller']
  del fp

print('-'*80)
if is_installer:
  print('Building Installer ...')
else:
  print('Building Uninstaller ...')
print('-'*80)

installer_icon = "data/image/icon.ico" if not is_mac else "data/image/icon.icns"
block_cipher = None

datas = recursive_data_files('data', 'data', exclude = [] if is_installer else ['data/install/*'])

a = Analysis(['bootstrapper.py'],
  pathex = [os.getcwd()],
  binaries = None,
  datas = datas,
  hiddenimports = ['c4dinstaller.ui.' + x[:-3] for x in os.listdir('c4dinstaller/ui')],
  hookspath = [],
  runtime_hooks = [] if is_installer else ['uninstaller-hook.py'],
  excludes = [],
  win_no_prefer_redirects = False,
  win_private_assemblies = False,
  cipher = block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher = block_cipher)

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
  name = config['name'],
  debug = False,
  strip = False,
  upx = False,
  console = True,
  uac_admin = True,
  icon = installer_icon)

if is_mac:
  app = BUNDLE(exe,
    name = config['name'] + '.app',
    icon = installer_icon,
    bundle_identifier = config['bundle_identifier'],
    upx = False)
