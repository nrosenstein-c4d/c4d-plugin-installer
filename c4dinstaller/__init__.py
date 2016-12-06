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

from . import ui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys


class Installer(QWidget, ui.form('installer')):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setupUi(self)


def main():
  app = QApplication(sys.argv)
  wnd = Installer()
  wnd.show()
  return app.exec_()
