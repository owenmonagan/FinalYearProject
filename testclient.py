import socket




message= "Dublin"
ip = 'localhost'
port = 3200



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, port))
try:
    sock.sendall(message.encode("ascii"))
    response = sock.recv(1024).decode("ascii")
    print ("Received: {}".format(response))
finally:
    sock.close()
