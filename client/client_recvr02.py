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

	while True:
		if len(q)>0:
			try:
				d1 = datetime.now()
				di = json.loads((q.popleft()).decode())
				sk=di['skill']
				p=datetime.strptime(di['payload'], '%Y-%m-%d %H:%M:%S.%f')
				diff = (d1-p).total_seconds()*1000
				print ("recvr_client: diff = ", diff)
				
				ws.emitText(json.dumps({'ack':''}))
				#print ("recvr_client: Sent ACK to messaging server")
			except:
				print ("recvr_client: Exception in calculating diff. Trace:", traceback.format_exc())
				
		time.sleep(0.080)

if __name__=="__main__":
	main()
