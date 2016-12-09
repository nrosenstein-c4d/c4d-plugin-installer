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
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import string


class PageBase(object):

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


def FormPage(form_name):
  form_class = ui.form(form_name)
  class Page(form_class, PageBase):
    def __init__(self, installer, parent=None):
      PageBase.__init__(self, installer)
      form_class.__init__(self, parent)
  Page.__name__ = '_FormPage_' + form_name
  return Page


class BaseInstaller(ui.form('installer')):

  def __init__(self, config, strings, parent=None):
    self._config = config
    self._strings = strings
    self.currentPage = None
    super().__init__(parent)

  def initForm(self):
    self.setWindowFlags(Qt.Window)
    self.bannerLayout.setSpacing(0)
    self.bannerLeft.setPixmap(QPixmap("data/image/banner_01.png"))
    self.bannerMiddle.setPixmap(QPixmap("data/image/banner_02.png"))
    self.bannerRight.setPixmap(QPixmap("data/image/banner_03.png"))
    self.setWindowIcon(QIcon("data/image/icon.ico"))
    self.initStyle()

  def initStyle(self):
    def rgb(color): return "rgb(" + ",".join(map(str, color)) + ")"
    buttonStyle = ""
    lineEditStyle = ""
    palette = self.palette()

    color = self.config('palette.background')
    palette.setColor(QPalette.Window, QColor(*color))
    palette.setColor(QPalette.Base, QColor(*color))
    palette.setColor(QPalette.AlternateBase, QColor(*color))

    color = self.config('palette.alternate_background')
    palette.setColor(QPalette.Base, QColor(*color))

    color = self.config('palette.foreground')
    palette.setColor(QPalette.Text, QColor(*color))
    palette.setColor(QPalette.ButtonText, QColor(*color))
    palette.setColor(QPalette.WindowText, QColor(*color))

    bg = rgb(self.config('palette.button_background'))
    fg = rgb(self.config('palette.button_foreground'))
    buttonStyle += "QPushButton { background:%s; color: %s} " % (bg, fg)
    lineEditStyle += "QLineEdit{border: 1px solid gray; background-color: %s;} "\
        "QLineEdit:hover{border: 1px solid gray; background-color: %s;}" % (bg, bg)

    bg = rgb(self.config('palette.button_disabled_background'))
    fg = rgb(self.config('palette.button_disabled_foreground'))
    buttonStyle += 'QPushButton:disabled { background: %s; color: %s }\n' % (bg, fg)

    def applyStyle(widget):
      if isinstance(widget, (QPushButton, QToolButton)):
        widget.setStyleSheet(buttonStyle)
      elif isinstance(widget, QLineEdit):
        widget.setStyleSheet(lineEditStyle)
        widget.setAutoFillBackground(True)
        widget.setPalette(palette)
      for child in widget.findChildren(QWidget):
        applyStyle(child)

    self.setPalette(palette)
    applyStyle(self)

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

  def config(self, name, default=NotImplemented):
    try:
      value = self._config
      for part in name.split('.'):
        value = value[part]
    except KeyError:
      if default is NotImplemented:
        raise
      value = default
    return value

  def setCurrentPage(self, page=None, save=True):
    if page is None:
      page = self.currentPage
    if save:
      self.currentPage = page
    assert isinstance(page, PageBase)
    print("info: switching to page:", page.objectName())
    self.stackedPages.setCurrentWidget(page)
    page.becomesVisible.emit()
