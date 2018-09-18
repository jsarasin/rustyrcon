#!/usr/bin/python3

# Cool items:
# ak
# ammo.rifle


import pyrcon
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio

class MainWindow:
    def __init__(self):
        self.traceroute_ping_interfaces = []
        self.new_node = None


        self.connect_builder_objects()

class MainWindow:
    def __init__(self):
        self.connect_builder_objects()

        self.window.show_all()

        self.load_default_connection()


    def load_default_connection(self):
        self.textentry_server_address.set_text("108.61.239.97")
        self.textentry_server_port.set_text("28018")
        self.textentry_password.set_text("1404817")


    def connect_builder_objects(self):
        builder = Gtk.Builder()
        builder.add_from_file("window.glade")

        self.window = builder.get_object("window")
        self.window.connect("delete-event", Gtk.main_quit)

        # Connection Stage 1
        self.stack_connection_stage = builder.get_object("stack_connection_stage")
        self.textentry_server_address = builder.get_object("textentry_server_address")
        self.textentry_server_port = builder.get_object("textentry_server_port")
        self.textentry_password = builder.get_object("textentry_password")
        self.button_connect = builder.get_object("button_connect")
        self.button_connect.connect("clicked", self.event_button_clicked)

        # Connection Stage 2
        # Connection Stage 3
        self.textentry_chat_who = builder.get_object("textentry_chat_who")
        self.buttoncolor_chat = builder.get_object("buttoncolor_chat")
        self.textentry_chat_message = builder.get_object("textentry_chat_message")
        self.button_chat_send = builder.get_object("button_chat_send")
        self.textentry_console = builder.get_object("textentry_console")
        self.button_console_send = builder.get_object("button_console_send")
        self.textview_chat = builder.get_object("textview_chat")
        self.treeview_players = builder.get_object("treeview_players")
        self.textentry_receiving_player = builder.get_object("textentry_receiving_player")
        self.treeview_loadout_item_list = builder.get_object("treeview_loadout_item_list")
        self.button_loadout_add = builder.get_object("button_loadout_add")
        self.button_loadout_remove = builder.get_object("button_loadout_remove")
        self.button_loadout_edit = builder.get_object("button_loadout_edit")

    def event_button_clicked(self, button):
        self.stack_connection_stage.set_visible_child_name("page1")

mw = MainWindow()
Gtk.main()

