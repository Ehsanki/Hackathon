import socket
import threading
import time
import random
import struct
from colorama import Fore, Back, Style



numClients=0
clients=[]
stop=False


def sendto_pack_msg(port):
    type=0x02
    broadsocketMessage=struct.pack('!IBH',0xabcddcba,type,port)
    return broadsocketMessage

def run_Server(server_port, broadcast_port):
    BroadCastSocket = create_broadcast_socket()
    message = sendto_pack_msg(4999)
    ServerSocket = socket.socket()  # get instance a
    ServerSocket.bind(("", server_port))  # bind host address and port together
    ServerSocket.setblocking(False)  # set socket to non-blocking mode
    ServerSocket.listen(5)  # configure how many client the server can listen simultaneously

   
    while True: 
        stop_broadcast = time.time() + 10
        while time.time() < stop_broadcast:
            BroadCastSocket.sendto(message, ('<broadcast>', broadcast_port))
            
            try:
              
                conn, address = ServerSocket.accept() # accept new connection
                clients.append(conn)
                print("Connection from: " + str(address) )
    
                global numClients
                numClients+=1
              

                if(numClients==2):
                    startGame()
                    print("all aggain")
                    
                

            except socket.error:    # for timeout exceptions since we call accept from a non-blocking socket
                print(end='\r')
            time.sleep(1)
       

def create_broadcast_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)   # broadcast socket
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(0.2)   # Set a timeout so the socket does not block indefinitely when trying to receive data.
    return udp_socket



def startGame():
    global clients
    global numClients
    global stop
    
    print( Fore.GREEN+Style.BRIGHT+"Game Started"+Style.RESET_ALL)
 
    for i in clients:
        i.send(b"Welcome To Game !!!")
    
  
    player1=clients[0]
    player2=clients[1]

       



    stop =False
    while(not stop):
      
        try:
            data = player1.recv(1024).decode('utf-8')  # receive response #leeeh?
            print("wow player 1  pressed !!! "+ data)
        except ConnectionResetError:
            print("Client Disconnected Game over ")
            break
        except:
             pass

        try:
             data = player2.recv(1024).decode('utf-8')  # receive response
             print("wow player 1  pressed !!! "+ data)

        except ConnectionResetError:
            player1.close()
            print("Player 2 Disconnected Game over ")
            break
        except:
             pass


    
    print("Game Ends , discoenneting Clients !")
    for i in clients:
        i.close()

    numClients=0
    clients=[]
    
 

    


if __name__ == '__main__':
    serverPort = 4999  # initiate port no above 1024
    broadcastPort = 13117  # this should be the port in the end when we test it
    msg ="Server started,listening on IP address : " 
    msg +=socket.gethostbyname(socket.gethostname())
    print(msg)
    run_Server(serverPort, broadcastPort)



   
