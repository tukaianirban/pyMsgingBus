# pyQMsgBus

A websocket-based client-server mechanism for message passing bus between independant geographically distributed systems. The messaging bus works using skills embedded in the incoming packets. Each client system is required to implement the "client" WebSocketClientQ class to connect into the messaging bus. The client system is then able to register to listen for new skills, deregister from existing skills, request buffering of messages in server, request fast-push of messages, using the same WebSocketClientQ object. 
The server acts with acknowledgements. Each client system after being sent a packet must send in an ACK if it wants to receive the next packet in its queue. If it wants to fetch the same packet again (provided buffering is enabled by the client), it needs to send a GET to the server.
The server recognizes difference between packets requesting some change in features(control), and data payload packets (forwarding) by the formatting of the packets. 
Control packets can be :
	a. register / de-register from skills
	b. buffering turn on/off
	c. fast-push turn on/off
	d. ACK for last packet
	e. GET of last buffered packet


Features available in the server:
1. Register / De-Register to skills : Each client object listens to a certain skill. When another client sends a packet with the interesting skill in it, the registered client(s) will get a copy of the packet. There can be multiple senders and receivers of the same skill. Each receiver needs to be pre-registered in the server for the skill(s) it wants to listen to.
Packet (in websocket.ABNF.OPCODE_TEXT) format : {'register':'skill1'}

2. Buffering of packets : Each client object is allocated a separate queue in the server. By default, packets are not buffered in the server. If buffering is enabled by a client, then the last packet sent to the client is buffered in the server. The client can choose to fetch this message again by sending a GET message to the server.
 If the client wants to get the next packet from the server, it should send an ACK message to the server.
Packet (in websocket.ABNF.OPCODE_TEXT) format :
a. To enable buffering :- {'buffering' : True}
a. To disable buffering :- {'buffering' : False}

3. Fast-Push : By default, a packet in the queue will be sent to the client only after the client system has sent an ACK to the server while the packet is present in the queue. To enable the server to immediately send the next packet to the client (even though one may not be in queue right now), as and when the packet arrives in the queue, the client system must enable Fast-Push.
Packet (in websocket.ABNF.OPCODE_TEXT) format :
a. To enable fast-push :- {'fastpush' : True}
a. To disable fast-push :- {'fastpush' : False}

The WebSocketClientQ object works by :
1. To send packets use either emitText() or emitBinary() depending on what format the packets needs to be transmitted in.
2. Received packets are queued into a collections.deque() object.

Code example : To send a data packet through the messaging system:

\# create a collections de-que structure; initialize and start off thread to maintain the websocket
q = collections.deque()
ws = WebSocketClientQ(q, '<SERVER_IP_ADDRESS>', SERVER_PORT_NUMBER, '/')
threading.Thread(target=ws.run_forever).start()

#wait a few seconds to check the websocket connection is up
while not (ws.client and ws.client.sock and ws.client.sock.connected):
    time.sleep(1)

#send a data payload with skill 'skill1' to the server
pkt_raw = json.dumps({'skill':'skill1', 'payload':str(datetime.now())})
ws.emitBinary(pkt_raw.encode())

Here the client will send 1 message packet to the server with skill = 'skill1' ; the payload being a string object.



Code example : To subscribe to a skill and receive relevant packets from the messaging system:

 #create a collections de-que structure; initialize and start off thread to maintain the websocket
q = collections.deque()
ws = WebSocketClientQ(q, '<SERVER_IP_ADDRESS>', <SERVER_PORT_NUMBER>, '/')
threading.Thread(target=ws.run_forever).start()
 #register for a skill in the server
while not ws.emitText(json.dumps({'register':'skill1'})):
        print ("recvr_client: trying to register in server...")
        time.sleep(1)

while True:
        if len(q)>0:
                #received packet must be decoded from unicode bytes to string format
                di = json.loads((q.popleft()).decode())
                sk=di['skill']
                payload=di['payload']
                ws.emitText(json.dumps({'ack':''}))
        except:
                pass
        #release some cpu cycles
        time.sleep(0.001)

Here, the client will subscribe to listen to skill 'skill1'




The client should be configured to use :
1. Binary mode of sending data to server : to pass payload packets
Example code:

q = collections.deque()
ws = WebSocketClientQ(q, "<myservername>", <port_number>, '/')
threading.Thread(target=ws.run_forever).start()
pkt_raw = json.dumps({'skill':'skill1', 'payload':str(datetime.now())})
ws.emitBinary(pkt_raw.encode())



2. Text mode of sending data to server : to set options for features to be used on the server
Example code:

q = collections.deque()
ws = WebSocketClientQ(q, "<myservername>", <port_number>, '/')
threading.Thread(target=ws.run_forever).start()
while not ws.emitText(json.dumps({'buffering':True})):
	print ("recvr_client: trying to enable buffering in the server")
    time.sleep(1)
