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

import collections
import json
import sys


class _PageBase(object):

  def __init__(self, installer):
    self.installer = installer
    self.config = installer.config

  def initButtonBox(self, nextPage=None):
    self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
    self.buttonCancel = self.buttonBox.button(QDialogButtonBox.Cancel)
    self.buttonClose = self.buttonBox.button(QDialogButtonBox.Close)

    if self.buttonOk:
      self.buttonOk.setText("Next")
    if self.buttonOk and nextPage:
      self.buttonOk.clicked.connect(lambda: self.installer.setCurrentPage(getattr(self.installer, nextPage)))
    if self.buttonCancel:
      self.buttonCancel.clicked.connect(lambda: self.installer.cancel())
    if self.buttonClose:
      self.buttonClose.clicked.connect(lambda: self.installer.close())


def _FormPage(form_name):
  form_class = ui.form(form_name)
  class Page(form_class, _PageBase):
    def __init__(self, installer, parent=None):
      _PageBase.__init__(self, installer)
      form_class.__init__(self, parent)
  Page.__name__ = '_FormPage_' + form_name
  return Page



class AboutPage(_FormPage('page00about')):
  pass


class WelcomePage(_FormPage('page01welcome')):

  def initForm(self):
    self.initButtonBox('eulaPage')
    self.label.setText(self.config['text']['title'])


class EulaPage(_FormPage('page02eula')):

  def initForm(self):
    self.initButtonBox('featuresPage')
    self.radioButtonGroup.buttonClicked.connect(self.on_radioButtonClicked)
    self.on_radioButtonClicked()

  def on_radioButtonClicked(self):
    agreed = self.radioButtonGroup.checkedButton() == self.radioAgree
    self.buttonOk.setEnabled(agreed)


class FeaturesPage(_FormPage('page03features')):

  def initForm(self):
    self.initButtonBox('targetPage')
    for feature in self.installer.config['features']:
      is_main_feature = feature.startswith('@')
      if is_main_feature:
        feature = feature[1:]
      enabled = not is_main_feature

      flags = Qt.ItemIsUserCheckable
      if enabled:
        flags |= Qt.ItemIsEnabled

      item = QListWidgetItem(feature)
      item.setFlags(flags)
      item.setCheckState(Qt.Checked if is_main_feature else Qt.Unchecked)
      self.listWidget.addItem(item)


class TargetPage(_FormPage('page04target')):

  def initForm(self):
    self.initButtonBox('installPage')


class InstallPage(_FormPage('page05install')):

  def initForm(self):
    self.initButtonBox('endPage')


class EndPage(_FormPage('page06end')):

  def initForm(self):
    self.initButtonBox()


class Installer(ui.form('installer')):

  def __init__(self, config, parent=None):
    self.config = config
    super().__init__(parent)

  def initForm(self):
    self.setWindowTitle(self.config['text']['title'])

    self.aboutPage = AboutPage(self)
    self.welcomePage = WelcomePage(self)
    self.eulaPage = EulaPage(self)
    self.featuresPage = FeaturesPage(self)
    self.targetPage = TargetPage(self)
    self.installPage = InstallPage(self)
    self.endPage = EndPage(self)

    self.stackedPages.addWidget(self.aboutPage)
    self.stackedPages.addWidget(self.welcomePage)
    self.stackedPages.addWidget(self.eulaPage)
    self.stackedPages.addWidget(self.featuresPage)
    self.stackedPages.addWidget(self.targetPage)
    self.stackedPages.addWidget(self.installPage)
    self.stackedPages.addWidget(self.endPage)

    self.setCurrentPage(self.welcomePage)
    self.aboutButton.clicked.connect(self.on_aboutButtonClicked)

  def setCurrentPage(self, page=None, save=True):
    if page is None:
      page = self.currentPage
    if save:
      self.currentPage = page
    self.stackedPages.setCurrentWidget(page)

  def cancel(self):
    self.endPage.canceled = True
    self.setCurrentPage(self.endPage)

  def on_aboutButtonClicked(self):
    if self.stackedPages.currentWidget() == self.aboutPage:
      self.aboutButton.setText("About")
      self.setCurrentPage()
    else:
      self.aboutButton.setText("Back")
      self.setCurrentPage(self.aboutPage, False)


def read_config():
  with open('config.json') as fp:
    return json.load(fp)


def main():
  app = QApplication(sys.argv)
  wnd = Installer(read_config())
  wnd.show()
  return app.exec_()
