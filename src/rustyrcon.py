#!/usr/bin/python3

# Cool items:
# ak
# ammo.rifle

import time
import json
import sys
from pyrcon import PyRCON
from utilities import unity_to_pango, gtkcolor_to_web

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject
from betterbuffer import BetterBuffer

class BufferManager:
    def __init__(self, buffer):
        self.buffer = buffer

class Autocomplete:
    def __init__(self):
        pass




class MainWindow:
    def __init__(self):
        # Program initialization
        self.autocomplete = None
        self.pyrcon = None
        self.unique_identifier = 5

        # Program data
        self.entity_list = None

        # Chat message globals
        self.first_chat_message = True
        self.last_chat_mark = None

        # Console globals
        self.first_console_message = True
        self.last_console_entry_color = 0
        self.last_console_mark = None

        # Shared Models
        self.liststore_players = Gtk.ListStore(str)# GObject.GType([str]) #TYPE_PYOBJECT
        self.entrycompletion_liststore = Gtk.ListStore(str,)# GObject.GType([str]) #TYPE_PYOBJECT

        # GUI initialization
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
        self.window.connect("delete-event", self.event_shutdown)
        self.stack_rcon = builder.get_object('stack_rcon')
        self.stack_rcon.connect('notify::visible-child', self.event_stack_rcon_switched)
        self.button_disconnect = builder.get_object('button_disconnect')
        self.button_disconnect.connect('clicked', self.event_button_disconnect_clicked)

        # Connection Stage 1
        self.stack_connection_stage = builder.get_object("stack_connection_stage")
        self.textentry_server_address = builder.get_object("textentry_server_address")
        self.textentry_server_port = builder.get_object("textentry_server_port")
        self.textentry_password = builder.get_object("textentry_password")
        self.button_connect = builder.get_object("button_connect")
        self.button_connect.connect("clicked", self.event_connect_clicked)

        # Connection Stage 2
        # Connection Stage 3
        # Chat
        self.textentry_chat_who = builder.get_object("textentry_chat_who")
        self.buttoncolor_chat = builder.get_object("buttoncolor_chat")
        self.textentry_chat_message = builder.get_object("textentry_chat_message")
        self.textentry_chat_message.connect('activate', self.send_chat_message)
        self.button_italic = builder.get_object("button_italic")
        self.scalebutton_text_size = builder.get_object("scalebutton_text_size")
        self.button_chat_send = builder.get_object("button_chat_send")
        self.button_chat_send.connect("clicked", self.send_chat_message)
        self.textview_chat = builder.get_object("textview_chat")
        self.textbuffer_chat = BetterBuffer()
        self.textbuffer_chat.create_tag("peasant_chat", paragraph_background="lightgreen", wrap_mode=Gtk.WrapMode.WORD_CHAR, foreground='Black')
        self.textbuffer_chat.create_tag("peasant_uname", weight=Pango.Weight.BOLD, foreground='Black')
        self.textbuffer_chat.create_tag("server_chat", paragraph_background="lightblue", wrap_mode=Gtk.WrapMode.WORD_CHAR, foreground='Black')
        self.textbuffer_chat.create_tag("server_uname", weight=Pango.Weight.BOLD, foreground='Black' )
        self.textview_chat.set_buffer(self.textbuffer_chat)
        self.buffermanager_chat = BufferManager(self.textbuffer_chat)


        # Console
        self.textentry_console = builder.get_object("textentry_console")
        self.textentry_console.connect('activate', self.event_button_send_console)
        self.button_console_send = builder.get_object("button_console_send")
        self.button_console_send.connect('clicked', self.event_button_send_console)

        self.textview_console = builder.get_object("textview_console")
        self.textbuffer_console = BetterBuffer()
        self.textbuffer_console.create_tag("e1", paragraph_background="lightgrey", foreground='Black')
        self.textbuffer_console.create_tag("e2", paragraph_background="darkgrey", foreground='White')
        self.textbuffer_console.create_tag("console_command", paragraph_background="black", foreground='lightgreen', weight=Pango.Weight.BOLD)
        self.textview_console.set_buffer(self.textbuffer_console)


        self.treeview_players = builder.get_object("treeview_players")
        self.entrycompletion_console = builder.get_object("entrycompletion_console")
        self.entrycompletion_console.set_model(self.entrycompletion_liststore)
        self.entrycompletion_console.set_text_column(0)

        # Players
        self.treeview_players = builder.get_object('treeview_players')
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Display Name", renderer_text, text=0)
        self.treeview_players.append_column(column_text)
        column_text = Gtk.TreeViewColumn("Steam ID", renderer_text, text=1)
        self.treeview_players.append_column(column_text)
        column_text = Gtk.TreeViewColumn("Ping", renderer_text, text=2)
        self.treeview_players.append_column(column_text)
        column_text = Gtk.TreeViewColumn("Address", renderer_text, text=3)
        self.treeview_players.append_column(column_text)
        column_text = Gtk.TreeViewColumn("Health", renderer_text, text=4)
        self.treeview_players.append_column(column_text)

        self.treestore_players = Gtk.TreeStore(str, str, int, str, float)
        self.treeview_players.set_model(self.treestore_players)



        # Loadout Gift
        self.textentry_receiving_player = builder.get_object("textentry_receiving_player")
        self.treeview_loadout_item_list = builder.get_object("treeview_loadout_item_list")
        self.button_loadout_add = builder.get_object("button_loadout_add")
        self.button_loadout_remove = builder.get_object("button_loadout_remove")
        self.button_loadout_edit = builder.get_object("button_loadout_edit")

        self.search_loadout_gift_players = builder.get_object("search_loadout_gift_players")
        self.entrycompletion_players = builder.get_object("entrycompletion_players")
        self.entrycompletion_players.set_model(self.liststore_players)
        self.entrycompletion_players.set_text_column(0)

        self.load_entity_types()

    def load_entity_types(self):
        fp = open("../rust_entities.json", 'r')
        self.entity_list = json.load(fp)
        fp.close()

    ####################
    ## Event handlers ##
    ####################
    def event_button_disconnect_clicked(self, button):
        self.disconnect()

    def event_stack_rcon_switched(self, event, cat):
        child_name = self.stack_rcon.get_visible_child_name()

        if child_name == "players" or child_name == "loadout_gift":
            self.pyrcon.send_console_callback("global.playerlist", self.pyrcon_cb_player_update)

    def event_connect_clicked(self, button):
        self.stack_connection_stage.set_visible_child_name("page1")
        self.pyrcon = PyRCON("ws://" + self.textentry_server_address.get_text() + ':' + self.textentry_server_port.get_text() + '/' + self.textentry_password.get_text(), protocols=['http-only', 'chat'])
        self.pyrcon.event_connected_cb = self.pyrcon_event_connected
        self.pyrcon.event_closed_cb = self.pyrcon_event_closed
        self.pyrcon.event_chat_cb = self.pyrcon_event_chat_received
        self.pyrcon.event_console_cb = self.pyrcon_event_console_message_received
        GLib.idle_add(self.connect)

    def connect(self):
        self.pyrcon.connect()

    def event_shutdown(self, widget, event):
        if self.pyrcon is not None:
            sys.stdout.flush()
            self.pyrcon.close()
            sys.stdout.flush()
            self.pyrcon.close_connection()
        Gtk.main_quit()
        return False

    def event_button_send_console(self, button):
        last_iter = self.textbuffer_console.get_end_iter()
        begin_mark = self.textbuffer_console.create_mark(None, last_iter, True)
        if not self.first_console_message:
            last_iter = self.textbuffer_console.get_end_iter()
            self.textbuffer_console.insert(last_iter, "\n")

        self.first_console_message = False

        last_iter = self.textbuffer_console.get_end_iter()
        self.textbuffer_console.insert(last_iter, " $ " + self.textentry_console.get_text())
        last_iter = self.textbuffer_console.get_end_iter()
        end_mark = self.textbuffer_console.create_mark(None, last_iter, True)

        self.textbuffer_console.apply_tag_to_mark_range("console_command", begin_mark, end_mark)

        self.send_console_message(self.textentry_console.get_text())
        self.textentry_console.set_text('')

    def process_console_message(self, message):
        if message == '':
            return

        last_iter = self.textbuffer_console.get_end_iter()
        begin_mark = self.textbuffer_console.create_mark(None, last_iter, True)
        if not self.first_console_message:
            last_iter = self.textbuffer_console.get_end_iter()
            self.textbuffer_console.insert(last_iter, "\n")

        self.first_console_message = False

        last_iter = self.textbuffer_console.get_end_iter()
        console_message = message.replace("\\n", "\n").replace("\\r", '').strip()
        self.textbuffer_console.insert(last_iter, console_message + "")
        last_iter = self.textbuffer_console.get_end_iter()
        end_mark = self.textbuffer_console.create_mark(None, last_iter, True)
        self.last_console_mark = end_mark

        if self.last_console_entry_color == 0:
            self.textbuffer_console.apply_tag_to_mark_range("e1", begin_mark, end_mark)
            self.last_console_entry_color = 1
        elif self.last_console_entry_color == 1:
            self.textbuffer_console.apply_tag_to_mark_range("e2", begin_mark, end_mark)
            self.last_console_entry_color = 0

        self.textview_console.scroll_to_mark(self.last_console_mark, 0.1, True, 0.0, 0.5)


    def send_console_message(self, message, identifier=1):
        dicty = dict()
        dicty['Identifier'] = identifier
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = message

        self.pyrcon.send(json.dumps(dicty))
        GLib.idle_add(self.textview_console.scroll_to_mark, self.last_console_mark, 0.1, True, 0.0, 0.5)


    def build_console_entry_completion(self, commands, variables):
        for command in commands:
            self.entrycompletion_liststore.append([command[0]])
        for variable in variables:
            self.entrycompletion_liststore.append([variable[0]])

    def scroll_chat_to_bottom(self):
        self.textview_chat.scroll_to_mark(self.last_chat_mark, 0.1, True, 0.0, 0.5)

    def process_chat_message(self, username, mtime, message):
        if self.first_chat_message != True:
            last_iter = self.textbuffer_chat.get_end_iter()
            self.textbuffer_chat.insert(last_iter, "\n")

        self.first_chat_message = False

        last_iter = self.textbuffer_chat.get_end_iter()
        begin_chat_mark = self.textbuffer_chat.create_mark(None, last_iter, True)
        self.textbuffer_chat.insert(last_iter, "" + username)
        last_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(last_iter, ":")
        last_iter = self.textbuffer_chat.get_end_iter()
        end_uname_mark = self.textbuffer_chat.create_mark(None, last_iter, True)
        (convert_successful, conversion_text) = unity_to_pango(message)
        if convert_successful:
            self.textbuffer_chat.insert_markup(last_iter, conversion_text, -1)
        else:
            self.textbuffer_chat.insert(last_iter, conversion_text, -1)
        last_iter = self.textbuffer_chat.get_end_iter()
        end_mark = self.textbuffer_chat.create_mark(None, last_iter, True)

        self.last_chat_mark = end_mark

        if username == "SERVER":
            self.textbuffer_chat.apply_tag_to_mark_range("server_chat", begin_chat_mark, end_mark)
            self.textbuffer_chat.apply_tag_to_mark_range("server_uname", begin_chat_mark, end_uname_mark)
        else:
            self.textbuffer_chat.apply_tag_to_mark_range("peasant_chat", begin_chat_mark, end_mark)
            self.textbuffer_chat.apply_tag_to_mark_range("peasant_uname", begin_chat_mark, end_uname_mark)

        GLib.idle_add(self.scroll_chat_to_bottom)


    def send_chat_message(self, button):
        font_color = gtkcolor_to_web(self.buttoncolor_chat)

        self.pyrcon.send_chat_message(self.textentry_chat_message.get_text(),
                                      italic=self.button_italic.get_active(),
                                      text_size=self.scalebutton_text_size.get_value(),
                                      font_color=font_color)

        GLib.idle_add(self.scroll_chat_to_bottom)
        self.textentry_chat_message.set_text('')

    def get_identifier(self):
        self.unique_identifier = self.unique_identifier + 1
        return self.unique_identifier - 1

    def disconnect(self):
        self.stack_connection_stage.set_visible_child_name("page0")
        self.pyrcon.close()
        self.button_disconnect.set_visible(False)
        self.liststore_players.clear()
        self.entrycompletion_liststore.clear()


    ##################################
    # Callbacks for server responses #
    ##################################
    def pyrcon_cg_chat_tail(self, message):
        messages = json.loads(message)

        for message in messages:
            self.process_chat_message(message['Username'], message['Time'], message['Message'])

    def pyrcon_cb_global_find(self, message):
        variables = []
        commands = []

        command_section_start = message.find("Commands:\n") + 10

        command_section = message[command_section_start:].split(sep="\n")
        command_section = [item.strip() for item in command_section]

        variables_section = message[11:command_section_start - 12].split(sep="\n")
        variables_section = [item.strip() for item in variables_section]

        for variable in variables_section:
            if variable == '':
                continue
            variable_name_end = variable.index(' ')
            variable_name = variable[0:variable_name_end]

            default_value_begin = variable.rindex('(')
            default_value_end = variable.rindex(')')

            description = variable[variable_name_end + 1:default_value_begin].strip()
            default_value = variable[default_value_begin + 1:default_value_end]
            variables.append((variable_name, description, default_value,))

        for command in command_section:
            if command == '':
                continue
            command_name = command[0:command.index('(')]
            description = command[command.index(')') + 1:].strip()
            commands.append((command_name, description))

        self.build_console_entry_completion(commands, variables)

    def pyrcon_cb_player_update(self, message):
        data = json.loads(message)
        self.treeview_players.set_model(None)
        self.treestore_players.clear()
        self.liststore_players.clear()

        for player in data:
            display_name = str(player['DisplayName'])
            steam_id = str(player['SteamID'])
            ping = int(player['Ping'])
            address = str(player['Address'].partition(':')[0])
            health = float(player['Health'])
            self.treestore_players.append(None, [display_name, steam_id, ping, address, health])
            self.liststore_players.append([display_name])

        self.treeview_players.set_model(self.treestore_players)

    def pyrcon_event_connected(self):
        GLib.idle_add(self.stack_connection_stage.set_visible_child_name, "page2")
        self.pyrcon.send_console_callback('global.find .', self.pyrcon_cb_global_find)
        self.pyrcon.send_console_callback('chat.tail', self.pyrcon_cg_chat_tail)
        self.button_disconnect.set_visible(True)

    def pyrcon_event_chat_received(self, json_message):
        message = json.loads(json_message)

        GLib.idle_add(self.process_chat_message, message['Username'], message['Time'], message['Message'])

    def pyrcon_event_console_message_received(self, message):
        GLib.idle_add(self.process_console_message, message)


    def pyrcon_event_chat_message(self, username, mtime, message):
        GLib.idle_add(self.process_chat_message, username, time, message)

    def pyrcon_event_closed(self, code, reason):
        self.stack_connection_stage.set_visible_child_name("page0")
        print("Closed client", code, reason)


mw = MainWindow()
Gtk.main()

# realm entity group parent name                              position                  local                     rotation              local                 status invokes
# sv    286882 8380  0      wolf                              (-429.0, 42.5, -272.8)    (-429.0, 42.5, -272.8)    (0.0, 350.7, 0.0)     (0.0, 350.7, 0.0)            TickAi, NetworkPositionTick
