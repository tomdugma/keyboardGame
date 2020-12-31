import random
import threading
import time
from _thread import start_new_thread
from socket import *
import traceback


class Server:

    def __init__(self):
        ''' trying to recieve the ip address'''
        try:
            self.server_ip = gethostbyname(gethostname())
        except Exception as e:
            print('wasnt able to get the ip')
            print(e)
            return
        self.broadcast_port = 13147
        self.server_port = 2065
        self.udp_socket = 0
        self.tcp_socket = 0
        self.players_on_server = ["p1", "p2", "p3"]
        self.total_kb = 0
        self.players_scores = [0] * 4
        # try to connect sockets
        try:
            self.udp_socket = socket(AF_INET, SOCK_DGRAM)
            if self.udp_socket == 0:
                print('wasnt able to connect udp socket')
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            if self.tcp_socket == 0:
                print('wasnt able to connect tcp socket')
        except Exception as e:
            print("wasnt able to connect sockets, error below: \n")
            print(e)
            return

        self.game_is_on = False


    def begin(self):
        '''  trying to bind the sockets, if fail to do so, probably its already bound '''
        try:
            self.udp_socket.bind((self.server_ip, self.server_port))
            self.tcp_socket.bind((self.server_ip, self.server_port))
        except Exception as e:
            print('wasnt able to bind the sockets, error below: \n')
            print(e)
        thread = threading.Thread(target=self.connect_TCP)
        thread.start()

    def connect_TCP(self):

        print("Server started, listening on IP address " + str(self.server_ip))
        threading.Thread(target=self.broadcast_details).start()
        self.tcp_socket.listen()
        ''' listen and waiting for clients ...'''
        while True:
            ''' client accepted '''
            connection, addr = self.tcp_socket.accept()

            ''' critical section, dont let other threads in'''
            mutex = threading.Lock()

            mutex.acquire()
            if len(self.players_on_server) >= 2:
                random.shuffle(self.players_on_server)

            mutex.release()
            # new thread
            start_new_thread(self.handler, (connection,))

    def handler(self, socket):
        ''' check socket value '''
        if socket is None:
            print('handler receive none value in socket')

        ''' convert the name we receive from client to str'''
        name = str(socket.recv(1024), 'utf-8')

        ''' check if name received properly '''

        self.set_player(name)

        while not self.check_if_game_started():
            time.sleep(0.5)

        ''' if we pass the while loop, means game is starting !'''
        if not self.send_Welcome_Message(socket):
            return

        index = self.players_on_server.index(name)

        ''' starting game '''
        start_time = time.time()
        while True:
            if time.time() - start_time > 10:
                break

            data = socket.recv(1024)
            ''' receiving click bits'''
            if not data:
                continue

            '''updating score when data recieved'''
            self.players_scores[index] += 1

        index_of_winner, team_one_score, team_two_score = self.choose_winner()

        # Game Over send end Message
        try:
            groups = ["Group 1", "Group 2"]
            massage = "Game over!\nGroup 1 typed in " + str(team_one_score) + " characters. Group 2 typed in "+str(team_two_score) +" characters.\n"
            massage = massage + str(groups[index_of_winner]) + " wins!\n\n" + "Congratulations to the winners: \n==\n" + self.players_on_server[0 + index_of_winner*2] + "\n" + self.players_on_server[1 + index_of_winner*2] +"\n"
            socket.send(bytes(massage, encoding='utf8'))
            print(self.players_scores)
            self.game_is_on = False
        except:
            traceback.print_exc()

        time.sleep(0.5)
        print("Game over, sending out offer requests...")
        self.players_on_server = ["p1", "p2", "p3"]
        self.players_scores = [0]*4
        if self.game_is_on:
            self.game_is_on = False
        socket.close()

    def init_server(self):
        ''' here we create server socket '''
        server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        server.settimeout(0.2)
        if server.getsockname() is None:
            print('issue with server address after init')
        server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        server.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        return server

    def broadcast_details(self):
        ''' send details to clients '''
        while True:
                if not self.game_is_on:
                    try:
                        begin_messure = time.time()
                        server = self.init_server()
                        try:
                            self.send_brodcast(begin_messure, server)
                        except:
                            pass
                    except Exception as e:
                        print('wasnt able to collect broadcasts and send to the clients, error below: \n')
                        print(e)

    def set_player(self, player):
        self.players_on_server += [player]

    def check_if_game_started(self):
        ''' checks if the game started '''
        if len(self.players_on_server) <= 1:
            if len(self.players_on_server) == 1:
                print('waiting alone for match up')
            self.game_is_on = False
            return False
        else:
            self.game_is_on = True
            return True

    def send_Welcome_Message(self, server):
        ''' sending welcome massage to the players ! '''
        if server is None:
            print('unable to send msgs, server is none')
            return False
        else:
            massage = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n" + str(
                self.players_on_server[0]) + "\n" + self.players_on_server[1] \
                      + "\n" + "Group 2: \n==\n" + str(self.players_on_server[2]) + "\n" + str(
                self.players_on_server[3]) + "\n" + \
                      "\nStart pressing keys on your keyboard as fast as you can!!\n"
            try:
                server.send(bytes(massage, encoding='utf8'))
                return True
            except Exception as e:
                print('wasnt able to send the massage, error below: \n')
                print(e)
                return False

    def choose_winner(self):
        ''' check and return whose the winner '''
        total_score = 0
        for player in self.players_scores:
            total_score += player
        team_one = self.players_scores[0] + self.players_scores[1]
        team_two = total_score - team_one
        index_of_winner = 0
        if team_one == team_two:
            print("oh god, its a tie, what are the odds ?")
        else:
            if team_one < team_two:
                index_of_winner = 1

        return index_of_winner, team_one, team_two

    def send_brodcast(self, start_time, server):

        ''' sens a broadcast messegs every 10 seconds '''
        broadcasts_msgs = bytes.fromhex("feedbeef") + bytes.fromhex("02") + self.server_port.to_bytes(2, byteorder='big')
        if broadcasts_msgs is None:
            print('was`nt able to convert broad`s msgs')

        while time.time() - start_time < 10:
            try:
                server.sendto(broadcasts_msgs, ('<broadcast>', self.broadcast_port))
                time.sleep(1)
            except Exception as e:
                print('was`nt able to convert broad`s msgs, error below \n')
                print(e)
