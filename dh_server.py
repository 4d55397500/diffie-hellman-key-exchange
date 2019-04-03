import cmath
import random
import time
from Crypto.Cipher import AES
import socket
import json

N = 32452867


server_vocabulary = ["That's very interesting, please tell me more",
                     "I'm only a computer, I don't have much to say",
                     "I have secrets on the Mueller investigation to share with you"]


def calc_exp(x):
    return cmath.exp(2j * cmath.pi * x / N)


def start_server():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 8089))
    s.listen(5)
    while True:
        c, addr = s.accept()
        print("connection requested from {}".format(addr[1]))
        c.send(bytes("""
        
        Hello Alice, this is Bob. 
        
        Beginning Diffie-Hellman key exchange. We will operate 
        with the cyclic group of order {}. That's no secret.
        
        Please provide your first computation in json format
        with json keys 'alice_i' and 'alice_j' for re/im components,
        and I will do similarly.
        
        """.format(N), "UTF-8"))
        b = random.randint(0, 100)  # private to bob
        x_bob = calc_exp(b)  # not private
        while True:
            try:
                c.send(bytes(json.dumps({"bob_i": x_bob.real, "bob_j": x_bob.imag}), "UTF-8"))
                js = c.recv(1024).decode('utf-8')
                d = json.loads(js)
                x_alice = complex(d['alice_i'], d['alice_j'])
                print("Read {} from alice".format(x_alice))
                x2 = x_alice ** b  # bob's second calculation
                computed_key = round((N * cmath.log(x2) / (2j * cmath.pi)).real)
                print("\033[1;31;40m Computed shared key: {}".format(computed_key))
                break
            except:
                c.send(bytes("""
                Error parsing. Please send again
                """, "UTF-8"))

        # convert key to a 16 byte string
        # hack extension, not a secure key
        extended_key = (str(computed_key) * (int(16 / len(str(computed_key))) + 1))[:16]
        dec_suite = AES.new(extended_key, AES.MODE_ECB)
        enc = AES.new(extended_key, AES.MODE_ECB)
        while True:
            time.sleep(0.5)
            client_msg = c.recv(1024)
            if len(client_msg) > 0:
                dec_client_msg = dec_suite.decrypt(client_msg)
                print("Received from Alice: \n\tencrypted: {} \n\tdecrypted: {}".format(client_msg, dec_client_msg))
                msg = server_vocabulary[random.randint(0, 2)]
                msg = msg + ' ' * (16 - (len(msg) % 16))
                enc_msg = enc.encrypt(msg)
                c.send(enc_msg)
        c.close()


start_server()



