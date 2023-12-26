import json
import socket
import proxyserv

def main():
    # jsonfile = open("setting.json","r")
    # jsondata = json.load(jsonfile)
    # print(jsondata['proxyServer']['port'])
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # sock.bind(("", 9999))
    # print(sock.getsockname())
    # sock.close()
    proxyServer = proxyserv.ProxyServer()
    proxyServer.serviceStart()

if __name__ == "__main__":
    main()