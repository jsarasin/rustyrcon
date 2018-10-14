import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject
from betterbuffer import BetterBuffer, scroll_to_textview_bottom


class WindowCommandBrowserItemType:
    COMMAND = 'emblem-system'
    VARIABLE = 'dialog-information'
    CATAGORY = 'folder'


class CommandBrowserModel:
    def __init__(self, command_list, variable_list):
        self.treestore_root_organized = None
        self.treestore_roots = None
        self.root_organized = None


        # Organize the list of commands and variables, it _should_ be in order, but maybe not
        self.root_organized = dict()
        for breakup, description in command_list:
            root, _, command = breakup.partition('.')
            if root not in self.root_organized:
                self.root_organized[root] = []

            self.root_organized[root].append((WindowCommandBrowserItemType.COMMAND, command, description))

        for breakup, description, default_value in variable_list:
            root, _, command = breakup.partition('.')
            if root not in self.root_organized:
                self.root_organized[root] = []

            self.root_organized[root].append((WindowCommandBrowserItemType.VARIABLE, command, description + "\nDefault: " + default_value))

    def get_treestore_root_organized(self):
        # If this model hasn't yet been made, make it
        if self.treestore_root_organized is None:
            self.treestore_root_organized = Gtk.TreeStore(str, str, str)

            for root in sorted(self.root_organized):
                parent = self.treestore_root_organized.append(None, [WindowCommandBrowserItemType.CATAGORY, root, ''])
                for icon_type, command, description in self.root_organized[root]:
                    self.treestore_root_organized.append(parent, [icon_type, command, description])

        return self.treestore_root_organized

    def get_treestore_roots(self):
        if self.treestore_roots is None:
            self.treestore_roots = Gtk.TreeStore(str)
            for root in sorted(self.root_organized):
                self.treestore_roots.append(None, [root])

        return self.treestore_roots

    def get_treestore_root_children(self, root):
        return None


class RustyRCONSharedState:
    command_browser_model = None
    item_browser_model = None
