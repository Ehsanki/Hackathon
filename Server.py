import socket
import threading
import time
import random
import struct
import select

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED='\033[31m'
    GREEN='\033[32m'
    redBack='\033[30;107m'

numClients=0 # Max 2 
clients=[] # (connection , Team Name )  
stop=False
lock = threading.Lock()

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
    ServerSocket.listen(0)  # configure how many client the server can listen simultaneously


    while True: 
        stop_broadcast = time.time() + 10
        while time.time() < stop_broadcast:
            BroadCastSocket.sendto(message, ('<broadcast>', broadcast_port)) # invitaions send
            
            try:

                conn, address = ServerSocket.accept() # accept new connection
                

                print("Connection from: " + str(address) )
    
                global numClients
                numClients+=1
                lock.acquire()
                clientConnected(conn)
                lock.release()
                if(numClients==2):
                    startGame()
                    print("REBRODCAST ? [y\\n]")
                    x=input()
                    if(x=="n"):
                        print(bcolors.WARNING+"Server Terminated Successfully "+bcolors.ENDC)
                        ServerSocket.close()
                        exit(0)
                    print(bcolors.OKBLUE+"re Brodcasting invitations..."+bcolors.ENDC)
                  
                    time.sleep(5)
                    
    
            except socket.error: 
                
                   # for timeout exceptions since we call accept from a non-blocking socket
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

    
def generateQuestion():
    
    option=random.randint(0,1)

    if(option==1): ##SUBSTRACT QUESTION
        
        fNum=random.randint(0,9999)
        answer=random.randint(0,9)
        question="How Much is "+str(fNum)+" - "+str(fNum-answer)
        return question,answer


    else: 
        fNum=random.randint(0,5)
        sNum=random.randint(0,4)
        question="How Much is "+str(fNum)+" + "+str(sNum)
        return question,fNum+sNum


def startGame():
    global clients
    global numClients
    global stop
    print(bcolors.WARNING+"Clients In Game Mode"+bcolors.ENDC)
    
    for i in clients:
        i[0].send(b"Welcome to Quick Maths.\n Game will start after 10 seconds")
       


    time.sleep(10) # Wait 10 second until sending questions! TODO UNCOMMENT
    
  
    player1=clients[0][0] 
    player2=clients[1][0]
    

    msg="Player 1: "+clients[0][1]+"\nPlayer 2: "+clients[1][1]+"\n==\nPlease answer the following question as fast as you can:"

    question,answer=generateQuestion() ## GETRANDOMQUESTION()->(question,Answer)

    for i in clients:
        i[0].send(msg.encode("utf-8"))
       
    

    
    for i in clients: ## Send Question To Clients 
        i[0].send(question.encode("utf-8"))
    
    print(bcolors.GREEN+"Question sent -> "+bcolors.ENDC+question)
    print("answer is ---> "+str(answer))


    TimeUp = time.time() + 60
    DrawFlag=True
    while(time.time()<TimeUp):
      
        try:
            data = player1.recv(1024).decode('utf-8')  # receive response 
            print("player 1 Answered !!! "+str(data))

            if data==str(answer):
                WonLostMsgSend(player1,player2)
            else:
                WonLostMsgSend(player2,player1)


            return
            

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
            
            
            if data==str(answer):
                WonLostMsgSend(player2,player1)
            else:
                WonLostMsgSend(player1,player2)

            return
            
        except ConnectionResetError:
            player1.close()
            print("Player 2  Disconnected Game over ")
            
            numClients=0
            clients=[]
            return


            
        except:## DIDNT ANSWER YET 
            pass
    
  

    print("Game Ends , discoenneting Clients !")        
    if(DrawFlag):
        drawMsg=bcolors.WARNING+"Time's Up , DRAW !"+bcolors.ENDC
        for i in clients:
            i[0].send(drawMsg.encode())

    
    
    for i in clients:
        i[0].close()

    numClients=0
    clients=[]
    

def WonLostMsgSend(playerWon,playerLost):
    wonMsg="CONGRATS CHAPMION YOU"+bcolors.GREEN+bcolors.BOLD+" WON !!!!!!\n"+bcolors.ENDC
    lostMsg="BETTER LUCK NEXT TIME TIME YOU HAVE"+bcolors.RED +bcolors.BOLD+  " Lost!\n "+bcolors.ENDC

    playerLost.send(lostMsg.encode())
    playerWon.send(wonMsg.encode())
    playerWon.close()
    playerLost.close()

    global numClients
    global clients
    numClients=0
    clients=[]





if __name__ == '__main__':
    serverPort = 4999  # initiate port no above 1024
    broadcastPort = 13117  # this should be the port in the end when we test it
    msg ="Server started,listening on IP address : " 
    msg +=socket.gethostbyname(socket.gethostname())
    print(bcolors.redBack+bcolors.BOLD +msg+bcolors.ENDC)
 
    run_Server(serverPort, broadcastPort)



   
