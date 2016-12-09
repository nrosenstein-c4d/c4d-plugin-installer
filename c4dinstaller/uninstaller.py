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

from .utils import fatal
from .base import FormPage, BaseInstaller
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import sys


class WelcomePage(FormPage('upage00welcome')):

  def initForm(self):
    self.initButtonBox('uninstallPage')
    self.label.setText(self.ls('uninstall.welcome'))


class UninstallPage(FormPage('upage01uninstall')):

  def initForm(self):
    self.initButtonBox()
    dataFile = self.installer.dataFile
    if not dataFile:
      self.label.setText('devnote: Not in a frozen environment, no uninstall file found')
    else:
      self.label.setText(self.ls('uninstall.processing'))
    self.progressBar.setValue(0)
    self.becomesVisible.connect(self.on_becomesVisible)

  def on_becomesVisible(self):
    # TODO: Uninstall logic
    pass


class Uninstaller(BaseInstaller):

    def initForm(self):
      self.dataFile = os.path.basename(sys.argv[0]) + '.data'
      self.dataFile = os.path.join(os.path.dirname(sys.argv[0]), self.dataFile)
      if not os.path.isfile(self.dataFile):
        if sys.frozen:
          fatal('"{}" does not exist'.format(self.dataFile))
        # If we're not in a frozen environment (built with PyInstaller),
        # for testing purposes we still want the uninstaller to run.
        self.dataFile = None

      self.welcomePage = WelcomePage(self)
      self.uninstallPage = UninstallPage(self)

      self.stackedPages.addWidget(self.welcomePage)
      self.stackedPages.addWidget(self.uninstallPage)

      self.setWindowTitle(self.ls('uninstall.title'))
      self.setCurrentPage(self.welcomePage)
      super().initForm()
