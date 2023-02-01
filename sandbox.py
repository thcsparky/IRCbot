import irc
import socket
import requests

strdir = dir(requests)
for x in strdir:
    if x.find('__') > -1:
        break
    print(x)