import threading, websocket
import pickle, json, time, traceback

from pyee import EventEmitter
import collections

class WebSocketClientQ(object):

        def __init__(self, equeue, host, port, path):
                self.host = host or ""
                self.port = port or 0
                self.path = path or "/"
                self.equeue = equeue
                self.create_url()
                self.client = self.create_client()


        def create_url(self):
                self.url = "ws://"+self.host+":"+str(self.port)+self.path

        def create_client(self):
                return websocket.WebSocketApp(self.url,
                        on_message=self.on_message, on_open=self.on_open,
                        on_close=self.on_close, on_error=self.on_error)

        def on_open(self, ws):
                print ("WebSocketClient: Connected")

        def on_close(self, ws):
                ws.close()
		#self.client.close()
                print ("WebSocketClient: Closed")

        def on_error(self, ws, err):
                try:
                        self.client.close()
                except:
                        print ("WebSocketClient: Exception on WebSocket client close() on error")
                self.client = self.create_client()

        def on_message(self, ws, msg):
                #print ("WebSocketClient: Recvd message from server. Dump=", msg)
                #print ("WebSocketClient: Recvd message type=", type(msg))
                self.equeue.append(msg)
                #print ("WebSocketClient: Type of ws = ", type(ws))

        def emitBinary(self, msg):
                if (not self.client or not self.client.sock or not self.client.sock.connected):
                        return False
                else:
#                       data = dest.encode() + pickle.dumps(msg)
                        self.client.send(msg, websocket.ABNF.OPCODE_BINARY)
                        return True

        def emitText(self, msg):
                try:
                       if (not self.client or not self.client.sock or not self.client.sock.connected):
                                return False
                       else:
                                self.client.send(msg, websocket.ABNF.OPCODE_TEXT)
                                return True
                except:
                        print ("WebSocketClient: Exception in emitText. Trace:", traceback.format_exc())
                        return False

        def run_forever(self):
                self.client.run_forever()

        def close(self):
                self.client.close()

        def run(self):
                self.run_forever()

        def join(self):
                self.client.close()

