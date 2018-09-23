# Dependencies:
# sudo -H pip install ws4py

from ws4py.client.threadedclient import WebSocketClient
import json
import sys


class ConnectionStatus:
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3

class PyRCON(WebSocketClient):
    event_connected_cb = None
    event_closed_cb = None
    event_message_cb = None

    def opened(self):
        if self.event_connected_cb:
            self.event_connected_cb()
        self.send("{'Identifier':1, 'Message':'chat.tail','Name':'WebRcon'}")
        pass

    def closed(self, code, reason=None):
        if self.event_closed_cb:
            self.event_closed_cb()

        print("Closed down", code, reason)

    def received_message(self, m):
        if self.event_message_cb:
            self.event_message_cb(m)
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

