from websocket_server import WebsocketServer
from datetime import datetime
import time

class Websocket_Server():
    def __init__(self):
        self.server = WebsocketServer(port=5555, host="localhost")
    
    #接続
    def new_client(self, client, server):
        counter = 0
        while True:
            time.sleep(10)
            server.send_message_to_all("TEST DATA : " + str(counter))
            counter += 1
    
    #切断
    def client_left(self, client, server):
        print("client({}) disconnected".format(client['id']))

    #メッセージ受信
    def message_received(self, client, server, message):
        pass

    def run(self):
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received) 
        self.server.run_forever()


ws_server = Websocket_Server()
ws_server.run()