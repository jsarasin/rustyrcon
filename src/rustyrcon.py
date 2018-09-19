#!/usr/bin/python3

# Cool items:
# ak
# ammo.rifle

import time
import json
import sys
from pyrcon import PyRCON

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango
from betterbuffer import BetterBuffer

class BufferManager:
    def __init__(self, buffer):
        self.buffer = buffer


class MainWindow:
    def __init__(self):
        self.pyrcon = None
        self.first_chat_message = True

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

        # Connection Stage 1
        self.stack_connection_stage = builder.get_object("stack_connection_stage")
        self.textentry_server_address = builder.get_object("textentry_server_address")
        self.textentry_server_port = builder.get_object("textentry_server_port")
        self.textentry_password = builder.get_object("textentry_password")
        self.button_connect = builder.get_object("button_connect")
        self.button_connect.connect("clicked", self.event_button_clicked)

        # Connection Stage 2
        # Connection Stage 3
        # Chat
        self.textentry_chat_who = builder.get_object("textentry_chat_who")
        self.buttoncolor_chat = builder.get_object("buttoncolor_chat")
        self.textentry_chat_message = builder.get_object("textentry_chat_message")
        self.textentry_chat_message.connect('activate', self.send_chat_message)
        self.button_chat_send = builder.get_object("button_chat_send")
        self.button_chat_send.connect("clicked", self.send_chat_message)
        self.textview_chat = builder.get_object("textview_chat")
        self.textbuffer_chat = BetterBuffer()
        self.textbuffer_chat.create_tag("peasant_chat", paragraph_background="lightgreen", wrap_mode=Gtk.WrapMode.WORD_CHAR, foreground='Black')
        self.textbuffer_chat.create_tag("peasant_uname", weight=Pango.Weight.BOLD, foreground='Black' )
        self.textbuffer_chat.create_tag("server_chat", paragraph_background="lightblue", wrap_mode=Gtk.WrapMode.WORD_CHAR, foreground='Black')
        self.textbuffer_chat.create_tag("server_uname", weight=Pango.Weight.BOLD, foreground='Black' )
        self.textview_chat.set_buffer(self.textbuffer_chat)
        self.buffermanager_chat = BufferManager(self.textbuffer_chat)


        # Console
        self.textentry_console = builder.get_object("textentry_console")
        self.button_console_send = builder.get_object("button_console_send")

        # Players
        self.treeview_players = builder.get_object("treeview_players")

        # Loadout Gift
        self.textentry_receiving_player = builder.get_object("textentry_receiving_player")
        self.treeview_loadout_item_list = builder.get_object("treeview_loadout_item_list")
        self.button_loadout_add = builder.get_object("button_loadout_add")
        self.button_loadout_remove = builder.get_object("button_loadout_remove")
        self.button_loadout_edit = builder.get_object("button_loadout_edit")

    def event_button_clicked(self, button):
        self.stack_connection_stage.set_visible_child_name("page1")
        self.pyrcon = PyRCON("ws://" + self.textentry_server_address.get_text() + ':' + self.textentry_server_port.get_text() + '/' + self.textentry_password.get_text(), protocols=['http-only', 'chat'])
        self.pyrcon.event_connected_cb = self.pyrcon_event_connected
        self.pyrcon.event_message_cb = self.pyrcon_event_rcon_message_received
        self.pyrcon.connect()
        # self.pyrcon.run()

    def event_shutdown(self, widget, event):
        if self.pyrcon is not None:
            sys.stdout.flush()
            self.pyrcon.close()
            sys.stdout.flush()
            self.pyrcon.close_connection()
        Gtk.main_quit()

        return False

    def pyrcon_event_connected(self):
        GLib.idle_add(self.stack_connection_stage.set_visible_child_name, "page2")

    def pyrcon_event_rcon_message_received(self, message):
        dicty = json.loads(message.data)
        GLib.idle_add(self.safe_wee, dicty)

    def safe_wee(self, dicty):
        """
         --- JSON Parse Error ---
        message type: Generic
         -- dicty --
        {'Message': 'Saved 20,838 ents, cache(0.01), write(0.01), disk(0.00).', 'Identifier': 0, 'Type': 'Generic', 'Stacktrace': ''}
         -- message --
        Saved 20,838 ents, cache(0.01), write(0.01), disk(0.00).
        Expecting value at 0

         --- JSON Parse Error ---
        message type: Generic
         -- dicty --
        {'Message': 'Saving complete', 'Identifier': 0, 'Type': 'Generic', 'Stacktrace': ''}
         -- message --
        Saving complete
        Expecting value at 0

        """
        identifier = dicty['Identifier']
        mtype = dicty['Type']
        stacktrace = dicty['Stacktrace']
        #assert(stacktrace == '')

        try:
            # Chat Message
            if(mtype == 'Chat'):
                message = json.loads(dicty['Message'])
                self.process_chat_message(message)
            elif(mtype == "Log"):
                pass
            elif(mtype == "Generic"):
                # Chat Message Received
                if 'Message' in dicty:
                    if dicty['Message'] == '':
                        return
                    # For some reason Rust occasionally sends chat messages like this on top of the normal way
                    if dicty['Message'][0:6] == '[CHAT]':
                        return
                    if dicty['Message'][0:5] == 'Saved':
                        return
                    if dicty['Message'][0:6] == 'Saving':
                        return

                    messages = json.loads(dicty['Message'])
                    for message in messages:
                        GLib.idle_add(self.process_chat_message, message)
                        sys.stdout.flush()
            else:
                print("Unhandled message type", dicty)
                sys.stdout.flush()
        except json.decoder.JSONDecodeError as e:
            print(" --- JSON Parse Error ---")
            print("message type:", mtype)
            print(" -- dicty --")
            print(dicty)
            print(" -- message --")
            print(e.doc)
            print(e.msg, "at", e.pos)
            sys.stdout.flush()

    def scroll_to_bottom(self):
        # start, end = self.textbuffer_chat.get_bounds()
        #iter = self.textbuffer_chat.get_iter_at_line(self.textbuffer_chat.get_line_count() - 1)
        # self.textview_chat.scroll_to_iter(end, 0.0, False, 0, 1)
        print(self.textview_chat.scroll_to_mark(self.last_mark, 0.1, True, 0.0, 0.5))


    def process_chat_message(self, message):
        text = message['Message']
        color = message['Color']
        time = message['Time']
        username = message['Username']
        userid = message['UserId']

        if self.first_chat_message != True:
            last_iter = self.textbuffer_chat.get_end_iter()
            self.textbuffer_chat.insert(last_iter, "\n")

        self.first_chat_message = False


        last_iter = self.textbuffer_chat.get_end_iter()
        begin_chat_mark = self.textbuffer_chat.create_mark(None, last_iter, True)
        self.textbuffer_chat.insert(last_iter, username)
        last_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(last_iter, ":")
        last_iter = self.textbuffer_chat.get_end_iter()
        end_uname_mark = self.textbuffer_chat.create_mark(None, last_iter, True)
        self.textbuffer_chat.insert(last_iter, text)
        last_iter = self.textbuffer_chat.get_end_iter()
        end_mark = self.textbuffer_chat.create_mark(None, last_iter, True)

        self.last_mark = end_mark

        if username == "SERVER":
            self.textbuffer_chat.apply_tag_to_mark_range("server_chat", begin_chat_mark, end_mark)
            self.textbuffer_chat.apply_tag_to_mark_range("server_uname", begin_chat_mark, end_uname_mark)
        else:
            self.textbuffer_chat.apply_tag_to_mark_range("peasant_chat", begin_chat_mark, end_mark)
            self.textbuffer_chat.apply_tag_to_mark_range("peasant_uname", begin_chat_mark, end_uname_mark)

        GLib.idle_add(self.scroll_to_bottom)

    def send_chat_message(self, button):
        rcon_message = dict()
        rcon_message['Message'] = self.textentry_chat_message.get_text()
        rcon_message['UserId'] = 0
        rcon_message['Username'] = self.textentry_chat_who.get_text()
        rcon_message['Time'] = time.time()
        rcon_message['Color'] = self.gtkcolor_to_web(self.buttoncolor_chat)

        dicty = dict()
        dicty['Identifier'] = 1
        dicty['Name'] = "WebRcon"
        dicty['Message'] = "say " + self.textentry_chat_message.get_text() #json.dumps(rcon_message)

        self.pyrcon.send(json.dumps(dicty))
        GLib.idle_add(self.scroll_to_bottom)
        self.textentry_chat_message.set_text('')

    def gtkcolor_to_web(self, widget):
        color = self.buttoncolor_chat.get_color().to_floats()
        string = "#" + '{0:x}'.format((int(255.0*(color[0]))))
        string = string + '{0:x}'.format((int(255.0*(color[1]))))
        string = string + '{0:x}'.format((int(255.0*(color[2]))))

        print(string)
        return ""




mw = MainWindow()
Gtk.main()

