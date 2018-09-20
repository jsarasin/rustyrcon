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
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject
from betterbuffer import BetterBuffer

class BufferManager:
    def __init__(self, buffer):
        self.buffer = buffer


class MainWindow:
    def __init__(self):
        self.pyrcon = None
        # Program initialization
        self.have_command_and_var_cache = False

        # Chat message globals
        self.first_chat_message = True
        self.last_chat_mark = None

        # Console globals
        self.first_console_message = True
        self.last_console_entry_color = 0
        self.last_console_mark = None


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
        self.textview_console.set_buffer(self.textbuffer_console)


        self.treeview_players = builder.get_object("treeview_players")
        self.entrycompletion_console = builder.get_object("entrycompletion_console")
        self.entrycompletion_liststore = Gtk.ListStore(str,)# GObject.GType([str]) #TYPE_PYOBJECT
        self.entrycompletion_console.set_model(self.entrycompletion_liststore)
        self.entrycompletion_console.set_text_column(0)
        # Players


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
        self.send_console_message("global.find .")

    def pyrcon_event_rcon_message_received(self, message):
        dicty = json.loads(message.data)
        GLib.idle_add(self.safe_wee, dicty)

    def process_chat_message(self, message):
        pass
    def process_console_message(self, message):
        pass

    def event_button_send_console(self, button):
        self.send_console_message(self.textentry_console.get_text())
        self.textentry_console.set_text('')

    def send_console_message(self, message):
        dicty = dict()
        dicty['Identifier'] = 1
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = message

        self.pyrcon.send(json.dumps(dicty))
        GLib.idle_add(self.textview_console.scroll_to_mark, self.last_console_mark, 0.1, True, 0.0, 0.5)

    def process_initial_cache_message(self, message):
        variables = []
        commands = []
        self.have_command_and_var_cache = True
        # message = message.replace("\\n ", "\n")

        command_section_start = message.find("Commands:\n") + 10

        command_section = message[command_section_start:].split(sep="\n")
        command_section = [item.strip() for item in command_section]

        variables_section = message[11:command_section_start-12].split(sep="\n")
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
            variables.append((variable_name, description, default_value, ))

        for command in command_section:
            if command == '':
                continue
            command_name = command[0:command.index('(')]
            description = command[command.index(')') + 1:].strip()
            commands.append((command_name, description))

        self.build_console_entry_completion(commands, variables)

    def build_console_entry_completion(self, commands, variables):
        for command in commands:
            self.entrycompletion_liststore.append([command[0]])
        for variable in variables:
            self.entrycompletion_liststore.append([variable[0]])



    def safe_wee(self, dicty):
        identifier = dicty['Identifier']
        mtype = dicty['Type']
        stacktrace = dicty['Stacktrace']
        #assert(stacktrace == '')

        if self.have_command_and_var_cache == False:
            if 'Message' in dicty:
                if dicty['Message'][0:10] == "Variables:":
                    self.process_initial_cache_message(dicty['Message'])
                    return

        if dicty['Message'][0:1] != '{' and dicty['Message'] != '':
            last_iter = self.textbuffer_console.get_end_iter()
            begin_mark = self.textbuffer_console.create_mark(None, last_iter, True)
            if not self.first_console_message:
                last_iter = self.textbuffer_console.get_end_iter()
                self.textbuffer_console.insert(last_iter, "\n")

            self.first_console_message = False

            last_iter = self.textbuffer_console.get_end_iter()
            self.textbuffer_console.insert(last_iter, repr(dicty['Message'])[1:-1] + "")
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
            return
            print(" --- JSON Parse Error ---")
            print("message type:", mtype)
            print(" -- dicty --")
            print(dicty)
            print(" -- message --")
            print(e.doc)
            print(e.msg, "at", e.pos)
            sys.stdout.flush()

    def scroll_chat_to_bottom(self):
        # start, end = self.textbuffer_chat.get_bounds()
        #iter = self.textbuffer_chat.get_iter_at_line(self.textbuffer_chat.get_line_count() - 1)
        # self.textview_chat.scroll_to_iter(end, 0.0, False, 0, 1)
        self.textview_chat.scroll_to_mark(self.last_chat_mark, 0.1, True, 0.0, 0.5)


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
        self.textbuffer_chat.insert(last_iter, "" + username)
        last_iter = self.textbuffer_chat.get_end_iter()
        self.textbuffer_chat.insert(last_iter, ":")
        last_iter = self.textbuffer_chat.get_end_iter()
        end_uname_mark = self.textbuffer_chat.create_mark(None, last_iter, True)
        (convert_successful, conversion_text) = self.unitymu_to_pangomu(text)
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

    def unitymu_to_pangomu(self, text):
        original_text = text
        markup_error = False

        # Add a " after all color tags
        pos = 0
        while True:
            if pos >= len(text):
                break
            found = text.find("<color=", pos)
            if found == -1:
                break

            closing = text.find(">", found)
            if closing == -1:
                markup_error = True
                print("Color markup error @", found)
                break

            text = text[0:closing] + "\"" + text[closing:]
            pos = closing + 1
        # Add a " after size tags
        pos = 0

        while True:
            if pos >= len(text):
                break
            found = text.find("<size=", pos)
            if found == -1:
                break

            closing = text.find(">", found)
            if closing == -1:
                markup_error = True
                print("Size markup error @", found)
                break

            text = text[0:closing] + "\"" + text[closing:]
            pos = closing + 1

        text = text.replace('<color=#', "<span fgcolor=\"#")
        text = text.replace('<size=', "<span font=\"")
        text = text.replace('</color>', '</span>')
        text = text.replace('</size>', '</span>')

        if markup_error:
            print("Markup Error: ", original_text)
            return (False, original_text)

        return (True, text)

    def send_chat_message(self, button):
        font_color = self.gtkcolor_to_web()

        message_composed = ""
        if self.button_italic.get_active():
            message_composed = message_composed + "<i>"
        if self.scalebutton_text_size.get_value() != 14:
            message_composed = message_composed + "<size=" + str(int(self.scalebutton_text_size.get_value())) + ">"
        if font_color != "#FFFFFF":
            message_composed = message_composed + "<color=" + font_color + ">"

        message_composed = message_composed + self.textentry_chat_message.get_text()

        if font_color != "#FFFFFF":
            message_composed = message_composed + "</color>"
        if self.scalebutton_text_size.get_value() != 14:
            message_composed = message_composed + "</size>"
        if self.button_italic.get_active():
            message_composed = message_composed + "</i>"

        dicty = dict()
        dicty['Identifier'] = 1
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = "say " + message_composed

        self.pyrcon.send(json.dumps(dicty))
        GLib.idle_add(self.scroll_chat_to_bottom)
        self.textentry_chat_message.set_text('')

    def gtkcolor_to_web(self):
        color = self.buttoncolor_chat.get_color().to_floats()
        r = "{:0>2X}".format((round(color[0] * 255)))
        g = "{:0>2X}".format((round(color[1] * 255)))
        b = "{:0>2X}".format((round(color[2] * 255)))
        string = "#" + str(r) + str(g) + str(b)

        return string




mw = MainWindow()
Gtk.main()

