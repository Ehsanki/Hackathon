import socket
import threading
import time
import random
import struct
import select


numClients=0
clients=[] # (connection , Team Name )  
stop=False


def sendto_pack_msg(port):
    type=0x2
    broadsocketMessage=struct.pack('IBH',0xabcddcba,type,port)
    return broadsocketMessage

def run_Server(server_port, broadcast_port):
    BroadCastSocket = create_broadcast_socket()
    message = sendto_pack_msg(4999)
    ServerSocket = socket.socket()  # get instance a
    ServerSocket.bind(("", server_port))  # bind host address and port together
    ServerSocket.setblocking(False)  # set socket to non-blocking mode
    ServerSocket.listen(1)  # configure how many client the server can listen simultaneously


    while True: 
        stop_broadcast = time.time() + 10
        while time.time() < stop_broadcast:
            BroadCastSocket.sendto(message, ('<broadcast>', broadcast_port)) # invitaions send
            
            try:
            
                conn, address = ServerSocket.accept() # accept new connection
                print("Connection from: " + str(address) )
    
                global numClients
                numClients+=1

                clientConnected(conn)

                if(numClients==2):
                    startGame()
                    print("re Brodcasting invitations...")
                    time.sleep(2)
                    
    
            except socket.error:    # for timeout exceptions since we call accept from a non-blocking socket
                print(end='\r')
            time.sleep(1)
       

def create_broadcast_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)   # broadcast socket
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(0.2)   # Set a timeout so the socket does not block indefinitely when trying to receive data.
    return udp_socket

def clientConnected(sock):
    global clients
    
    try: ## GET CLIENT NAME 
        teamName=sock.recv(1024).decode('utf-8') 
        clients.append((sock,teamName))

    except:
        sock.send(b"Could Not receive Team Name")
        clients.append((sock,"No Name"))
    
    global numClients

    if(numClients==1):
        sock.send(b"Waiting Second Player to join ...")

    


def startGame():
    global clients
    global numClients
    global stop
    print("Clients In Game Mode")
    
    for i in clients:
        i[0].send(b"Welcome to Quick Maths.\n Game will start after 10 seconds")

    #time.sleep(10) # Wait 10 second until sending questions! TODO UNCOMMENT
    
  
    player1=clients[0][0] 
    player2=clients[1][0]
    

    msg="Player 1: "+clients[0][1]+"\nPlayer 2: "+clients[1][1]+"\n==\nPlease answer the following question as fast as you can:"

    question="How Much is 2 + 2 ?" ## GETRANDOMQUESTION()->(question,Answer)

    for i in clients:
        i[0].send(msg.encode("utf-8"))
    

    
    for i in clients: ## Send Question To Clients 
        i[0].send(question.encode("utf-8"))
    

    TimeUp = time.time() + 10
    DrawFlag=True
    while(time.time()<TimeUp):
      
        try:
            data = player1.recv(1024).decode('utf-8')  # receive response #leeeh?
            if data=="4":
                player1.send(b"CONGRATS CHAPMION YOU HAVE WON!!!!!!!!!")
                player2.send(b"BETTER LUCK NEXT TIME TIME YOU HAVE LOST LOSER ! ")
            ## IF WIN SEND SOMETHING

            DrawFlag=False
            break

        except ConnectionResetError:
            print("Player 1  Disconnected Game over ")
            player2.close()
            numClients=0
            clients=[]
            return
        except: ## DIDNT ANSWER YET 
            pass

        try:
            data = player2.recv(1024).decode('utf-8')  # receive response
            print("wow player 2  pressed !!! "+ data)
            ## IF WIN SEND SOMETHING
            if data=="4":
                player2.send(b"CONGRATS CHAPMION YOU HAVE WON!!!!!!!!!")
                player1.send(b"BETTER LUCK NEXT TIME TIME YOU HAVE LOST LOSER ! ")
            DrawFlag=False
            break


        except ConnectionResetError:
            player1.close()
            print("Player 2  Disconnected Game over ")
            player2.close()
            numClients=0
            clients=[]
            return


            
        except:## DIDNT ANSWER YET 
            pass
    
    # NEED TO CHECK
    """
    th1=threading.Thread(target=empty_socket,args=(player1,))
    th2=threading.Thread(target=empty_socket,args=(player2,)) 

    th1.start()
    th2.start()

    th1.join()
    th2.join()
    """



    print("Game Ends , discoenneting Clients !")        
    if(DrawFlag):
        for i in clients:
            i[0].send(b"Time's Up , DRAW !")

    
    
    for i in clients:
        i[0].close()

    numClients=0
    clients=[]
    
 

def empty_socket(sock):
    ""
    "remove the data present on the socket"
    ""
    while True:
        try :
            sock.recv(1024)
        except :
            break


if __name__ == '__main__':
    serverPort = 4999  # initiate port no above 1024
    broadcastPort = 13117  # this should be the port in the end when we test it
    msg ="Server started,listening on IP address : " 
    msg +=socket.gethostbyname(socket.gethostname())
    print(msg)
    run_Server(serverPort, broadcastPort)



   
