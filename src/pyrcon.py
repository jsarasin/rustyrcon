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

class PyRCON:
    def __init__(self):
        self.status = ConnectionStatus.CLOSED
        self.address = None
        self.port = None
        self.password = None


    def connect(self, address, port, pword):
        self.address = address
        self.port = port
        self.password = pword



class DummyClient(WebSocketClient):
    def opened(self):
        # """
        #   "Message": "{
        #   'Message': 'hello',
        #   'UserId': 0,
        #   'Username': 'SERVER',
        #   'Color': '#eee',
        #   'Time': 1537168254
        # }",
        # """

        self.send("{'Identifier':1, 'Message':'say hello','Name':'WebRcon'}")
        # self.send("{'Identifier':1, 'Message':'chat.tail 10','Name':'WebRcon'}")
        pass

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, m):
        print(m)
        sys.stdout.flush()


if __name__ == '__main__':
    try:
        password = "1404817"
        ws = DummyClient('ws://108.61.239.97:28018/' + password, protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()

    except KeyboardInterrupt:
        ws.close()