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
from .utils import c4dfinder
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import collections
import json
import sys
import os


class _PageBase(object):

  becomesVisible = pyqtSignal()

  def __init__(self, installer):
    self.installer = installer

  def config(self, name):
    return self.installer.config(name)

  def initButtonBox(self, nextPage=None):
    self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
    self.buttonCancel = self.buttonBox.button(QDialogButtonBox.Cancel)
    self.buttonClose = self.buttonBox.button(QDialogButtonBox.Close)
    self.nextPageName = nextPage

    if self.buttonOk:
      self.buttonOk.setText("Next")
    if self.buttonOk and nextPage:
      self.buttonOk.clicked.connect(self.nextPage)
    if self.buttonCancel:
      self.buttonCancel.clicked.connect(lambda: self.installer.cancel())
    if self.buttonClose:
      self.buttonClose.clicked.connect(lambda: self.installer.close())

  def nextPage(self):
    if self.nextPageName:
      page = getattr(self.installer, self.nextPageName)
      self.installer.setCurrentPage(page)


def _FormPage(form_name):
  form_class = ui.form(form_name)
  class Page(form_class, _PageBase):
    def __init__(self, installer, parent=None):
      _PageBase.__init__(self, installer)
      form_class.__init__(self, parent)
  Page.__name__ = '_FormPage_' + form_name
  return Page


class AboutPage(_FormPage('page00about')):

  def initForm(self):
    self.label.setText(self.config('text.pages.about'))
    self.textView.setWordWrapMode(QTextOption.NoWrap)
    self.buttonBack.clicked.connect(lambda: self.installer.setCurrentPage())
    self.becomesVisible.connect(self.on_becomesVisible)

  def on_becomesVisible(self):
    if not self.textView.toPlainText():
      try:
        with open('data/about.txt') as fp:
          content = fp.read()
      except Exception as exc:
        content = 'Error: ' + str(exc)
      self.textView.setPlainText(content)


class WelcomePage(_FormPage('page01welcome')):

  def initForm(self):
    self.label.setText(self.config('text.pages.welcome'))
    self.initButtonBox('eulaPage')
    self.buttonAbout.clicked.connect(lambda: self.installer.setCurrentPage(self.installer.aboutPage, False))


class EulaPage(_FormPage('page02eula')):

  def initForm(self):
    self.label.setText(self.config('text.pages.eula'))
    self.initButtonBox('featuresPage')
    self.radioButtonGroup.buttonClicked.connect(self.on_radioButtonClicked)
    self.on_radioButtonClicked()

  def on_radioButtonClicked(self):
    agreed = self.radioButtonGroup.checkedButton() == self.radioAgree
    self.buttonOk.setEnabled(agreed)


class FeaturesPage(_FormPage('page03features')):

  def initForm(self):
    self.label.setText(self.config('text.pages.features'))
    self.initButtonBox('targetPage')
    for feature in self.config('features'):
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

    self.becomesVisible.connect(self.on_becomesVisible)

  def on_becomesVisible(self):
    if not self.config('features'):
      self.nextPage()


class TargetPage(_FormPage('page04target')):

  class C4DInstallation(QListWidgetItem):
    def __init__(self, name, path, parent=None):
      super().__init__(name, parent)
      self._path = path
    def installPath(self):
      return self._path

  def initForm(self):
    self.label.setText(self.config('text.pages.target'))
    self.initButtonBox('installPage')
    for name, path in c4dfinder.find_installations():
      item = self.C4DInstallation(name, path)
      self.listWidget.addItem(item)
      if not self.listWidget.currentItem():
        self.listWidget.setCurrentItem(item)
    self.listWidget.itemClicked.connect(self.on_itemClicked)
    self.buttonChoosePath.clicked.connect(self.on_choosePath)
    self.targetPath.textChanged.connect(self.on_targetPathChanged)
    self.on_itemClicked()

  def on_targetPathChanged(self):
    self.buttonOk.setEnabled(os.path.isdir(self.targetPath.text()))

  def on_itemClicked(self):
    item = self.listWidget.currentItem()
    if item:
      self.targetPath.setText(item.installPath())

  def on_choosePath(self):
    path = QFileDialog.getExistingDirectory(self, directory=self.targetPath.text())
    if path:
      self.targetPath.setText(path)


class InstallPage(_FormPage('page05install')):

  def initForm(self):
    self.initButtonBox('endPage')
    sp = self.textView.sizePolicy()
    sp.setRetainSizeWhenHidden(True)
    self.textView.setSizePolicy(sp)
    self.buttonDetails.clicked.connect(self.on_detailsClicked)
    self.becomesVisible.connect(self.on_becomesVisible)

  def on_detailsClicked(self):
    self.textView.setVisible(not self.textView.isVisible())

  def on_becomesVisible(self):
    #self.label.setText(self.config('text.pages.install.collecting'))
    #self.label.setText(self.config('text.pages.install.copying'))
    # TODO: start the installation process
    pass


class EndPage(_FormPage('page06end')):

  def initForm(self):
    self.canceled = False
    self.error = None
    self.initButtonBox()
    self.becomesVisible.connect(self.on_becomesVisible)

  def on_becomesVisible(self):
    if self.canceled:
      text = self.config('text.pages.end.canceled')
    elif self.error:
      text = self.config('text.pages.end.failed')
    else:
      text = self.config('text.pages.end.success')
    self.label.setText(text)


class Installer(ui.form('installer')):

  def __init__(self, config, parent=None):
    self._config = config
    super().__init__(parent)

  def initForm(self):
    self.setWindowFlags(Qt.Window)
    self.setWindowTitle(self.config('text.title'))
    self.bannerLayout.setSpacing(0)
    self.bannerLeft.setPixmap(QPixmap(self.config('installer.banner.left')))
    self.bannerMiddle.setPixmap(QPixmap(self.config('installer.banner.fill')))
    self.bannerRight.setPixmap(QPixmap(self.config('installer.banner.right')))
    self.setWindowIcon(QIcon(self.config('installer.icon')))

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

  def config(self, name):
    value = self._config
    for part in name.split('.'):
      value = value[part]
    return value

  def cancel(self):
    self.endPage.canceled = True
    self.setCurrentPage(self.endPage)

  def setCurrentPage(self, page=None, save=True):
    if page is None:
      page = self.currentPage
    if save:
      self.currentPage = page
    self.stackedPages.setCurrentWidget(page)
    page.becomesVisible.emit()


def read_config():
  with open('config.json') as fp:
    return json.load(fp)


def main():
  app = QApplication(sys.argv)
  wnd = Installer(read_config())
  wnd.show()
  return app.exec_()
