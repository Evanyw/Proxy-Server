# -*- coding: utf-8 -*-
from socket import *
import sys
import time
from threading import *

def main():
    if len(sys.argv) <= 1:
        print 'Usage: "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address of the Proxy Server'
        sys.exit(2)

    # Create a server socket, bind it to a port and start listening
    tcpSerSock = socket(AF_INET, SOCK_STREAM)

    # Fill in start.
    tcpSerPort = 8888
    tcpSerip = "192.168.1.6"
    #tcpSerSock.bind(('', tcpSerPort))
    tcpSerSock.bind((tcpSerip, tcpSerPort))
    tcpSerSock.listen(1)
    # Fill in end.

    time_record = {}
    count = 0
    while True:
        # Start receiving data from the client
        print 'Ready to serve...'
        tcpCliSock, addr = tcpSerSock.accept()
        print 'Received a connection from: ', addr
        count += 1
        threading = Thread(name = 'proxy', target = proxy_server, args = (tcpCliSock, addr, count))
        threading.start()
    tcpSerSock.close()
    
def proxy_server(tcpCliSock, addr, count):
    print('Request %d from %s'%(count,addr))
    message = tcpCliSock.recv(1024)

    # Extract the filename from the given message
    #print message.split()[1]
    filename = message.split()[1].partition("/")[2]
    fileExist = "false"
    filetouse = "/" + filename
    try:
        # Check whether the file exists in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = "true"
        print 'File Exists!'

        for item in outputdata:
            if item.startswith("Date"): 
                print(item)
                time = item[6::]
                print(time)

        #connect to web server, check if being modified
        cachesock = socket(AF_INET, SOCK_STREAM)
        hostn = filename.replace("www.","",1)
        hostip = gethostbyname(hostn)
        cachesock.connect((hostip,80))

        cacheobj = cachesock.makefile('r', 0)
        cacheobj.write("GET "+"http://" + filename + " HTTP/1.0\n" + "If-Modified-Since: " + time + "\n\n")
        cachefile = cacheobj.readlines()
        cachesock.close()

        for item in cachefile:
            #'304' Not Modified, send the requested file
            if '304' in item:
                print(item)
                tcpCliSock.send("HTTP/1.0 200 OK\r\n")
                tcpCliSock.send("Content-Type:text/html\r\n")
                for i in range(0, len(outputdata)):
                    tcpCliSock.send(outputdata[i])
                print 'Read from cahce'
            else:
                fileExist = 'false'
                print 'Modified! Being updated'
                raise IOError

        # Error handling for file not found in cache
    except IOError:
        print 'File Exist: ', fileExist
        if fileExist == "false":
            # Create a socket on the proxyserver
            print 'Creating socket on proxyserver'
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)
            print 'Host Name: ', hostn

            try:
                # Connect to the socket to port 80
                c.connect((hostn, 80))
                print 'Socket connected to port 80 of the host'

                # Create a temporary file on this socket and ask port 80
                # for the file requested by the client 
                fileobj = c.makefile('r', 0)
                fileobj.write("GET " + "http://" + filename + " HTTP/1.0\n\n")
                print "GET " + "http://" + filename + " HTTP/1.0\n"

                # Read the response into buffer
                buff = fileobj.readlines() 

                #cache_time = time.strftime('%a, %d %h %Y %H:%M:%S GMT')
                #time_record[filename] = cache_time
                #print time_record[filename]

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket
                # and the corresponding file in the cache
                tmpFile = open("./" + filename, "wb")
                for i in range(0, len(buff)):
                    tmpFile.write(buff[i])
                    tcpCliSock.send(buff[i])
                tmpFile.close()
            except:
                print 'Illegal request'

        else:
            # HTTP response message for file not found
            print 'File Not Found'
            tcpCliSock.send("<html><header></header><body><h1>404 Not Found</h1></body></html>\r\n")
            tcpCliSock.send("HTTP/1.0 404 Not Found Error\r\n")
            tcpCliSock.send("Content-Type:text/html\n")
            tcpCliSock.send("\r\n")

    # Close the socket and the server sockets 
    print('End request %d from %s'%(count,addr))
    tcpCliSock.close()

if __name__ == '__main__':
    main()