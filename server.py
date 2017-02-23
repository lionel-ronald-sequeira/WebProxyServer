import thread,socket,sys,os,re,time
class ProxyServer:

    def __init__(self):
        try:
            serverPort = proxyPortNo;
            #creating proxy server socket.
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            self.serverSocket.bind(("", serverPort));
            self.serverSocket.listen(2);
            self.loggingInfo("Proxy Server hostname :127.0.0.1 and server port no :" + str(serverPort)+"\n");
            self.loggingInfo("The proxy server is ready to receive client requests \n");
            print("The proxy server is ready to receive client requests.");

        except socket.error, e:
            if self.serverSocket:
                self.serverSocket.close();
            self.loggingInfo("Failed in socket opening :"+ str(e)+"\n");
            sys.exit(1);

    def serverListening(self):
        while 1:
            #server accepting client request
            clientSocket, clientAddress= self.serverSocket.accept();
            # process each client request with a separate thread.
            thread.start_new_thread(self.processRequest, (clientSocket, clientAddress));

        self.serverSocket.close();

    # method for processing the incoming client request.
    def processRequest(self,clientSocket,clientAddress):
        #to get start time to measure RTT.
        startTime=time.time();

        clientRequest = clientSocket.recv(1024);
        clientRequestType = clientRequest.splitlines();
        datamode = 'web server';
        if len(clientRequestType)!=0:
            clientSocketDetails = socket.getaddrinfo(clientAddress[0], clientAddress[1]);
            self.loggingInfo("*******************************Client Details :**********************************\n\n"
                             + "Hostname :" + str(clientAddress[0]) + "\n"
                             + "Port :" + str(clientAddress[1]) + "\n"
                             + "Socket family :" + str(clientSocketDetails[0][0]) + "\n"
                             + "Socket type :" + str(clientSocketDetails[0][1]) + "\n"
                             + "Protocol :" + str(clientSocketDetails[0][2]) + "\n"
                             + "Timeout :" + str(clientSocket.gettimeout()) + " seconds.\n"
                             + "**********************************************************************************\n\n");

            self.loggingInfo("******Http request details for client with hostname " + str(clientAddress[0]) +
                             " and port " + str(clientAddress[1]) + "*******\n"
                             + clientRequest
                             + "Request length :" + str(len(clientRequest)) + " bytes.\n"
                             + "*******************************************************************************************\n\n");
            clientRequestType = clientRequestType[0];
            if "GET" in clientRequestType:

                # fetching url from client request.
                url = clientRequestType.split(" ")[1];

                if url.startswith("/"):
                    url = url[1:];
                webServerAddress = url.split("/")[0];

                # creating cache file name using client request url.
                cacheFileName = self.getCacheFileName(url);
                print cacheFileName;
                # to check if cache file name exists if exists get it from cache.
                if os.path.exists("./" + cacheFileName):
                    datamode="cache";
                    self.loggingInfo("Data available for the request in cache file." + "\n")
                    self.getDataFromCache(url, clientSocket);
                else:
                    datamode="web server";
                    self.loggingInfo("Data not available for the request in cache file." + "\n")
                    self.getDataFromWebServer(webServerAddress, clientSocket, url);
            else:
                self.loggingInfo("Proxy server is allowed to process GET Request only." + "\n");
                clientSocket.send("405 method not allowed.");
                clientSocket.close();
        else:
            clientSocket.close();
        endTime=time.time();
        #calculating RTT
        roundTripTime=endTime-startTime;
        self.loggingInfo("Round trip time(RTT) for client hostname "+str(clientAddress[0])+
                     " and port "+str(clientAddress[1])+" is "+str(roundTripTime)+" seconds from "+datamode+".\n");

    # method for getting data from web server.
    def getDataFromWebServer(self,webServerAddress,clientSocket,url):
        self.loggingInfo("Start getting data from web server. \n");
        portNo = 80;
        serverName = webServerAddress;
        colonpos = webServerAddress.find(":");
        if colonpos != -1:
            portNo = webServerAddress[colonpos + 1:];
            serverName = webServerAddress[:colonpos];
        tmpData = 0;
        cachedFile=0;
        clientData='';
        webSocket="";
        try:
            cacheFileName = self.getCacheFileName(url);

            webServerDetails = socket.getaddrinfo(serverName, portNo);

           # creating socket connection with web server.
            webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            webSocket.settimeout(5);
            webSocket.connect((serverName, portNo));

            self.loggingInfo("*******************************Web Server Details :**********************************\n\n"
                             + "Hostname :" + str(serverName) + "\n"
                             + "Port :" + str(portNo) + "\n"
                             + "Socket family :" + str(webServerDetails[0][0]) + "\n"
                             + "Socket type :" + str(webServerDetails[0][1]) + "\n"
                             + "Protocol :" + str(webServerDetails[0][2]) + "\n"
                             + "Timeout :" + str(webSocket.gettimeout()) + " seconds.\n"
                             + "**********************************************************************************\n\n");

            data='';
            if url.endswith("/"):
                data=url[0:len(url)-1];
            else :
                data=url[0:];
            webSocket.send(b"GET / HTTP/1.1\nHost: " + data  + "\n\n");

            while 1:
                    cachedFile = open(cacheFileName, "a");
                    # waiting for response from web server.
                    clientData = webSocket.recv(4096);
                    #print "Client Data",clientData;
                    tmpData += len(clientData);
                    cachedFile.write(clientData);
                    if len(clientData) > 0:
                        # sending data to client.
                        clientSocket.send(clientData);
                    else:
                        break;

            clientSocket.send("<body> Hostname :" + str(serverName) + "Port :" + str(portNo)
                             + "Socket family :" + str(webServerDetails[0][0])
                             + "Socket type :" + str(webServerDetails[0][1])
                             + "Protocol :" + str(webServerDetails[0][2])
                             + "Timeout :" + str(webSocket.gettimeout()) + " seconds.</body>");

            # releasing connections after data send.
            self.closeConnections(cachedFile, webSocket, clientSocket);
        except socket.error, e:
            if clientData =='':
                #if url requested is invalid.
                clientSocket.send("HTTP/1.1 404 not found \r\n");
            else :
                self.loggingInfo(" ");
            self.closeConnections(cachedFile, webSocket, clientSocket);
        self.loggingInfo("Server response length in bytes :" + str(tmpData) + "\n");
        self.loggingInfo("End of getting data from web server. \n");

    #method for getting data from cache.
    def getDataFromCache(self,url,clientSocket):
        self.loggingInfo("Start getting data from cache.\n");
        proxySocketDetails = socket.getaddrinfo("127.0.0.1", proxyPortNo);

        self.loggingInfo("*******************************Proxy Server Details :**********************************\n\n"
                         + "Hostname :" + "127.0.0.1" + "\n"
                         + "Port :" + str(proxyPortNo) + "\n"
                         + "Socket family :" + str(proxySocketDetails[0][0]) + "\n"
                         + "Socket type :" + str(proxySocketDetails[0][1]) + "\n"
                         + "Protocol :" + str(proxySocketDetails[0][2]) + "\n"
                         + "Timeout :" + str(self.serverSocket.gettimeout()) +"\n"
                         + "**********************************************************************************\n\n");

        cacheFileName = self.getCacheFileName(url);
        cachedLines="";

        #reading data from cache file.
        cachedFile=open(cacheFileName,"r",0);
        cachedLines = cachedFile.readlines();
        cachedLines = ''.join(cachedLines);

        # sending data from cached file to client.
        clientSocket.send(cachedLines+"<span>Hostname : 127.0.0.1" + "\n"
                         + "Port :" + str(proxyPortNo) + "\n"
                         + "Socket family :" + str(proxySocketDetails[0][0]) + "\n"
                         + "Socket type :" + str(proxySocketDetails[0][1]) + "\n"
                         + "Protocol :" + str(proxySocketDetails[0][2]) + "\n"
                         + "Timeout :" + str(self.serverSocket.gettimeout()) +"\n</span>");


        cachedFile.close();
        clientSocket.close();
        self.loggingInfo("Server response length in bytes :" + str(len(cachedLines)) + "\n");
        self.loggingInfo("End getting data from web cache. \n");

    #method for logging info in cache file.
    def loggingInfo(self, msg):
        logFile = open("log.txt", "a");
        logFile.write(msg);
        logFile.close();

    #method for creating cache file names.
    def getCacheFileName(self,url):
        if url.endswith("/"):
            cacheFileName=re.sub('[^a-zA-Z0-9_\.]','-',url[0:len(url)-1]);
        else:
            cacheFileName = re.sub('[^a-zA-Z0-9_\.]', '-',url);
        return cacheFileName;

    #method for logging connections.
    def closeConnections(self,cachedFile,webSocket,clientSocket):
        if cachedFile:
            cachedFile.close();
        if webSocket:
            webSocket.close();
        if clientSocket:
            clientSocket.close();

if __name__=='__main__':
        global proxyPortNo;
        proxyPortNo=8080;
        # if port set by user input from console.
        if len(sys.argv)==2 :
            proxyPortNo=int(sys.argv[1]);
        # create proxy server object.
        proxyServer=ProxyServer();
        proxyServer.serverListening();









