Motivation:
===============================================

* Learn the basics of socket programming.
* Understand the functionality of a Proxy Server.
* Explore basic structures of HTTP messages.

Project Design:
===============================================
* Created a multithreaded web proxy server that supports GET method and implements
  caching.
    Step 1: Create a ServerSocket object to monitor the port 8080 or other ports from input
    Step 2: If receive client request, create a new thread to process the request. Also a 
            new socket is created for the connection with client;
    Step 3: The ServerSocket object continues monitoring.
    Step 4: Parse the request line and headers sent by the client.
    Step 5: If the new request matches a past one, the proxy server will directly return the 
            cached data.If not then perform Step 6.
    Step 6: Send request to “real” Web server. A HTTP response including the requested file will be
            received at the proxy server.
    Step 7: The thread reads in the instream, get the file name and the content;
    Step 8: Forward the content to the Client.
    Step 9: Close the socket, and end the thread.
* Created a separate TCP connection for each request/response pair. A separate thread
  handles each of these connections. There will also be a main thread, in which the server listens for
  clients.