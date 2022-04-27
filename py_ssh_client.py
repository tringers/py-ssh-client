import socket
import sys
import pyDH
import rsa

diffieHellman = pyDH.DiffieHellman()

class Py_ssh_client:

    def __init__(self, host="", port=22):
        self.generateKeys()
        self.HOST = host
        self.PORT = port
        (self.publicKey, self.privateKey) = self.loadKeys()
        self.sharedKey = None

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect((self.HOST, self.PORT))

            while True:

                recivevedpub = self.recievePublicKey(s)
                recivevedpub = str(recivevedpub).split("(")[1].split(",")
                recivevedpub[1] = recivevedpub[1].split(")")[0].strip()

                keyN = int(recivevedpub[0])
                keyE = int(recivevedpub[1])
                pub = rsa.PublicKey(keyN, keyE)

                self.sendPublicKey(s, self.publicKey)

                self.sharedKey = diffieHellman.gen_shared_key(
                    pub
                )

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

                print("{}".format(data))

    def sendPublicKey(self, sock, message):
        sock.sendall(bytes("{}".format(message), "utf-8"))

    def send(self, sock, message):
        message = rsa.encrypt(message.encode('ascii'), self.publicKey)
        self.sendPublicKey(sock, message)

    def recievePublicKey(self, sock):
        data = sock.recv(1024)
        return data

    def recieve(self, sock):
        data = sock.recv(1024)
        data = rsa.decrypt(data, self.sharedKey)
        output = str(data.decode("utf-8"))
        output = output.replace("\n", "")
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
        return publicKey, privateKey
