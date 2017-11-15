import tornado.websocket
import tornado.web
import tornado.ioloop
import collections
import sys, traceback, pickle, json

from datetime import datetime
from pyee import EventEmitter
from multiprocessing.pool import ThreadPool

eventhandler = EventEmitter()

class websockserver(tornado.websocket.WebSocketHandler):

	def __init__(self,app, req, **kwargs):
		tornado.websocket.WebSocketHandler.__init__(self, app, req, **kwargs)
#		print ("websockethandler: New constructor spawned...")
		self.msgq = collections.deque()
		self.msgqlen = 0
		self.flagbuffer=False
		self.lastbuffered=False
		self.flagfastpush=False
		self.skillset=list()

	def open(self):
		print ("websockethandler: New connection opened")


	def on_message(self, msg):
		if isinstance(msg, bytes):		# data plane packets
			try:
				#print ("server: received bytes type data")
				pkt = json.loads(msg.decode())
				#skill=pkt['skill']
				eventhandler.emit(pkt['skill'], msg)
				#print ("server: Received new message=",pkt,"with skill=",skill)
			except:
				print ("server: Exception processing byte-type data packet. Trace:", traceback.format_exc())
		elif isinstance(msg, str):
			#print ("server: received str type data")
			try:
				di = json.loads(msg)
				if ('register' in di.keys()):
					# client registers to listen for a certain skill
					# define a handler for this skill
					# handler will buffer the received packet, until the client requests for the next packet
			
					regskill=di['register']
					print ("server: registered handler for skill=", regskill)
					@eventhandler.on(regskill)		
					def evthandler(msg):
						if self.msgqlen==0 and self.flagfastpush:
							self.write_message(msg, binary=True)
							if self.flagbuffer:
								self.msgq.append(msg)
								self.msgqlen+=1
								self.lastbuffered=True
						else:
							self.msgq.append(msg)
							self.msgqlen+=1
							self.lastbuffered=True
							
						#print ("server: enqueued new packet received from EventEmitter")
					self.skillset.append((regskill, evthandler))
				elif ('buffering' in di.keys()):
					# client sends in a packet with {buffering: True/False} depending on 
					# whether it wants queuing bus to buffer last sent packets or not
					try:
						f=di['buffering']
						if isinstance(f,bool):
							self.flagbuffer=f
					except:
						#print("server: Exception parsing out buffering key from received packet. Trace=", traceback.format_exc())
						pass

				elif ('fastpush' in di.keys()):
					# client sets FASTPUSH to send ACK only for the last packet it processed, and no more ACKs afterwards
					# prevents excess signalling due to incoming ACKs

					try:
						f=di['fastpush']
						if isinstance(f, bool):
							self.flagfastpush=f
							print ("server: Enabled fastpush for client")
					except:
						print("server: Exception processing fastpush signal from client. Trace:", traceback.format_exc())
						pass

				elif ('get' in di.keys()):
					# client sends a 'GET' packet when it wants to get a copy of the last packet sent to it.
					# buffer keeps a copy of the packet sent to the client

					try:					
						# exception will raise only if local queue is empty; hence can accord delay in Exception raise
						if self.msgqlen>0:
							t = self.msgq.popleft()
							self.write_message(t, binary=True)
							if self.flagbuffer:				# buffer the packet only if buffering flag is set
								self.msgq.appendleft(t)
								self.lastbuffered=True
								#print ("server: copy of topmost item sent to client; preserved topmost item")
					except IndexError:
						#print ("server: No more items to pop from queue. Trace:", traceback.format_exc())
						pass
					except:
						#print ("server: Exception in popping left from the local queue. Trace:", traceback.format_exc())
						pass
				elif ('ack' in di.keys()):
					# client sends an 'ACK' packet when it wants to fetch the next packet in the message queue buffer
					# buffer drops the last packet that was sent to the client and sends the next packet sent to the client
	
					try:
						if self.msgqlen>0:
							if self.lastbuffered:			# if the topmost item is a buffered item, drop it
								t=self.msgq.popleft()			
								self.msgqlen-=1
								self.lastbuffered=False		# always assign , rather than if stmt to check for flagbuffering

							if self.msgqlen>0:			# if there are still more messages in buffer, then :
								t=self.msgq.popleft()
								self.write_message(t, binary=True)
								if self.flagbuffer:
									self.msgq.appendleft(t)
								else:
									self.msgqlen-=1
								self.lastbuffered = self.flagbuffer
					except:
						#print ("server: Exception handling ack packet from client. Trace=", traceback.format_exc())
						pass
			except:
				print ("Exception handling incoming data. Trace:", traceback.format_exc())
		else:
			print ("server: other data type received")
			return


#		t = datetime.now()
#		try:	
#			delta = (t-m).total_seconds()*1000
#			print ("Delay=",delta,"msec")
#		except:
#			print ("Exception processing recvd msg")

	def on_close(self):
		for sk,fn in self.skillset:
			eventhandler.remove_listener(sk, fn)
			print ("websockethandler: removed handler for skill=",sk)
		print ("websockhandler: Connection closed down")

	def check_origin(self, o):
		return True

