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
This directory will contain all the compiled UI files generated with pyuic5.
"""

from PyQt5.QtWidgets import QWidget

def form(name, base_class=QWidget):
  form_class = __import__(__name__ + '.' + name, fromlist=['Ui_Form']).Ui_Form
  class Widget(base_class, form_class):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.setupUi(self)
      self.initForm()
    def initForm(self):
      pass
  Widget.__name__ = name
  return Widget
