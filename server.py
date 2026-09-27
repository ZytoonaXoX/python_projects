import socket

ip=input("enter your server ip : ").strip()
port=int(input("enter server port : "))

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((ip,port))

server.listen(5)
print(f"server listen in {ip}:{port}")

client,address=server.accept()
print(f"client: {address} connect ")

data=client.recv(4096)
print("Receved : ",data.decode())

client.close()
server.close()
