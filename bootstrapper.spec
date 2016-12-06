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

installer_name = 'C4DInstaller'
block_cipher = None

a = Analysis(['bootstrapper.py'],
  pathex = [os.getcwd()],
  binaries = None,
  datas = [],
  hiddenimports = [],
  hookspath = [],
  runtime_hooks = [],
  excludes = [],
  win_no_prefer_redirects = False,
  win_private_assemblies = False,
  cipher = block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher = block_cipher)

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
  name = installer_name,
  debug = False,
  strip = False,
  upx = False,
  console = True,
  uac_admin = True,
  icon = None)

if sys.platform.startswith('darwin'):
  app = BUNDLE(exe,
    name = installer_name + '.app',
    icon = None,
    bundle_identifier = 'com.laublab.vraybridge.installer',
    upx = False)
