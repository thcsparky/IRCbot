import os
import socket
import threading 
import time 
import requests
sentConfigYet = 0

def recvMessage(sock):
    global sentConfigYet

    while True:
        try:
            get = sock.recv(4985)
            if not get:
                break
            print(get.decode())
            time.sleep(1)
            ##I guess i'll put the bot processing in here.
            bget = get.decode()

            if bget.find('PING') > -1:
                bping = bget.replace('PING :', '')
                print('ping msg: ' + bping)
                sendOneMessage(sock, 'PONG :' + bping)

            ##Send configuration after receiving this message if not sent yet:
            if sentConfigYet == 0:
                sencfgRecvVariable = ':'
                
                if bget.find(sencfgRecvVariable) > -1:
                    sendCfg(sock)
                    sentConfigYet = 1

        except Exception as e:
            print(e)


def openConnection(sock, server, port):
    hostuple = ((server, int(port)))
    try: ##double try layer, annoying i know. 
        sock.connect(hostuple)
    except Exception as e:
        print('socket error: \n')
        print(e)
        return

    print('Connected')
    return(sock.getpeername())

def sendOneMessage(sock, msg):
    #IRC commands must end with '\r\n'. Formatting accordingly:
    formatMSG = msg + '\r\n'
    msgsend = formatMSG.encode()
    print(msgsend) ##debug opt
    sock.sendall(msgsend)

def sendCfg(sock):
    ##will just reload the config file..
    fileio = open(os.getcwd() + '/config3.txt')
    filedat = fileio.read()
    fileio.close()
    messages = filedat.splitlines()
    print('sending configuration')

    for index, sendline in enumerate(messages):
        if index > 2:
            print(sendline)
            sendOneMessage(sock, sendline)  #send command with the ending newline.

def promptUser(sock):
    help = 'quit - closes the socket and quits the program\n'
    help += 'msg - (who) (what)\n'
    help += 'type and hit enter to send\n'

    print(help)
    a = input()
    if a.startswith('quit'):
        quit()

    if a.find('msg ') > -1:
        b = a.split('msg ')[1]
        msguser = b.split(' ')[0]
        msgmsg = b.split(' ')[1]
        sendOneMessage(sock, 'PRIVMSG ' + msguser + ' ' + msgmsg)
    
    sendOneMessage(sock, a)
    promptUser(sock) ##Oddly, the recursion instead of the While: loop seemed to have fixed my socket action taken on non socket object error.

        
def main():
    try:
        getconfiguration1 = open(os.getcwd() + '/config3.txt') ##Changed this to ircd.chat for testing purposes.
        getconfiguration = getconfiguration1.read()
        getconfiglist = getconfiguration.splitlines()
        ##declare our vars
        confignick = ''
        configserver = ''
        configport = ''
        for x in getconfiglist:
            if x.find('nick: ') > -1:
                confignick = x.split('nick: ')[1]
            if x.find('server: ') > -1:
                configserver = x.split('server: ')[1]
            if x.find('port: ') > -1:
                configport = x.split('port: ')[1]
        print('User vars: ' ) 
        print(confignick)
        print(configserver)
        print(configport)

    except Exception as e:
        print('Error loading configuration. make sure you have /config.txt in this directory')
        print('Exception:\n')
        print(e)

    print('Attempting to connect:\n')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    a = openConnection(sock, configserver, configport)
    if a:
        print(a)
    else: 
        print("Couldn't connect\n")

    ##start the listening for data thread.
    thread1 = threading.Thread(target=recvMessage, args=(sock,))
    thread1.start()

    time.sleep(1) ##Give the socket a chance to get our connection properly established.
    promptUser(sock)

    
if __name__ == "__main__":
    main()