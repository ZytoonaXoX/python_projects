import socket

def tcp_connection(target_host,target_port,payload):
    # socket opject
    tcp=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #socket connect 
    tcp.connect((target_host,target_port))
    
    tcp.sendall(f"{payload}\r\n".encode())

    response=tcp.recv(4096)
    print(response)


def udp_connection(target_host,target_port,payload):

    udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    udp.sendto(f"{payload}".encode(),(target_host,target_port))

    data=udp.recvfrom(4096)
    print(data)

connection_type=input("connection type (TCP , UDP) : ").lower()

target_host=input("target_host : ").strip()
target_port=int(input("port : "))
payload=input("payload : ")

if connection_type == "tcp" :
    tcp_connection(target_host,target_port,payload)

elif connection_type == "udp":
     udp_connection(target_host,target_port,payload) 

else :
    print("choose the connection protocol")

