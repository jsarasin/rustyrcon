#!/usr/bin/python3

# sudo -H pip3 install appdirs

#
# (rustyrcon.py:7098): Gtk-WARNING **: 00:50:46.359: Invalid text buffer iterator: either the iterator is uninitialized, or the characters/pixbufs/widgets in the buffer have been modified since the iterator was created.
# You must use marks, character numbers, or line numbers to preserve a position across buffer modifications.
# You can apply tags and insert marks without invalidating your iterators,
# but any mutation that affects 'indexable' buffer contents (contents that can be referred to by character offset)
# will invalidate all outstanding iterators
#
# (rustyrcon.py:7098): Gtk-WARNING **: 00:50:46.359: Invalid text buffer iterator: either the iterator is uninitialized, or the characters/pixbufs/widgets in the buffer have been modified since the iterator was created.
# You must use marks, character numbers, or line numbers to preserve a position across buffer modifications.
# You can apply tags and insert marks without invalidating your iterators,
# but any mutation that affects 'indexable' buffer contents (contents that can be referred to by character offset)
# will invalidate all outstanding iterators

# (rustyrcon.py:4773): Gtk-ERROR **: 19:33:14.339: Unknown segment type: \xc0\\xa9\u0001



import time
from datetime import datetime
from datetime import timedelta

import json
import sys
from os import path, makedirs
from pyrcon import PyRCON
from utilities import unity_to_pango, gtkcolor_to_web
from appdirs import user_data_dir

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject
from betterbuffer import BetterBuffer, scroll_to_textview_bottom

