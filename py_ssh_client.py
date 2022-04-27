import socket
import sys
import rsa
import hashlib
from Crypto.Cipher import AES

class Py_ssh_client:

    def __init__(self, host="", port=22):
        self.generateKeys()
        self.HOST = host
        self.PORT = port
        (self.publicKey, self.privateKey, self.sharedKey) = self.loadKeys()
        self.recievedPublicKey = None
        self.authenticated = False

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            sock.connect((self.HOST, self.PORT))

            self.publicKeyTransaction(sock)
            self.recieveSharedKey(sock)

            while True:

                data = self.recieve(sock)

                if data == "auth error":
                    sock.close()
                    sys.exit("Authentifizierung fehlgeschlagen.")

                print("{}".format(data))

                if not self.authenticated:
                    self.authentifizierung(sock, data)
                else:
                    self.commands(sock)

                if not data:
                    sys.exit()

    def authentifizierung(self, sock, data):

        if data == "User:":
            self.userInput(sock)
        elif data == "Password:":
            self.userPassword(sock)

    def publicKeyTransaction(self, sock):

        recivedPublicKey = self.recievePublicKey(sock)
        recivedPublicKey = str(recivedPublicKey).split("(")[1].split(",")
        recivedPublicKey[1] = recivedPublicKey[1].split(")")[0].strip()

        keyN = int(recivedPublicKey[0])
        keyE = int(recivedPublicKey[1])

        self.recievedPublicKey = rsa.PublicKey(keyN, keyE)

        self.sendPublicKey(sock)

    def userInput(self, sock):

        user_input = input()
        self.send(sock, user_input)

        if user_input.lower() == "exit":
            sock.close()
            sys.exit("User beendet die Verbindung.")

    def commands(self, sock):
        self.userInput(sock)
        data = self.recieve(sock)
        print("{}".format(data.replace("\n", "")))

    def userPassword(self, sock):

        user_input = input()
        password_hash = hashlib.sha512(user_input.encode("utf-8")).hexdigest()
        self.authenticated = True
        self.send(sock, password_hash)

    def sendPublicKey(self, sock):
        sock.sendall(bytes("{}".format(self.publicKey), "utf-8"))

    def recievePublicKey(self, sock):
        data = sock.recv(1024)
        return data


    def recieveSharedKey(self, sock):

        data = sock.recv(1024).decode("utf-8")
        #data = rsa.decrypt(data, self.privateKey)
        self.sharedKey = data


    def send(self, sock, message):

        sender = AES.new("self.sharedKey12", AES.MODE_ECB)
        #message = sender.encrypt(message)
        sock.sendall(bytes("{}".format(message), "utf-8"))

    def recieve(self, sock):

        data = sock.recv(1024).decode("utf-8")
        reciever = AES.new("self.sharedKey12", AES.MODE_ECB)
        #data = reciever.decrypt(data)
        output = str(data).lstrip("b").strip('\'')
        output = output.strip('\n')
        return output

    def generateKeys(self):
        (publicKey, privateKey) = rsa.newkeys(1024)
        with open('keys/publicKey.pem', 'wb') as p:
            p.write(publicKey.save_pkcs1('PEM'))
        with open('keys/privateKey.pem', 'wb') as p:
            p.write(privateKey.save_pkcs1('PEM'))

    def loadKeys(self):
        with open('keys/publicKey.pem', 'rb') as p:
            publicKey = rsa.PublicKey.load_pkcs1(p.read())
        with open('keys/privateKey.pem', 'rb') as p:
            privateKey = rsa.PrivateKey.load_pkcs1(p.read())
        with open('keys/sharedKey', 'rb') as p:
            sharedKey = p.read() * 16
        return publicKey, privateKey, sharedKey
