# window.py
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

from gi.repository import Gtk, Gio

# GObject
import pyreadstat
import datetime

import numpy as np
import pandas as pd

# import logging


# need to be bytes.
CSS = b"""
        #SummaryStatisticsLabel {
        font-size: large;
        }
        """


def convert_pandas(data_frame: pd.DataFrame):
    """Convert pandas to python native for compatibility with Gtk"""
    columns = data_frame.columns
    # detect NaN columns
    for col in columns:
        condition = data_frame[col].isna().any()
        if condition == True:
            data_frame[col] = data_frame[col].replace({np.nan, "NaN"})
            # logging.warning("REPLACED")
            data_frame[col] = data_frame[col].astype(str)
        data_frame[col] = data_frame[col].astype("object")
        if (
            isinstance(
                data_frame.iloc[0, data_frame.columns.get_loc(col)],
                (datetime.datetime, datetime.date, datetime.time),
            )
            is True
        ):
            # conversion for compatibility with Gtk Types.
            data_frame[col] = data_frame[col].astype(str)
    return data_frame


@Gtk.Template(resource_path="/io/github/sondalex/MetaDatViewer/window.ui")
class ViewMetaWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "ViewMetaWindow"
    # the var is the id in xml.

    dta_labels = Gtk.Template.Child()
    open_button = Gtk.Template.Child()
    main_text_view = Gtk.Template.Child()

    def __init__(self, dta_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.box)

        open_action = Gio.SimpleAction(name="open")
        open_action.connect("activate", self.open_file_dialog)
        self.add_action(open_action)

        self.scrollable_treelist = None

        if dta_file is not None:
            self.read_dta(dta_file)

    def read_dta(self, filepath):
        self.table = Gtk.ListStore(str, str)
        if self.scrollable_treelist is not None:

            self.box.remove(self.box.get_last_child())
            self.box.remove(self.box.get_last_child())

        df, dta_metadata = pyreadstat.read_dta(
            filepath, metadataonly=False, row_offset=0, row_limit=10
        )
        column_labels = dta_metadata.column_names_to_labels
        number_rows = dta_metadata.number_rows
        number_columns = dta_metadata.number_columns

        variable_info = list(column_labels.items())

        column_labels_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        column_labels_box.set_spacing(10)

        column_labels_label = Gtk.Label()
        column_labels_label.set_markup("<b>Column-Labels</b>")
        column_labels_box.append(column_labels_label)

        df_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        df_box.set_spacing(10)
        df_label = Gtk.Label()
        df_label.set_markup("<b> Data Preview (First 10 rows). </b>")
        df_box.append(df_label)

        df = convert_pandas(df)

        python_types = [int] + [
            type(df.iloc[0, df.columns.get_loc(col)]) for col in df.columns
        ]
        # logging.warning(python_types)
        df_table = Gtk.ListStore(*python_types)
        for row in df.itertuples():
            df_table.append(tuple(row))

        df_treeview = Gtk.TreeView.new_with_model(df_table)

        for i, column in enumerate(["index"] + df.columns.tolist()):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column, renderer, text=i)
            df_treeview.append_column(column)

        for tuple_ in variable_info:
            self.table.append(list(tuple_))

        self.treeview = Gtk.TreeView.new_with_model(self.table)
        for i, column_title in enumerate(["Column", "Label"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)

        summary_stat = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        summary_stat.set_spacing(10)
        summary_stat_label = Gtk.Label(name="SummaryStatisticsLabel")
        summary_stat_label.set_markup("<b>Summary Statistics</b>")
        summary_stat_table = Gtk.ListStore(int, int)
        summary_stat_table.append((number_columns, number_rows))
        summary_stat_treeview = Gtk.TreeView.new_with_model(summary_stat_table)

        for i, column_title in enumerate(["Number of columns", "Number of rows"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            summary_stat_treeview.append_column(column)

        summary_stat.append(summary_stat_label)
        summary_stat.append(summary_stat_treeview)

        self.scrollable_treelist.set_child(self.treeview)
        column_labels_box.append(self.scrollable_treelist)

        df_scrollable = Gtk.ScrolledWindow()
        df_scrollable.set_vexpand(True)
        df_scrollable.set_child(df_treeview)
        df_box.append(df_scrollable)

        self.box.append(summary_stat)
        self.box.append(column_labels_box)
        self.box.append(df_box)

    def open_file_dialog(self, action, _):
        self._native = Gtk.FileChooserNative(
            title="Open File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        filter_ = Gtk.FileFilter()
        filter_.set_name("Stata File")
        # add_pattern doesn't work when add_mime_type is used.
        # filter_.add_mime_type("application/octet-stream")
        filter_.add_pattern("*.dta")

        self._native.add_filter(filter_)

        self._native.connect("response", self.on_open_response)
        self._native.show()

    def on_open_response(self, dialog, response):

        if response == Gtk.ResponseType.ACCEPT:

            file_path = dialog.get_file().get_path()

            self.read_dta(file_path)

        elif response == Gtk.ResponseType.CANCEL:
            # logging.warning("Cancel clicked")
            pass
        else:
            # logging.warning("Not OK")
            pass
        self._native = None


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = "metadatviewer"
        self.props.version = "0.1.0"
        self.props.authors = ["sondalex"]
        self.props.copyright = "2022 sondalex"
        self.props.logo_icon_name = "MetaDatViewer"
        self.props.modal = True
        self.set_transient_for(parent)
