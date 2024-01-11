import socket
import select
from random import randint
import random
game_flag = 0#是不是已經在遊戲中
this_time_end = 0#遊戲結束要告訴大家，所以message會不一樣特別分出來
this_time_start = 0
HEADER_LENGTH = 10

IP = '172.20.10.13'
PORT = 9999
import random
QA = [" "," "]


def generate():#用來生成遊戲答案
    random_num = random.randint(1,128)
    print(random_num)
    f = open("guess.txt",'r',encoding="utf-8")
    line = ""
    for i in range(1,random_num+1):
      line = f.readline()
    f.close()
    seperate = line.split(" - ")
    seperate2 = seperate[1].split("\n")
    QA[0] = seperate[0]
    QA[1] = seperate2[0]


def answering(mess):##檢測使用者是不是在猜題
  your_guess = 0
  if len(mess)!=3:
    return False
  if mess[0] == "答":
    if mess[1] == ":":
      return True
  return False

def judge(mess):#用來判斷答題結果
  if mess[2] == QA[1]:
    return 0
  elif mess[2] == '解':

    return 1
  else:
    return 2


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}
#scores
scores = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):

    try:
        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False
        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())
        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False

while True:
    
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    print_score = False

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            scores[client_socket] = 0

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del scores[notified_socket]
                del clients[notified_socket]
                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]
            if message is True:
                print(f'Received message from {clients[client_socket]["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            if (message["data"].decode("utf-8") == "score"):
                print_score = True

            if(message["data"].decode("utf-8") == "game"):
              if game_flag ==0:
                this_time_start = 1
                generate()
                print(f"game start, Q:{QA[0]}, A:{QA[1]} ")
                game_flag = 1

            if answering(message["data"].decode("utf-8")):
                result = judge(message["data"].decode("utf-8"))
                if result == 1:
                    this_time_end = 1
                    game_flag = 0
                    print("有人答題了，此提結束")
                if result == 0:
                    this_time_end = 1
                    game_flag = 0
                    print("有人答題了，此提結束")
                if result == 2:
                    this_time_end = 1


            if this_time_end == 1:
              for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:
                    your_point = judge(message["data"].decode("utf-8"))
                    tell_them = ""
                    if your_point == 0:
                      tell_them = "恭喜 {} 答對了".format(user['data'].decode('utf-8'))
                      #scores[client_socket] += 1
                      #print(str(client_socket) + str(scores[client_socket]))
                    elif your_point == 1:
                      tell_them = f"猜答案是:{QA[1]}"
                    elif your_point == 2:
                      tell_them = f"猜錯了,繼續"
                    message2 = message["data"].decode("utf-8") + " -----> " + tell_them
                    message2 = message2.encode('utf-8')
                    message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(user['header'] + user['data'] + message2_header + message2 )
                elif client_socket == notified_socket:
                    your_point = judge(message["data"].decode("utf-8"))
                    tell_them = ""
                    if your_point == 0:
                      tell_them = "恭喜 {} 答對了".format(user['data'].decode('utf-8'))
                      scores[client_socket] += 1
                      #print(str(client_socket)+str(scores[client_socket]))
                      for key, value in scores.items():
                          print(str(key) + str(value))
                    elif your_point == 1:
                      tell_them = f"答案是:{QA[1]}"
                    elif your_point == 2:
                      tell_them = f"猜錯了,繼續"
                      this_time_end = 0
                    message2 = message["data"].decode("utf-8") + " -----> " + tell_them
                    message2 = message2.encode('utf-8')
                    message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(user['header'] + user['data'] + message2_header + message2 )


            else :
              # Iterate over connected clients and broadcast message
              for client_socket in clients:

                  # But don't sent it to sender
                  if client_socket != notified_socket:
                      if game_flag == 0:

                      # Send user and message (both with their headers)
                      # We are reusing here message header sent by sender, and saved username header send by user when he connected
                          client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                      if game_flag == 1 :
                        if answering(message["data"].decode("utf-8")):
                          your_point = judge(message["data"].decode("utf-8"))
                          tell_them = ""
                          if your_point == 0:
                              tell_them = "恭喜 {} 答對了".format(user['data'].decode('utf-8'))
                              scores[client_socket] += 1
                              for key, value in scores.items():
                                print(str(key) + str(value))
                          elif your_point == 1:
                              tell_them = f"答案是:{QA[1]}"
                          elif your_point == 2:
                              tell_them = f"猜錯了,繼續"
                          message2 = message["data"].decode("utf-8") + " -----> " + tell_them
                          message2 = message2.encode('utf-8')
                          message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                          client_socket.send(user['header'] + user['data'] + message2_header + message2 )
                        elif this_time_start == 0:
                          client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                        else:
                          message2 = message["data"].decode("utf-8") + " -----> " + QA[0]
                          message2 = message2.encode('utf-8')
                          message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                          client_socket.send(user['header'] + user['data'] + message2_header + message2 )

                  elif (client_socket == notified_socket) & (this_time_start == 1) :
                      message2 = message["data"].decode("utf-8") + " -----> " + QA[0]
                      message2 = message2.encode('utf-8')
                      message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                      client_socket.send(user['header'] + user['data'] + message2_header + message2 )

            if(print_score == True):
                for client_socket in clients:
                    message2 = ' '.encode('utf-8')
                    for key, value in scores.items():
                        message2_1 = "{}------分數為{}，".format(clients[key]['data'].decode("utf-8"), value)
                        message2_1 = message2_1.encode('utf-8')
                        message2 += message2_1

                    message2_header = f"{len(message2):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(user['header'] + user['data'] + message2_header + message2)


            if this_time_end:
                  QA[0] = " "
                  QA[1] = " "
            this_time_end = 0
            this_time_start = 0
    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]