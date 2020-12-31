import socket
import threading
from socket import *
import getch


class Client():
    def __init__(self, badass_team_name):
        self.TEAM_ROCKET = badass_team_name
        self.client_ip = gethostbyname(gethostname())
        if self.client_ip is None:
            print('error at receiving ip at Client init !')
        self.my_statistics = []
        self.broad_port = 13147
        self.UDP_SOCKET = socket(AF_INET, SOCK_DGRAM)

    def begin_client(self):
        #######################################
        # BEGIN THREADING
        #######################################
        print("BEGIN CLIENT")
        thread = threading.Thread(target=self.begin_on_listenning)
        thread.start()

    def begin_on_listenning(self):
        port_tcp = None
        print("Client started - listening for broadcasts...")
        #######################################
        # HERE: client begin accepting udp msg`s
        #######################################
        try:
            self.UDP_SOCKET.bind(('', self.broad_port))
        except:
            self.begin_on_listenning()
        #######################################
        # HERE: trying to find the udp port
        #       if we went out of the try block,
        #       means we were`nt able to connect to the udp socket.
        #######################################
        try:
            # receives the msg
            msg = self.UDP_SOCKET.recvfrom(1024)
            if msg is None:
                print('issue accord with {} msg'.format(msg))
            elif msg[0] is None:
                print('invalid port_msg')
            else:
                port_tcp = msg[0][5:]

            the_tcp_port_we_found = int.from_bytes(port_tcp, byteorder='big', signed=False)
            print(the_tcp_port_we_found)
            if the_tcp_port_we_found is None:
                print('error accord while cast tcp port from bytes')
            else:
                self.connecting_to_TCP_server(the_tcp_port_we_found)

        except Exception as e:
            print('error accord while tried to connect to udp socket')

    def connecting_to_TCP_server(self, tcp_port):
        # print(port_tcp)
        # print(type(port_tcp))

        #######################################
        # HERE: we creating a TCP connection.
        #######################################
        try:
            # creating client socket
            our_client_socket = socket(AF_INET, SOCK_STREAM)
            print("Client connecting to server port: {}".format(tcp_port))

            # if creating client socked failed ?
            if our_client_socket is None:
                print('value recieved is {} '.format(our_client_socket))

            # connecting to server and send him the chars.
            our_client_socket.connect((self.client_ip, tcp_port))

            #######################################
            # HERE: sending our badass team name to server socket !
            #######################################

            # send name in bytes
            our_client_socket.send(bytes(self.TEAM_ROCKET, encoding='utf8'))

            # is something happend to the client socket during sending ?
            if our_client_socket is None:
                print('value recieved is {} '.format(our_client_socket))

            # data we get from the server
            respond_we_get_from_the_server = str(our_client_socket.recv(1024), 'utf-8')

            # check if respond is None ?
            if respond_we_get_from_the_server is None:
                print('invalid massage recieved ! {}'.format(respond_we_get_from_the_server))

            print(respond_we_get_from_the_server)
            our_client_socket.settimeout(0.0)

            # after connecting to server, we are ready to send chars as bytes !
            while True:
                try:
                    # here we recieve massages from the server !
                    self.recieve_from_server(client_socket=our_client_socket)
                    data = our_client_socket.recv(1024)
                    # check if data received correctly.
                    if data is None:
                        print('error accord recieving the data from the server !')
                    # cast the data
                    data = str(data, 'utf-8')
                    print(data)
                    break
                except:
                    try:
                        # catching keyboard clicks and seding it to the server with getch libary.
                        curr_ch = getch.getch()
                        if curr_ch is None:
                            print('invalid return from getch')
                        # sending clicks to server as bytes.
                        our_client_socket.send(bytes(curr_ch,encoding = 'utf8'))
                    except:
                        print('wasnt able to catch key board events -> TRY AGIAN !')
                        continue
            our_client_socket.close()

        # outer try block, if reach here no tcp connection created.
        except Exception as e:
            print('wasnt able to create a tcp connection, check connection to tcp func at client')
            print(e)


def begin():
    client = Client("tom_N_dani")
    if client is None:
        print('issue with client at init')
    client.begin_client()


if __name__ == '__main__':
    begin()
