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
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio

class MainWindow:
    def __init__(self):
        self.pyrcon = None
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
        self.button_chat_send = builder.get_object("button_chat_send")
        self.button_chat_send.connect("clicked", self.send_chat_message)
        # Console
        self.textentry_console = builder.get_object("textentry_console")
        self.button_console_send = builder.get_object("button_console_send")
        self.textview_chat = builder.get_object("textview_chat")
        self.textbuffer_chat = Gtk.TextBuffer.new()
        self.textview_chat.set_buffer(self.textbuffer_chat)
        self.treeview_players = builder.get_object("treeview_players")
        self.textentry_receiving_player = builder.get_object("textentry_receiving_player")
        self.treeview_loadout_item_list = builder.get_object("treeview_loadout_item_list")
        self.button_loadout_add = builder.get_object("button_loadout_add")
        self.button_loadout_remove = builder.get_object("button_loadout_remove")
        self.button_loadout_edit = builder.get_object("button_loadout_edit")

    def event_button_clicked(self, button):
        self.stack_connection_stage.set_visible_child_name("page1")
        self.pyrcon = PyRCON("ws://" + self.textentry_server_address.get_text() + ':' + self.textentry_server_port.get_text() + '/' + self.textentry_password.get_text(), protocols=['http-only', 'chat'])
        self.pyrcon.event_connected_cb = self.event_connected
        self.pyrcon.event_message_cb = self.event_rcon_message_received
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

    def event_connected(self):
        self.stack_connection_stage.set_visible_child_name("page2")

    def event_rcon_message_received(self, message):

        dicty = json.loads(message.data)
        identifier = dicty['Identifier']
        mtype = dicty['Type']
        stacktrace = dicty['Stacktrace']
        # assert(stacktrace == '')

        # Chat Message
        if(mtype == 'Chat'):
            message = json.loads(dicty['Message'])
            self.process_chat_message(message)
        elif(mtype == "Log"):
            pass
        elif(mtype == "Generic"):
            # Chat Message Received
            if 'Message' in dicty:
                print("mes", dicty['Messages'])
                messages = json.loads(dicty['Message'])
                for message in messages:
                    GLib.idle_add(self.process_chat_message, message)
        else:
            print("Unhandled message type", dicty)

        # print("Type:", dicty['message'])
    def process_chat_message(self, message):
        text = message['Message']
        color = message['Color']
        time = message['Time']
        username = message['Username']
        userid = message['UserId']

        end_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(end_iter, username)
        end_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(end_iter, ":")
        end_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(end_iter, text)
        end_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(end_iter, "\n")

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
        print("Sending", json.dumps(dicty))
        self.pyrcon.send(json.dumps(dicty))

    def gtkcolor_to_web(self, widget):
        color = self.buttoncolor_chat.get_color().to_floats()
        string = "#" + '{0:x}'.format((int(255.0*(color[0]))))
        string = string + '{0:x}'.format((int(255.0*(color[1]))))
        string = string + '{0:x}'.format((int(255.0*(color[2]))))

        print(string)
        return ""




mw = MainWindow()
Gtk.main()

