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

from PyQt5.QtCore import *

import os
import time
import threading
import traceback


class InstallCancelled(Exception):
  pass


class InstallThread(QObject):
  """
  This class implements the installation process. It gathers a list of all
  files to be installed, then starts the installation process. If the
  installation is canceled, it can undo the process.

  :param copyfiles: A list of pairs that represent files to copy from the
    source location (first element) to the second location (second element).
    The elements may also point to directories.

  .. todo:: Support glob patterns

  .. note::

    Connecting to any of the signals of this object must be done using a
    :data:`Qt.QueuedConnection`.

  Signals:

  .. signal:: logUpdate(text)

    Emitted when something has been added to the installation log. Basically
    acts like a ``print()`` function.

  .. signal:: progressUpdate(mode, progress)

    Emitted when the progress changed. *mode* is None unless the mode changed.
    The first time this signal is called, *mode* will be ``'collect'``, then
    when the process is finished, *mode* will be ``'copy'``. If the installer
    has to undo the installed filed, *mode* will be ``'undo'``.
  """

  logUpdate = pyqtSignal(str)
  progressUpdate = pyqtSignal(str, float)

  class Mode:
    Collect = 'collect'
    Copy = 'copy'
    Undo = 'undo'
    Complete = 'complete'
    Cancelled = 'cancelled'
    Error = 'error'

  def __init__(self, copyfiles):
    super().__init__()
    self._copyfiles = copyfiles
    self._running = False
    self._cancelled = False
    self._thread = None
    self._lock = threading.Lock()
    self._mode = None
    self._installedFiles = None

  def _log(self, *objects, sep=' ', end='\n'):
    message = sep.join(map(str, objects)) + end
    print('] installer:', message, end='')
    self.logUpdate.emit(message)

  def _updateProgress(self, mode, progress):
    if mode == self._mode:
      mode = None
    if mode is not None:
      self._mode = mode
    self.progressUpdate.emit(mode, progress)

  def _run(self):
    Mode = self.Mode
    filelist = []
    installedFiles = self._installedFiles = []

    try:
      # Generate a list of all source and target files.
      self._log('Collecting file list ...')
      for i, (from_, to) in enumerate(self._copyfiles):
        self.raiseCancelled()
        self._updateProgress(Mode.Collect, i / len(self._copyfiles))
        filelist += get_filelist(from_, to)
      self._updateProgress(Mode.Collect, 1.0)

      # Copy the source files to their target location.
      self._log('Copying {} files ...'.format(len(filelist)))
      for i, (from_, to) in enumerate(filelist):
        self.raiseCancelled()
        self._updateProgress(Mode.Copy, i / len(filelist))
        # TODO: Actually copy the file
        self._log('Installed file: {}'.format(to))
      self._updateProgress(Mode.Copy, 1.0)

      self._log('Installation successful!')
    except Exception as exc:
      traceback.print_exc()
      self.running = False

      if isinstance(exc, InstallCancelled):
        self._log("User cancelled installation.")
      elif isinstance(exc, FileNotFoundError):
        self._log('Error: file could not be found:', exc)
      else:
        self._log('Error:', exc)

      # Try to undo all installed files.
      self._log('Removing already installed files ...')
      for i, filename in enumerate(installedFiles):
        self._updateProgress(Mode.Undo, 1.0 - i / len(installedFiles))
        try:
          os.remove(filename)
        except OSError as exc:
          self._log('Error: Could not remove file: {}'.format(filename))
        else:
          self._log('Removed file: {}'.format(filename))

      self._updateProgress(Mode.Cancelled if self.cancelled() else Mode.Error, 1.0)
    else:
      self._updateProgress(Mode.Complete, 1.0)
    print("note: Installer thread ended")

  def cancel(self, join=True):
    with self._lock:
      self._canceled = True
      self._running = False
    if join:
      self._thread.join()

  def cancelled(self):
    with self._lock:
      return self._cancelled

  def raiseCancelled(self):
    if self.cancelled():
      raise InstallCancelled()

  def start(self):
    with self._lock:
      if self._running:
        raise RuntimeError("already running")
    if self._thread:
      raise RuntimeError("can not be restarted")
    self._running = True
    self._thread = threading.Thread(target=self._run)
    self._thread.start()
    print("note: Installer thread started")

  def installedFiles(self):
    " Only access while installer is NOT running. "
    return self._installedFiles


def get_filelist(from_, to):
  """
  Given two paths *from_* and *to*, returns a generator that yields absolute
  source and target filenames. If *from_* is a directory, *to* will also be
  assumed to be a directory.

  :raise FileNotFoundError: If *from_* or *to* are not absolute paths.

  .. todo:: Support glob patterns
  """

  if not os.path.isabs(from_):
    raise FileNotFoundError(from_)
  if not os.path.isabs(to):
    raise FileNotFoundError(to)

  if os.path.isfile(from_):
    yield (from_, to)
    return
  elif os.path.isdir(from_):
    for filename in os.listdir(from_):
      yield from get_filelist(os.path.join(from_, filename), os.path.join(to, filename))
  else:
    raise FileNotFoundError(from_)
