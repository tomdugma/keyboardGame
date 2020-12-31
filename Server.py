import random
import threading
import time
from _thread import start_new_thread
from socket import *
import traceback


class Server:
    def __init__(self):
        self.TEAMS_TOTAL_SCORE = None
        self.udp_s = socket(AF_INET, SOCK_DGRAM)
        self.tcp_s = socket(AF_INET, SOCK_STREAM)
        self.server_IP = gethostbyname(gethostname())
        if len(self.server_IP) == 0:
            print('issue with server ip at init')
        self.broad_port = 13147
        self.server_port = 2065
        self.players = []
        self.TEAMS_TOTAL_SCORE=[0, 0]
        self.score_to_add = [0, 0, 0, 0]

        self.team_names = ["Group 1", "Group 2"]
        self.game_on = False

    def BindServer(self):
        try:
            self.udp_s.bind((self.server_IP, self.server_port))
            self.tcp_s.bind((self.server_IP, self.server_port))
            self.ThreadStarter()
        except:
            traceback.print_exc()

    def ThreadStarter(self):
        try:
            thread = threading.Thread(target=self.StartTcpServer)
            thread.start()
        except:
            traceback.print_exc()

    def StartTcpServer(self):
        client = None
        print("Server started, listening on IP address " + str(self.server_IP))
        try:
            threading.Thread(target=self.Brodcast).start()
        except:
            traceback.print_exc()

        self.tcp_s.listen()
        while True:
            try:
                client, address = self.tcp_s.accept()
            except:
                traceback.print_exc()

            lock = threading.Lock()
            lock.acquire()

            if len(self.players) >= 2:
                if lock is not None:
                    random.shuffle(self.players)

            lock.release()

            try:
                start_new_thread(self.client_handling, (client,))
            except:
                traceback.print_exc()

    def client_handling(self, s):
        team_name = None
        data = None
        try:
            team_name = str(s.recv(1024), 'utf-8')
        except:
            traceback.print_exc()

        self.players += [team_name]
        if self.players is not None:
            while not self.game_on:
                if len(self.players) >= 2:
                    self.game_on = True
                else:
                    time.sleep(0.5)

        try:
            s.send(bytes(self.StartGameMsg(), encoding='utf8'))
        except:
            traceback.print_exc()

        player_index = self.players.index(team_name)

        # Listen for packets for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                data = s.recv(1024)
            except:
                traceback.print_exc()
            if not data:
                continue
            self.score_to_add[player_index] += 1
        #######################################
        # ADD SCORE !
        #######################################
        if self.score_to_add[0] is not None and self.score_to_add[1] is not None:
            self.TEAMS_TOTAL_SCORE[0] = self.score_to_add[0] + self.score_to_add[1]
        if self.score_to_add[2] is not None and self.score_to_add[3] is not None:
            self.TEAMS_TOTAL_SCORE[1] = self.score_to_add[2] + self.score_to_add[3]

        try:
            if self.TEAMS_TOTAL_SCORE[0] < self.TEAMS_TOTAL_SCORE[1]:
                s.send(bytes(self.GameOverMsg(1), encoding='utf8'))
            else:
                s.send(bytes(self.GameOverMsg(0), encoding='utf8'))
        except:
            traceback.print_exc()

        self.game_on = False
        s.close()

    def StartGameMsg(self):
        return "Welcome to Keyboard Spamming Battle Royale.\n" + "Group 1:\n==\n" + f"{self.players[0]}\n{self.players[1]}\n" + "Group 2:\n==\n" + f"{self.players[2]}\n{self.players[3]}\n" + "Start pressing keys on your keyboard as fast as you can!!\n"

    def GameOverMsg(self, winner_team_index):
        return "Game over!\n" \
               f"Group 1 typed in {self.TEAMS_TOTAL_SCORE[0]} characters. Group 2 typed in {self.TEAMS_TOTAL_SCORE[1]} characters.\n" \
               f"{self.team_names[winner_team_index]} wins!\n==\n" \
               f"Congratulations to the winners:\n==\n" \
               f"{self.players[0 + winner_team_index * 2]}\n{self.players[1 + winner_team_index * 2]}\n"

    def Brodcast(self):
        server = None
        while True:
            if not self.game_on:
                try:
                    server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
                    server.settimeout(0.2)
                    if server is None:
                        print('fatal error accord with server, CHECK BROADCAST !')
                    server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                    server.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
                except:
                    traceback.print_exc()

                count = 0
                while count < 10:
                    try:
                        server.sendto(
                            bytes.fromhex("feedbeef") + bytes.fromhex("02") + self.server_port.to_bytes(2,
                                                                                                        byteorder='big'),
                            ('<broadcast>', self.broad_port))
                    except:
                        traceback.print_exc()
                    time.sleep(1)
                    count += 1


def StartServer():
    try:
        server = Server()
        server.BindServer()
    except:
        traceback.print_exc()


if __name__ == '__main__':
    StartServer()
