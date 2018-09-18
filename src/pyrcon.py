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

#
#
# class DummyClient(WebSocketClient):
#     def opened(self):
#         self.send("{'Identifier':1, 'Message':'say hello','Name':'WebRcon'}")
#         pass
#
#     def closed(self, code, reason=None):
#         print("Closed down", code, reason)
#
#     def received_message(self, m):
#         print(m)
#         sys.stdout.flush()
#
#
# if __name__ == '__main__':
#     try:
#         password = "1404817"
#         ws = DummyClient('ws://108.61.239.97:28018/' + password, protocols=['http-only', 'chat'])
#         ws.connect()
#         ws.run_forever()
#
#     except KeyboardInterrupt:
#         ws.close()

# """
#   "Message": "{
#   'Message': 'hello',
#   'UserId': 0,
#   'Username': 'SERVER',
#   'Color': '#eee',
#   'Time': 1537168254
# }",
# """
# self.send("{'Identifier':1, 'Message':'say hello','Name':'WebRcon'}")
# # self.send("{'Identifier':1, 'Message':'chat.tail 10','Name':'WebRcon'}")
