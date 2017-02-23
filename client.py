from socket import *
serverName = "localhost";
serverPort = 8080
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
#sentence = raw_input("Input lowercase sentence:")
#clientSocket.send("GET http://www.google.com/ HTTP/1.1");
modifiedSentence = clientSocket.recv(4096)
print ("From Server:", modifiedSentence);
#clientSocket.close()