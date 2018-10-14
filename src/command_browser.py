import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject
from betterbuffer import BetterBuffer, scroll_to_textview_bottom

from shared import CommandBrowserModel, WindowCommandBrowserItemType
from shared import RustyRCONSharedState


class WindowCommandBrowser:
    def __init__(self):
        self.activate_callback = None
        self.connect_builder_objects()
        self.selected_command = None


        # Show the TreeStore
        self.treeview_commands.set_model(RustyRCONSharedState.command_browser_model.get_treestore_root_organized())

    def connect_builder_objects(self):
        builder = Gtk.Builder()
        builder.add_from_file("command_browser.glade")

        self.window = builder.get_object('window')
        self.window.connect("delete-event", self.event_window_close)
        self.treeview_favourites = builder.get_object('treeview_favourites')

        self.treeview_commands = builder.get_object('treeview_commands')
        self.treeview_commands.connect('row-activated', self.event_treeview_command_row_activated)
        self.treeview_commands.connect('cursor-changed', self.event_treeview_cursor_changed)

        # Empty Column for expander
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("", renderer_text)
        column_text.set_fixed_width(20)
        self.treeview_commands.append_column(column_text)

        renderer_text = Gtk.CellRendererPixbuf()
        column_text = Gtk.TreeViewColumn("Type", renderer_text, icon_name=0)
        column_text.set_fixed_width(20)
        # column_text.set_visible(False)
        self.treeview_commands.append_column(column_text)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Name", renderer_text, text=1)
        self.treeview_commands.append_column(column_text)

        column_text = Gtk.TreeViewColumn("Description", renderer_text, text=2)
        column_text.set_visible(False)
        self.treeview_commands.append_column(column_text)

        self.textview_description = builder.get_object('textview_description')
        self.textbuffer_description = Gtk.TextBuffer()
        self.textbuffer_description.create_tag('command', foreground='lightgreen', paragraph_background='black', weight=Pango.Weight.BOLD)
        self.textbuffer_description.create_tag('description', style=Pango.Style.ITALIC, left_margin=10)
        self.textview_description.set_buffer(self.textbuffer_description)

        self.checkbutton_insertclose_activate = builder.get_object('checkbutton_insertclose_activate')
        self.searchentry_command = builder.get_object('searchentry_command')
        self.searchentry_command.connect('search-changed', self.event_search_changed)

    def event_window_close(self, window, event):
        self.window.hide()
        return True

    def event_treeview_cursor_changed(self, treeview):
        self.textbuffer_description.set_text('')
        model, iter = treeview.get_selection().get_selected()
        if iter is None:
            return

        parent_iter = model.iter_parent(iter)

        if parent_iter is None:
            return

        item_type = model[iter][0]
        command = model[parent_iter][1] + '.' + model[iter][1]
        description = model[iter][2]

        self.selected_command = command
        end_iter = self.textbuffer_description.get_end_iter()
        self.textbuffer_description.insert_with_tags_by_name(end_iter, command + "\n", 'command')
        end_iter = self.textbuffer_description.get_end_iter()
        self.textbuffer_description.insert_with_tags_by_name(end_iter, description, 'description')

    def event_search_changed(self, searchentry):
        pass

    def event_treeview_command_row_activated(self, treeview, path, column):
        if path.get_depth() == 1:
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, True)
            return False

        if self.checkbutton_insertclose_activate.get_active():
            self.window.hide()

        if self.activate_callback is not None:
            self.activate_callback(self.selected_command)


if __name__ == '__main__':
    print("Command Browser directly executed for testing purposes")
    settings = Gtk.Settings.get_default()
    settings.props.gtk_application_prefer_dark_theme = True

    wib = WindowCommandBrowser()
    Gtk.main()
