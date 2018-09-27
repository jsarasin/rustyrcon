# Dependencies:
# sudo -H pip install ws4py
# sudo apt-get install glib

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

from ws4py.exc import HandshakeError
from ws4py.client.threadedclient import WebSocketClient
import json
import sys


class ConnectionStatus:
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

class PyRCON(WebSocketClient):
    class ProtocolNotUnderstood(Exception):
        pass


    def __init__(self, *args, **kargs):
        self.event_connected_cb = None
        self.event_closed_cb = None
        self.event_message_cb = None
        self.event_chat_cb = None
        self.event_console_cb = None

        self.chat_message_identifier = 250
        self.console_cmd_cb_identifier = 500
        self.console_cmd_outstanding_cb = {}

        super(PyRCON, self).__init__(*args, **kargs)

    def opened(self):
        if self.event_connected_cb:
            self.event_connected_cb()
        # self.send("{'Identifier':1, 'Message':'chat.tail','Name':'WebRcon'}")
        pass

    def closed(self, code, reason=None):
        if self.event_closed_cb:
            self.event_closed_cb(code, reason)

    def received_message(self, message):
        dicty = json.loads(message.data.decode("utf-8"))

        identifier = dicty['Identifier']
        mtype = dicty['Type']
        stacktrace = dicty['Stacktrace']
        #
        # print(" --- Received Message --- ")
        # print("Identifier: %s  Type: %s  Stacktrace:[%s]  Message:" % (identifier, mtype, stacktrace))
        # print(dicty['Message'].replace("\n", "\\n").replace("\r", "\\r")[0:100])
        # print()

        sys.stdout.flush()

        # The user of the library has marked a message to return data to a call back, this is such a message
        if identifier in self.console_cmd_outstanding_cb:
            GLib.idle_add(self.console_cmd_outstanding_cb[identifier], dicty['Message'])
            sys.stdout.flush()
            return

        # Chat messages
        if identifier == -1:
            if mtype != "Chat":
                raise self.ProtocolNotUnderstood("Chat message has identifier that isn't -1")

            if self.event_chat_cb != None:
                self.event_chat_cb(dicty['Message'])
                return

        if mtype == "Generic":
            if self.event_console_cb != None:
                if 'Time' in dicty:
                    mtime = dicty['Time']
                else:
                    mtime = None
                self.event_console_cb(dicty['Message'], mtime)
                return


        # Unhandled message types
        if self.event_message_cb:
            self.event_message_cb(message)
        sys.stdout.flush()

    def send_chat_message(self, message, text_size=14, font_color="#FFFFFF", italic=False):
        message_composed = ""
        if italic:
            message_composed = message_composed + "<i>"
        if text_size != 14:
            message_composed = message_composed + "<size=" + str(int(text_size)) + ">"
        if font_color != "#FFFFFF":
            message_composed = message_composed + "<color=" + font_color + ">"

        message_composed = message_composed + message

        if font_color != "#FFFFFF":
            message_composed = message_composed + "</color>"
        if text_size != 14:
            message_composed = message_composed + "</size>"
        if italic:
            message_composed = message_composed + "</i>"

        dicty = dict()
        dicty['Identifier'] = 1
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = "say " + message_composed

        self.send(json.dumps(dicty))

    def send_console_callback(self, cmd, callback):
        dicty = dict()
        dicty['Identifier'] = self.console_cmd_cb_identifier
        dicty['Name'] = "WebRcon"
        dicty['Type'] = "Chat"
        dicty['Message'] = cmd

        self.console_cmd_outstanding_cb[self.console_cmd_cb_identifier] = callback

        self.send(json.dumps(dicty))
        self.console_cmd_cb_identifier = self.console_cmd_cb_identifier + 1
