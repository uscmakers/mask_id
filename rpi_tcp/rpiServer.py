"""Example python3 server-side socket program using TCP from the tutorial video below.
https://www.youtube.com/watch?v=bTThyxVy7Sk&index=6&list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d
"""
import socket

def Main():
    # Replace host and port with host and port of RPi
    host = '192.168.1.219'
    port = 5000

    s = socket.socket()
    s.bind((host,port))

    print('Binded to ' + str(host) + ' ' + str(port))
    s.listen(1)
    c, addr = s.accept()
    print("Connection from: " + str(addr))
    while True:
        data = c.recv(1024).decode('utf-8')
        if not data:
            break
        print("From connected user: " + data)
        data = data.upper()
        print("Sending: " + data)
        c.send(data.encode('utf-8'))
    c.close()

if __name__ == '__main__':
    Main()
