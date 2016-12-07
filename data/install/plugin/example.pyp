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

import c4d


class Command(c4d.plugins.CommandData):

  def Execute(self, doc):
    c4d.gui.MessageDialog("Hello from the C4DInstaller example plugin!\n\n"
        "Visit https://github.com/nr-plugins/installer for more information")
    return True


if __name__ == '__main__':
  info = 0
  icon = None
  help = "This plugin was installed via the C4DInstaller example"
  c4d.plugins.RegisterCommandPlugin(1038467, "C4DInstaller Example",
    info, icon, help, Command())
