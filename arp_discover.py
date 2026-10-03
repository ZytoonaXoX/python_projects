from scapy.all import ARP,Ether,srp 


network="192.168.1.0/24"

packet=Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)

response,w=srp(packet,timeout=2,verbose=False)

for sent,received in response:
	print(f"{received.psrc:13}--> {received.hwsrc}")
