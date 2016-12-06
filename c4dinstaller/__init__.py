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
import string
import sys
import os


class _PageBase(object):

  becomesVisible = pyqtSignal()

  def __init__(self, installer):
    self.installer = installer

  def config(self, name):
    return self.installer.config(name)

  def ls(self, name=None, subst=None):
    return self.installer.ls(name, subst)

  def initButtonBox(self, nextPage=None):
    self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
    self.buttonCancel = self.buttonBox.button(QDialogButtonBox.Cancel)
    self.buttonClose = self.buttonBox.button(QDialogButtonBox.Close)
    self.nextPageName = nextPage

    if self.buttonOk:
      self.buttonOk.setText(self.ls('button.next'))
    if self.buttonOk and nextPage:
      self.buttonOk.clicked.connect(self.nextPage)
    if self.buttonCancel:
      self.buttonCancel.setText(self.ls('button.cancel'))
      self.buttonCancel.clicked.connect(lambda: self.installer.cancel())
    if self.buttonClose:
      self.buttonClose.setText(self.ls('button.close'))
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
    self.label.setText(self.ls('about.label'))
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
    self.label.setText(self.ls('welcome.label'))
    self.initButtonBox('eulaPage')
    self.buttonAbout.clicked.connect(lambda: self.installer.setCurrentPage(self.installer.aboutPage, False))


class EulaPage(_FormPage('page02eula')):

  def initForm(self):
    self.label.setText(self.ls('eula.label'))
    self.initButtonBox('featuresPage')
    self.radioButtonGroup.buttonClicked.connect(self.on_radioButtonClicked)
    self.becomesVisible.connect(self.on_becomesVisible)
    self.on_radioButtonClicked()

  def on_becomesVisible(self):
    filename = 'data/eula.txt'
    if not os.path.isfile(filename):
      self.nextPage()
    else:
      try:
        with open(filename) as fp:
          content = fp.read()
      except Exception as exc:
        content = 'Error: ' + str(exc)
      self.textView.setPlainText(content)

  def on_radioButtonClicked(self):
    agreed = self.radioButtonGroup.checkedButton() == self.radioAgree
    self.buttonOk.setEnabled(agreed)


class FeaturesPage(_FormPage('page03features')):

  class Feature(QListWidgetItem):
    def __init__(self, ident, text, parent=None):
      super().__init__(text)
      self._ident = ident
    def ident(self):
      return self._ident

  def initForm(self):
    self.label.setText(self.ls('features.label'))
    self.initButtonBox('targetPage')
    for ident, name in self.config('features').items():
      is_main_feature = ident.startswith('!')
      if is_main_feature:
        ident = ident[1:]

      flags = Qt.ItemIsUserCheckable
      if not is_main_feature:
        flags |= Qt.ItemIsEnabled

      item = self.Feature(ident, self.ls(subst=name))
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
    self.label.setText(self.ls('target.label'))
    self.labelPath.setText(self.ls('target.path'))
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
    #self.label.setText(self.ls('install.collecting'))
    #self.label.setText(self.ls('install.copying'))
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
      text = self.ls('end.canceled')
    elif self.error:
      text = self.ls('end.failed')
    else:
      text = self.ls('end.success')
    self.label.setText(text)


class Installer(ui.form('installer')):

  def __init__(self, config, strings, parent=None):
    self._config = config
    self._strings = strings
    super().__init__(parent)

  def initForm(self):
    self.setWindowFlags(Qt.Window)
    self.setWindowTitle(self.ls('installer.title'))
    self.bannerLayout.setSpacing(0)
    self.bannerLeft.setPixmap(QPixmap("data/image/banner_01.png"))
    self.bannerMiddle.setPixmap(QPixmap("data/image/banner_02.png"))
    self.bannerRight.setPixmap(QPixmap("data/image/banner_03.png"))
    self.setWindowIcon(QIcon("data/image/icon.ico"))

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

  def ls(self, name=None, subst=None):
    """
    If *name* is specified, it must be a key of a string from the string
    resource.

    Otherwise, *subst* must be specified which can be just a string value
    that will be returned. Also, if *subst* is specified and the key for
    *name* does not exist, *subst* will be used instead.

    Variables in the returned value will be expanded.
    """

    if name is not None:
      try:
        value = self._strings[name]
      except KeyError as exc:
        if subst is None:
          raise
        value = subst
    elif subst is not None:
      value = subst
    else:
      raise ValueError('At least one of "name" and "subst" must be specified')

    template = string.Template(value)
    return template.safe_substitute(**self._strings.get('__vars__'))

  def config(self, name):
    value = self._config
    for part in name.split('.'):
      value = value[part]
    return value

  def cancel(self):
    print("info: called Installer.cancel()")
    self.endPage.canceled = True
    self.setCurrentPage(self.endPage)

  def setCurrentPage(self, page=None, save=True):
    if page is None:
      page = self.currentPage
    if save:
      self.currentPage = page
    print("info: switching to page:", page.objectName())
    self.stackedPages.setCurrentWidget(page)
    page.becomesVisible.emit()


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
  wnd = Installer(read_config(), read_strings())
  wnd.show()
  return app.exec_()
