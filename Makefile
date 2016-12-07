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

default:
	@echo "usage: make <target>"
	@echo " "
	@echo "Available Targets:"
	@echo " "
	@echo " - run          run the installer for testing"
	@echo " - installer    generate an executable installer"
	@echo " - clean"
	@echo "   - clean-qtui"
	@echo "   - clean-installer"

# =======================================
# CONFIG
# =======================================

ifeq ($(OS),Windows_NT)
  PATHSEP :=;
  PYTHON ?= python
  PYTHON_BASEDIR = $(subst \,/,$(shell $(PYTHON) -c "import sys, os; print(os.path.dirname(sys.executable))"))
  PYTHON := $(PYTHON_BASEDIR)/python
  PYUIC5 ?= $(PYTHON_BASEDIR)/Scripts/pyuic5
  PYINSTALLER ?= $(PYTHON_BASEDIR)/Scripts/pyinstaller
else
  PYTHON ?= python3
  PATHSEP :=:
endif

PYUIC5 ?= pyuic5
PYINSTALLER ?= pyinstaller
PYTHONPATH := $(PYTHONPATH)$(PATHSEP)libs
BUILD_DIR = build
QTUI_LIBS = $(patsubst ui/%.ui,c4dinstaller/ui/%.py,$(wildcard ui/*.ui))

c4dinstaller/ui/%.py: ui/%.ui
	$(PYUIC5) $< -o $@

run: $(QTUI_LIBS)
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) "bootstrapper.py"

installer: bootstrapper.py bootstrapper.spec $(QTUI_LIBS)
	PYTHONPATH="$(PYTHONPATH)" $(PYINSTALLER) bootstrapper.spec -y --uac-admin --onefile \
		--workpath "$(BUILD_DIR)/temp" --distpath "$(BUILD_DIR)/dist"

clean-qtui:
	rm -f $(QTUI_LIBS)

clean-installer:
	rm -rf $(BUILD_DIR)

clean: clean-installer clean-qtui
