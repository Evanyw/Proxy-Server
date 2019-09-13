Proxy Server
1. IP address: xxx.xxx.xxx.xxx
   port number: 8888

2. Data structure of caching
Use list for caching files, like the following code segment:
---------------------------------
for i in range(0, len(buff)):
    tmpFile.write(buff[i])
    tcpCliSock.send(buff[i])

3. Bonus parts
a) Step 1: make the code structure more robust
   Add main function: create the server socket, bind it to the specified port and start listening to requests
   Add proxy_server function: create the connection socket for handling client requests both for cached or non-cached files

b) Step 4: multi-threading
   import threading module, and use a thread for each client and use the main thread for listening for new clients. When one client connects, the main thread creates a new thread.
----------------------------------
count += 1
threading = Thread(name = 'proxy', target = proxy_server, args = (tcpCliSock, addr, count))
threading.start()
		
