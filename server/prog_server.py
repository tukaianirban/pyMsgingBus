from websockserver import websockserver
import tornado.ioloop
import getopt, sys

def main():

        options,_ = getopt.getopt(sys.argv[1:], 'h:p:')

        host,port = 'localhost',8081
        if len(options)>0:
	        for opt,arg in options:
                        if opt=='-h':
                                host=arg
                        elif opt=='-p':
                                port=arg

        handlerslist=[(r'/ws', websockserver), (r"/", websockserver)]

        print ("Starting server to listen on",host,":",port)
        application = tornado.web.Application(handlerslist)
        application.listen(port,host)
        tornado.ioloop.IOLoop.instance().start()

if __name__=='__main__':
        main()

