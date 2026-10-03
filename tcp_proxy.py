import socket
import threading
proxy_ip="192.168.1.8" # edit this to make user add ip for his proxy 
proxy_port=8888 # edit this to make user add port 

client_ip=str(input("client ip : ")).strip()
client_port=int(input("clint port : "))

proxy=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # this socket to listen to client 
proxy.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #it used to make connection to server 



def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
            print(f"data: {data}")
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        dst.close()   


proxy.bind((proxy_ip,proxy_port))

proxy.listen(5) #listen(5) mean it make lsiten in port , number 5 mean how many connection can wait to connect 
print (f"proxy listening on  {proxy_ip}:{proxy_port}")

client_socket,client_address=proxy.accept() #client_address >> ('ip',port) | .accept() it accept a connection 
print(f"connect from : {client_address}")
server_socket.connect((client_ip,client_port))

thread_1=threading.Thread(target=forward,args=(client_socket,server_socket))
thread_2=threading.Thread(target=forward,args=(server_socket,client_socket))

thread_1.start()
thread_2.start()

thread_1.join()
thread_2.join()


