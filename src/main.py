# main.py
#
# Copyright 2022 sondalex
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi

# import logging
import os

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw
from .window import ViewMetaWindow, AboutDialog


class ViewMetaApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="io.github.sondalex.MetaDatViewer",
            # important to set HANDLES_COMMAND_LINE
            # flags=Gio.ApplicationFlags.FLAGS_NONE)
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.create_action("quit", self.quit, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.set_accels_for_action("win.open", ["<Ctrl>o"])
        self.dta_file = None

    def do_activate(self, dta_file=None):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win and self.dta_file is None:
            win = ViewMetaWindow(application=self)
        elif not win and self.dta_file is not None:
            win = ViewMetaWindow(application=self, dta_file=self.dta_file)
        win.present()

    def do_command_line(self, command_line):
        # doc: https://python-gtk-3-tutorial.readthedocs.io/en/latest/application.html
        arguments = command_line.get_arguments()

        if len(arguments) > 1:

            if isinstance(arguments[1], str):
                file_path = arguments[1]
                if os.path.exists(file_path) is True:
                    self.dta_file = file_path
        self.activate()
        return 0

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = ViewMetaApplication()
    return app.run(sys.argv)
