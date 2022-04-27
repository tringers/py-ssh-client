import unittest
import socket

from py_ssh_client import Py_ssh_client

class ServerTests(unittest.TestCase):

    server = Py_ssh_client()

    def testServerAuth(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect(("", 22))

            data = self.server.recieve(s)
            self.assertEqual("User:", data)
            self.server.send(s, "timo")
            data = self.server.recieve(s)
            self.assertEqual("Password:", data)
            self.server.send(s, "timo")
            data = self.server.recieve(s)
            self.assertEqual("timo@Server:", data)
            self.server.send(s, "ls -la")
            data = self.server.recieve(s)
            print(data)
            self.assertIn("total", data)
            self.server.send(s, "exit")
            data = self.server.recieve(s)
            print(data)

            s.close()