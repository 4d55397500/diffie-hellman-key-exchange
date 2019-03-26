import socket
import json
import cmath
import random
from Crypto.Cipher import AES

N = 32452867


def calc_exp(x):
   return cmath.exp(2j * cmath.pi * x / N)

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))

first_server_msg = clientsocket.recv(1024).decode('utf-8')
print(first_server_msg)

a = random.randint(0, 100)  # private to client
x_alice = calc_exp(a)  # not secret
clientsocket.send(bytes(json.dumps({"alice_i": x_alice.real, "alice_j": x_alice.imag}), "UTF-8"))

d = json.loads(clientsocket.recv(1024).decode('utf-8'))
x_bob = complex(d['bob_i'], d['bob_j'])
print("Read from Bob {}".format(x_bob))
x2 = x_bob ** a  # alice's second computation
computed_key = int((N * cmath.log(x2) / (2j * cmath.pi)).real)
print("\033[1;31;40m Computed shared key: {}".format(computed_key))

# convert key to a 16 byte string
extended_key = (str(computed_key) * (int(16 / len(str(computed_key))) + 1))[:16]  # hack extension, not a secure key
dec_suite = AES.new(extended_key, AES.MODE_ECB)
enc = AES.new(extended_key, AES.MODE_ECB)

while True:
   msg = input("Provide message for server:\n")
   msg = msg + ' ' * (16 - (len(msg) % 16))
   enc_msg = enc.encrypt(msg)
   assert (len(enc_msg) % 16 == 0)
   clientsocket.send(enc_msg)
   server_msg = clientsocket.recv(1024)
   if len(server_msg) > 0:
      dec_server_msg = dec_suite.decrypt(server_msg)
      print("Received from Bob: \n\tencrypted: {} \n\tdecrypted: {}".format(server_msg, dec_server_msg))