from ws4py.exc import HandshakeError
from rust import RustMessageType, get_console_message_info


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
        self.server_list = []
        self.default_connection = ""
        self.editing_connection = None

        # Program data
        self.entity_list = None

        # Chat message globals
        self.first_chat_message = True
        self.last_chat_mark = None

        # Console globals
        self.first_console_message = True
        self.last_console_entry_color = 'e1'
        self.last_console_mark = None

        # Shared Models
        self.liststore_players = Gtk.ListStore(str)# GObject.GType([str]) #TYPE_PYOBJECT
        self.entrycompletion_liststore = Gtk.ListStore(str,)# GObject.GType([str]) #TYPE_PYOBJECT
        self.liststore_servers = Gtk.ListStore(str)

        # GUI initialization
        self.connect_builder_objects()
        self.window.show_all()

        self.setup_connection_dialog()

    def populate_server_list(self):
        self.liststore_servers.clear()
        for server in self.server_list:
            self.liststore_servers.append([server['name']])

        self.combo_servers.set_model(self.liststore_servers)

    def connect_builder_objects(self):
        builder = Gtk.Builder()
        builder.add_from_file("window.glade")

        self.window = builder.get_object("window")
        self.window.connect("delete-event", self.event_shutdown)
        self.stack_rcon = builder.get_object('stack_rcon')
        self.stack_rcon.connect('notify::visible-child', self.event_stack_rcon_switched)
        self.button_disconnect = builder.get_object('button_disconnect')
        self.button_disconnect.connect('clicked', self.event_button_disconnect_clicked)
        self.revealer_disconnect = builder.get_object('revealer_disconnect')

        # Connection Stage 1
        self.stack_connection_stage = builder.get_object("stack_connection_stage")

        # Connection View
        self.button_connect = builder.get_object("button_connect")
        self.button_connect.connect("clicked", self.event_button_connect_clicked)
        self.combo_servers = builder.get_object('combo_servers')
        self.combo_servers.connect('changed', self.event_combo_servers_changed)

        self.button_new_connection = builder.get_object('button_new_connection')
        self.button_new_connection.connect("clicked", self.event_button_new_clicked)
        self.button_edit_connection = builder.get_object('button_edit_connection')
        self.button_edit_connection.connect("clicked", self.event_button_edit_clicked)
        self.button_delete_connection = builder.get_object('button_delete_connection')
        self.button_delete_connection.connect("clicked", self.event_button_delete_clicked)

        # Connection Editor
        self.stack_connect = builder.get_object('stack_connect')
        self.entry_server_name = builder.get_object('entry_server_name')
        self.entry_server_address = builder.get_object('entry_server_address')
        self.entry_port = builder.get_object('entry_port')
        self.entry_password = builder.get_object('entry_password')
        self.button_save_connection = builder.get_object('button_save_connection')
        self.button_save_connection.connect('clicked', self.event_button_save_connection_clicked)
        self.button_discard_connection = builder.get_object('button_discard_connection')
        self.button_discard_connection.connect('clicked', self.event_button_discard_connection)

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
        self.textbuffer_console.create_tag("time", foreground="darkgrey", style=Pango.Style.ITALIC, scale=0.75)
        self.textbuffer_console.create_tag("cat", paragraph_background="red", foreground='white', style=Pango.Style.ITALIC, scale=0.75)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.SAVE), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.CONNECT), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.DISCONNECT_GAME), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.LOAD_BEGIN), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.MANIFEST_UPDATE), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.CHAT), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.ENTER_GAME), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.KILLED_BY_PLAYER), invisible=False, invisible_set=True)
        self.textbuffer_console.create_tag('mtype' + str(RustMessageType.KILLED_BY_ENTITY), invisible=False, invisible_set=True)
        self.textview_console.set_buffer(self.textbuffer_console)


        self.treeview_players = builder.get_object("treeview_players")
        self.entrycompletion_console = builder.get_object("entrycompletion_console")
        self.entrycompletion_console.set_model(self.entrycompletion_liststore)
        self.entrycompletion_console.set_text_column(0)

        self.button_console_view_settings = builder.get_object('button_console_view_settings')
        self.button_console_view_settings.connect('clicked', self.event_button_console_view_settings)
        self.button_console_clear = builder.get_object('button_console_clear')
        self.button_console_clear.connect('clicked', self.event_button_console_clear_clicked)
        self.popover_console_visible = builder.get_object('popover_console_visible')

        self.check_visible_save = builder.get_object('check_visible_save')
        self.check_visible_save.connect('toggled', self.event_check_visible_toggled)
        self.check_visible_connect = builder.get_object('check_visible_connect')
        self.check_visible_connect.connect('toggled', self.event_check_visible_toggled)
        self.check_visible_disconnect = builder.get_object('check_visible_disconnect')
        self.check_visible_disconnect.connect('toggled', self.event_check_visible_toggled)
        self.check_visible_load_begin = builder.get_object('check_visible_load_begin')
        self.check_visible_load_begin.connect('toggled', self.event_check_visible_toggled)
        self.check_visible_manifest = builder.get_object('check_visible_manifest')
        self.check_visible_manifest.connect('toggled', self.event_check_visible_toggled)
        self.check_visible_chat = builder.get_object('check_visible_chat')
        self.check_visible_chat.connect('toggled', self.event_check_visible_toggled)

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

    def load_config_file(self):
        config_file = path.join(user_data_dir("RustyRCON", "opensource"), "settings.json")

        with open(config_file, "r") as f:
            initial_config = json.load(f)

        self.default_connection = initial_config['default']
        self.server_list = initial_config['servers']

        print("Initial default:", self.default_connection)
        print("servers:", self.server_list)


    def write_config_file(self):
        config_file = path.join(user_data_dir("RustyRCON", "opensource"), "settings.json")

        config = dict()
        config['default'] = self.default_connection
        config['servers'] = self.server_list

        with open(config_file, "w") as f:
            json.dump(config, f)

    def setup_connection_dialog(self):
        config_file = path.join(user_data_dir("RustyRCON", "opensource"), "settings.json")
        print("config", config_file)

        if path.exists(config_file) == False:
            initial_config = dict()
            initial_config['default'] = ''
            initial_config['servers'] = []

            makedirs(path.dirname(config_file), exist_ok=True)
            with open(config_file, "w") as f:
                json.dump(initial_config, f)

            print("Created emtpy file")

        self.load_config_file()
        self.populate_server_list()

        self.select_combo_connection(self.default_connection)



        if self.server_list == []:
            self.revealer_disconnect.set_reveal_child(False)
            self.editing_connection = None
            self.stack_connect.set_visible_child_name('page_edit')
            return
    def select_combo_connection(self, connection_name):
        for index, server in enumerate(self.server_list):
            if server['name'] == connection_name:
                self.combo_servers.set_active(index)
                break

    def event_check_visible_toggled(self, check):
        if check is self.check_visible_save:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.SAVE))
        if check is self.check_visible_chat:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.CHAT))
        if check is self.check_visible_connect:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.CONNECT))
        if check is self.check_visible_disconnect:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.DISCONNECT_GAME))
        # if check is self.check_visible_:
        #     tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.ENTER_GAME))
        # if check is self.check_visible_chat:
        #     tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.KILLED_BY_ENTITY))
        # if check is self.check_visible_chat:
        #     tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.KILLED_BY_PLAYER))
        if check is self.check_visible_load_begin:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.LOAD_BEGIN))
        if check is self.check_visible_manifest:
            tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.MANIFEST_UPDATE))
        # if check is self.check_visible_chat:
        #     tag = self.textbuffer_console.get_tag_table().lookup('mtype' + str(RustMessageType.SUICIDE))


        if check.get_active():
            pass
            # tag.props.size = 0.0
        else:
            tag.props.size_set = True
            tag.props.size_points = 0.0

            pass
            # tag.props.size = 1024.0

    def event_button_console_clear_clicked(self, button):
        self.reset_interface()

    def event_button_console_view_settings(self, button):
        self.popover_console_visible.popup()

    def event_button_discard_connection(self, button):
        self.stack_connect.set_visible_child_name('page_connect')
        self.editing_connection = ""

    def event_combo_servers_changed(self, combo):
        selected = combo.get_active_text()
        self.default_connection = selected
        self.write_config_file()

    def event_button_new_clicked(self, button):
        self.entry_server_name.set_text('')
        self.entry_server_address.set_text('')
        self.entry_port.set_text('')
        self.entry_password.set_text('')
        self.editing_connection = ""
        self.stack_connect.set_visible_child_name('page_edit')

    def event_button_edit_clicked(self, button):
        server = self.get_selected_connection()

        self.entry_server_name.set_text(server['name'])
        self.entry_server_address.set_text(server['address'])
        self.entry_port.set_text(server['port'])
        self.entry_password.set_text(server['password'])

        self.editing_connection = server['name']
        self.stack_connect.set_visible_child_name('page_edit')

    def event_button_delete_clicked(self, button):
        dialog = Gtk.Dialog()
        dialog.set_transient_for(self.window)
        dialog.add_button("Delete", 0)
        dialog.add_button("Cancel", 1)
        dialog.set_default_response(1)
        dialog.get_content_area().add(Gtk.Label("Are you sure you want to delete this?"))
        dialog.show_all()
        result = dialog.run()
        if result == 1:
            dialog.close()
            del(dialog)
            return

        dialog.close()
        del(dialog)


        # Delete the item
        selected = self.get_selected_connection()
        to_sel_index = self.combo_servers.get_active() - 1
        if to_sel_index < 0:
            to_sel_index = 0

        self.server_list.remove(selected)
        self.write_config_file()
        self.populate_server_list()

        # Ensure selection or switch to the new connection stack
        if len(self.combo_servers.get_model()) == 0:
            self.event_button_new_clicked(button)
            self.button_discard_connection.hide()
            self.default_connection = ''
        else:
            self.combo_servers.set_active_iter(self.combo_servers.get_model()[to_sel_index].iter)
            self.default_connection = self.combo_servers.get_active()


    def event_button_save_connection_clicked(self, button):
        combo_selected_index = self.combo_servers.get_active()

        if self.entry_server_name.get_text() == '':
            prompt = Gtk.Dialog()
            prompt.set_transient_for(self.window)
            prompt.add_button("Okay", 0)
            prompt.set_default_response(0)
            prompt.get_content_area().add(Gtk.Label("Your server must have a name."))
            prompt.show_all()
            result = prompt.run()
            prompt.close()
            return

        # Check if these settings conflict with another server
        for index, server in enumerate(self.server_list):
            if self.entry_server_name.get_text().lower() == server['name'].lower():
                if self.editing_connection.lower() != server['name'].lower():
                    prompt = Gtk.Dialog()
                    prompt.set_transient_for(self.window)
                    prompt.add_button("Replace Existing", 0)
                    prompt.add_button("Rename Current", 1)
                    prompt.set_default_response(1)
                    prompt.get_content_area().add(Gtk.Label("A connection with this name already exists, would you like to:"))
                    prompt.show_all()
                    result = prompt.run()
                    prompt.close()

                    if result != 0:
                        self.entry_server_address.grab_focus()
                        return

                self.server_list[index] = self.connection_edit_form_to_struct()
                self.write_config_file()
                self.populate_server_list()
                self.combo_servers.set_active(combo_selected_index)
                self.stack_connect.set_visible_child_name('page_connect')
                self.button_discard_connection.show()
                return

        # New connection entry
        self.server_list.append(self.connection_edit_form_to_struct())
        self.write_config_file()
        self.populate_server_list()

        # Select the last item which will be what we just added
        first = self.combo_servers.get_model().get_iter_first()
        last = first
        while True:
            next = self.combo_servers.get_model().iter_next(last)
            if next != None:
                last = next
                continue
            else:
                break
        self.combo_servers.set_active_iter(last)

        self.stack_connect.set_visible_child_name('page_connect')
        self.button_discard_connection.set_visible(True)
        self.select_combo_connection(self.entry_server_name.get_text())

    ####################
    ## Event handlers ##
    ####################
    def event_button_disconnect_clicked(self, button):
        self.disconnect()

    def event_stack_rcon_switched(self, event, cat):
        child_name = self.stack_rcon.get_visible_child_name()

        if child_name == "players" or child_name == "loadout_gift":
            self.pyrcon.send_console_callback("global.playerlist", self.pyrcon_cb_player_update)

    def event_button_connect_clicked(self, button):
        server = self.get_selected_connection()
        if server == None:
            prompt = Gtk.Dialog()
            prompt.set_transient_for(self.window)
            prompt.get_content_area().add(Gtk.Label("You must select a connection"))
            prompt.add_button("Okay", 0)
            prompt.show_all()
            prompt.run()
            prompt.close()
            return

        self.reset_interface()

        self.stack_connection_stage.set_visible_child_name("page1")
        self.pyrcon = PyRCON("ws://" + server['address'] + ':' + server['port'] + '/' + server['password'], protocols=['http-only', 'chat'])
        self.pyrcon.event_connected_cb = self.pyrcon_event_connected
        self.pyrcon.event_closed_cb = self.pyrcon_event_closed
        self.pyrcon.event_chat_cb = self.pyrcon_event_chat_received
        self.pyrcon.event_console_cb = self.pyrcon_event_console_message_received
        GLib.idle_add(self.connect)

    def reset_interface(self):
        start = self.textbuffer_console.get_start_iter()
        end = self.textbuffer_console.get_end_iter()
        self.textbuffer_console.delete(start, end)
        self.liststore_players.clear()
        self.entrycompletion_liststore.clear()

    def connect(self):
        try:
            self.pyrcon.connect()
        except HandshakeError:
            print("Failed to connect")
            del self.pyrcon
            self.pyrcon = None
            self.stack_connection_stage.set_visible_child_name('page0')


    def event_shutdown(self, widget, event):
        if self.pyrcon is not None:
            sys.stdout.flush()
            self.pyrcon.close()
            sys.stdout.flush()
            self.pyrcon.close_connection()
        Gtk.main_quit()
        return False

    def event_button_send_console(self, button):
        console_command = ''
        if self.textbuffer_console.get_char_count() > 0:
            console_command = "\n"

        console_command = console_command + " $ " + self.textentry_console.get_text()
        tags = [self.textbuffer_console.get_tag("console_command")]

        last_iter = self.textbuffer_console.get_end_iter()
        self.textbuffer_console.insert_with_tags(last_iter, console_command, *tags)

        self.send_console_message(self.textentry_console.get_text())
        self.textentry_console.set_text('')

    def connection_edit_form_to_struct(self):
        struct = dict()
        struct['address'] = self.entry_server_address.get_text()
        struct['port'] = self.entry_port.get_text()
        struct['name'] = self.entry_server_name.get_text()
        struct['password'] = self.entry_password.get_text()

        return struct

    def get_selected_connection(self):
        text = self.combo_servers.get_active_text()

        for index, server in enumerate(self.server_list):
            if text == server['name']:
                return self.server_list[index]

        return None

    def set_selected_connection(self):
        treemodel = self.combo_servers.get_model()



    def load_entity_types(self):
        fp = open("../rust_entities.json", 'r')
        self.entity_list = json.load(fp)
        fp.close()

    def get_normal_date(self, dt):
        return dt.strftime('%b %d').strip()

    def get_normal_time(self, dt):
        return '{d:%l}:{d.minute:02}:{d.second:02} {d:%p}'.format(d=dt).strip()

    def get_message_time_string(self, dt):
        now = datetime.now()
        mtime_dt = datetime.fromtimestamp(dt)
        # This doesn't take into account timezones, but roughly if the message is
        # more than a few hours old we should put it all
        if now - mtime_dt > timedelta(hours=6):
            time_string = self.get_normal_date(mtime_dt) + ' ' + self.get_normal_time(mtime_dt)
        else:
            time_string = self.get_normal_time(mtime_dt)

        return time_string

    def add_console_message_to_buffer(self, message, mtime):
        if message == '':
            return

        if self.textbuffer_console.get_char_count() == 0:
            first_item = True
        else:
            first_item = False

        tags = []
        message_type = get_console_message_info(message)
        if message_type is not None:
            tags.append(self.textbuffer_console.get_tag_table().lookup("mtype" + str(message_type)))

        if first_item:
            console_message = ''
        else:
            console_message = "\n"

        console_message = console_message + message.replace("\\n", "\n").replace("\\r", '').strip()

        last_iter = self.textbuffer_console.get_end_iter()
        self.textbuffer_console.insert_with_tags(last_iter, console_message, *tags)

        GLib.idle_add(scroll_to_textview_bottom, self.textview_console)



    def add_chat_message_to_buffer(self, username, mtime, message):
        if self.textbuffer_chat.get_char_count() > 0:
            last_iter = self.textbuffer_chat.get_end_iter()
            self.textbuffer_chat.insert(last_iter, "\n")

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

        self.textbuffer_chat.delete_mark(begin_chat_mark)
        self.textbuffer_chat.delete_mark(end_uname_mark)
        self.textbuffer_chat.delete_mark(end_mark)

        scroll_to_textview_bottom(self.textview_chat)

    def send_console_message(self, message, identifier=1):
        dicty = dict()
        dicty['Identifier'] = identifier
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = message

        self.pyrcon.send(json.dumps(dicty))
        scroll_to_textview_bottom(self.textview_console)

    def send_chat_message(self, button):
        font_color = gtkcolor_to_web(self.buttoncolor_chat)

        self.pyrcon.send_chat_message(self.textentry_chat_message.get_text(),
                                      italic=self.button_italic.get_active(),
                                      text_size=self.scalebutton_text_size.get_value(),
                                      font_color=font_color)

        scroll_to_textview_bottom(self.textview_chat)
        self.textentry_chat_message.set_text('')

    def build_console_entry_completion(self, commands, variables):
        for command in commands:
            self.entrycompletion_liststore.append([command[0]])
        for variable in variables:
            self.entrycompletion_liststore.append([variable[0]])

    def get_identifier(self):
        self.unique_identifier = self.unique_identifier + 1
        return self.unique_identifier - 1

    def disconnect(self):
        self.stack_connection_stage.set_visible_child_name("page0")
        self.pyrcon.close()
        self.revealer_disconnect.set_reveal_child(False)

    ##################################
    # Callbacks for server responses #
    ##################################
    def pyrcon_cb_console_tail(self, message):
        messages = json.loads(message)
        for message in messages:
            self.add_console_message_to_buffer(message['Message'].rstrip(), message['Time'])



    def pyrcon_cb_chat_tail(self, message):
        messages = json.loads(message)

        for message in messages:
            self.add_chat_message_to_buffer(message['Username'], message['Time'], message['Message'])

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
        self.pyrcon.send_console_callback('chat.tail', self.pyrcon_cb_chat_tail)
        self.pyrcon.send_console_callback('console.tail', self.pyrcon_cb_console_tail)
        self.revealer_disconnect.set_reveal_child(True)

    def pyrcon_event_chat_received(self, json_message):
        message = json.loads(json_message)

        GLib.idle_add(self.add_chat_message_to_buffer, message['Username'], message['Time'], message['Message'])

    def pyrcon_event_console_message_received(self, message, time):
        GLib.idle_add(self.add_console_message_to_buffer, message, time)


    def pyrcon_event_chat_message(self, username, mtime, message):
        GLib.idle_add(self.add_chat_message_to_buffer, username, time, message)

    def pyrcon_event_closed(self, code, reason):
        self.stack_connection_stage.set_visible_child_name("page0")
        start = self.textbuffer_chat.get_start_iter()
        end = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.delete(start, end)


mw = MainWindow()
Gtk.main()
