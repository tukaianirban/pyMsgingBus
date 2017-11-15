import collections
import traceback, json
import threading, time
import pickle, random

from utils.WebSocketClientQ import WebSocketClientQ
from datetime import datetime

def main():
	
	q = collections.deque()
	
	# open a websocket connection to the server
	ws = WebSocketClientQ(q, 'ec2-18-196-1-187.eu-central-1.compute.amazonaws.com', 8081, '/')
	threading.Thread(target=ws.run_forever).start()

	# register for a skill in the server
	while not ws.emitText(json.dumps({'register':'skill1'})):	
		print ("recvr_client: trying to register in server...")
		time.sleep(1)
	print ("recvr_client: registered in server")
	
	# enable buffering in server
	while not ws.emitText(json.dumps({'buffering':True})):
		print ("recvr_client: trying to enable buffering in the server")
		time.sleep(1)
	print ("recvr_client: Enabled buffering in server")

	# enable fastpush in server
	while not ws.emitText(json.dumps({'fastpush':True})):
		print ("recvr_client: trying to enable fastpush in the server")
		time.sleep(1)
	print ("recvr_client: Enabled fastpush in server")

	c=0
	prev=0
	reqtype=0
	while True:
		if len(q)>0:
			try:
				d1 = datetime.now()
				di = json.loads((q.popleft()).decode())
				sk=di['skill']
				#payload=di['payload']
				p=datetime.strptime(di['payload'], '%Y-%m-%d %H:%M:%S.%f')
				#print ("recvr_client: Payload type received =", type(payload))
				diff = (d1-p).total_seconds()*1000
				print ("recvr_client: diff = ", diff, " increment=", (diff-prev))
				prev=diff
				
				ws.emitText(json.dumps({'ack':''}))
				#print ("recvr_client: Sent ACK to messaging server")
				#reqtype = 0
				#if reqtype==0:
				#	print ("recvr_client: Sending ACK to messaging server")
				#else:
				#	print ("recvr_client: Sending GET to messaging server")
			except:
				print ("recvr_client: Exception in calculating diff. Trace:", traceback.format_exc())
				
#		if c%10==0:
#			try:
#				if reqtype==0:
#					ws.emitText(json.dumps({'ack':''}))
#					#print ("recvr_client: Sent ACK to messaging server")
#				else:
#					ws.emitText(json.dumps({'get':''}))
#					#print ("recvr_client: Sent GET to messaging server")
#					
#			except:
#				print ("recvr_client: Exception sending ACK request. Trace:", traceback.format_exc())
		
		c+=1
		time.sleep(0.001)

if __name__=="__main__":
	main()
