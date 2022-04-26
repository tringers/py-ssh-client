import socket
import sys


class Py_ssh_client:

    def __init__(self, host="", port=22):
        self.HOST = host
        self.PORT = port

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))
            data = self.recieve(s)
            print("{}".format(data))

            while True:
                user_input = input()
                s.sendall(bytes(user_input, 'utf-8'))
                if user_input.lower() == "exit":
                    s.close()
                    break

                data = s.recv(1024)

                if data.decode("utf-8") == "auth error":
                    s.close()
                    sys.exit("Authentifizierung fehlgeschlagen.")

                if not data:
                    sys.exit()

                print(f"{data!r}:")

    def send(self, sock, message):
        sock.sendall(bytes("{}".format(message), "utf-8"))

    def recieve(self, sock):
        data = sock.recv(1024)
        output = str(data.decode("utf-8"))
        output = output.replace("\n", "")
        return output
