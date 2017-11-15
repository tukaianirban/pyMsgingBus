import traceback, json, time
import collections, threading, pickle

from datetime import datetime
from utils.WebSocketClientQ import WebSocketClientQ

def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code"""

	if isinstance(obj, datetime):
		return obj.isoformat()
	raise TypeError ("Type %s not serializable" % type(obj))

def main():

	q = collections.deque()
	ws = WebSocketClientQ(q, 'ec2-18-196-1-187.eu-central-1.compute.amazonaws.com', 8081, '/')
	threading.Thread(target=ws.run_forever).start()

	#wait a few seconds to check the websocket connection is up
	while not (ws.client and ws.client.sock and ws.client.sock.connected):
		time.sleep(1)

	for i in range(100):
		pkt_raw = json.dumps({'skill':'skill1', 'payload':str(datetime.now())})
		ws.emitBinary(pkt_raw.encode())
		print ("sender_client: emitted a probe")
		time.sleep(0.08)
	print ("sender_client: finished sending probes")



if __name__=="__main__":
	main()
