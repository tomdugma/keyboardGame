from Client import Client
from Server import Server


def main():
    server = Server()
    server.begin()
    client = Client("Hapoel Bikini Bottom")
    client.begin_client()


if __name__ == '__main__':
    main()