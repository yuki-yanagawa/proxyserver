import socket
import signal
import threading
import json
import re

BUF_SZIE = 4096

class ProxyServer:
    def __init__(self):
        settingFile = open("setting.json","r")
        settingData = json.load(settingFile)
        self.ipaddr = settingData['proxyServer']['ipaddr']
        self.port = settingData['proxyServer']['port']
        self.websocketAPI = settingData['proxyServer']['websocketAPI']
        self.videostreamAPI = settingData['proxyServer']['videostream']

        try:
            self.servsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        except  Exception as e:
            print("Socket Created Error.....")
            return None
    
    def serviceStart(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.servsocket.bind((self.ipaddr, self.port))
        self.servsocket.listen(10)

        # address, port = self.servsocket.getsockname()
        print(" * Running on http://" + self.ipaddr + ":" + str(self.port))
        print("Press CTRL+C to quit")

        try:
            while True:
                print("accept start.....")
                clientsocket, clientaddr = self.servsocket.accept()
                data = clientsocket.recv(BUF_SZIE)
                statusLine = data.decode('UTF-8').split("\r\n")[0]
                print(clientaddr[0] + " - - " + statusLine)
                websockFlg = False
                if statusLine.split(" ")[1] in self.websocketAPI:
                    websockFlg = True
                videostreamFlg = False
                if statusLine.split(" ")[1] in self.videostreamAPI:
                    videostreamFlg = True
                data = data.decode('UTF-8').replace("Host: localhost:9999","Host: localhost:8888").encode('UTF-8')
                threading.Thread(target=handleThread,args=(clientsocket,data,statusLine,websockFlg,videostreamFlg, )).start()
        except KeyboardInterrupt as e:
            self.servsocket.close()
            print("* Service Stop http://" + self.ipaddr + ":" + str(self.port))


def handleThread(clientsocket:socket.socket, requestParamBinary, statusLine,websockFlg:bool,videostreamFlg:bool):
    forcli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        forcli.connect(createConnectDest(websockFlg))
        forcli.send(requestParamBinary)
        if videostreamFlg:
            firstReponse = searchMotionJPEGHeader(forcli)
            clientsocket.send(firstReponse)
            while True:
                tmpdata = forcli.recv(BUF_SZIE)
                clientsocket.send(tmpdata)
        elif websockFlg:
            print("<<< websocket start >>> ")
            firstResponse = searchWebSocketUpdateHeader(forcli)
            clientsocket.send(firstResponse)
            # logs pattern first action is from websocket server
            while True:
                tmpdata = forcli.recv(BUF_SZIE)
                clientsocket.send(tmpdata)
        else:
            responseData = b''
            tmpdata = forcli.recv(BUF_SZIE)
            responseStatusLine = tmpdata.decode('UTF-8').split("\r\n")[0]
            if isBadResponse(responseStatusLine):
                responseData = tmpdata
                clientsocket.send(responseData)
            else:
                # while True:
                #     responseData += tmpdata
                #     print(responseData)
                #     print("dataread start..")
                #     tmpdata = forcli.recv(BUF_SZIE)
                    # if not contentlineFlg :
                    #     contentlen = analysisContentLength(tmpdata)
                    #     if contentlen > 0:
                    #         contentlineFlg = True
                    # if contentlineFlg :
                    #     print(tmpdata)
                    #     if len(tmpdata) == contentlen:
                    #         recvEndFlg = True
                    # if count > 10:
                    #     break
                    # fromflask += tmpdata

                    # if recvEndFlg:
                    #     break
                    # if tmpdata.decode('UTF-8') == "":
                    #     readEndCount += 1
                    # if readEndCount > 2:
                    #     break
                responseData = analysisResponseHeader(forcli, tmpdata, responseStatusLine)
                # print(responseData)
                clientsocket.send(responseData)
    except ConnectionRefusedError as e:
        print("[Warning] ConnectionRefuedError")
    except ConnectionError as e:
        print("connection Error")
        pass
    forcli.close()
    clientsocket.close()

def createConnectDest(websockFlg:bool):
    if websockFlg:
        return ("127.0.0.1",5555)
    else:
        return ("127.0.0.1",8888)

def analysisContentLength(responseData:bytes) -> int:
    pattern = "^CONTENT-LENGTH:.*$"
    line = responseData.decode('UTF-8').split("\r\n")
    for l in line:
        if re.match(pattern, l.upper().replace(' ','')):
            return int(l.split(":")[1].replace(' ',''))
    
    return 0

def searchMotionJPEGHeader(servsock:socket.socket) -> bytes:
    retData = b''
    firstHeadCount = 0
    while True:
        tmpdata = servsock.recv(BUF_SZIE)
        retData += tmpdata
        contentTypeFlg,contentTypeFrameFlg = analysisMotionJPEGHeader(tmpdata)
        if contentTypeFlg and contentTypeFrameFlg:
            return retData
        if contentTypeFlg and not contentTypeFrameFlg:
            raise RuntimeError("Server Response Content-Type is not correct!!!!")
        firstHeadCount += 1
        if firstHeadCount > 10:
            break
    return retData

def analysisMotionJPEGHeader(data:bytes) -> tuple:
    pattern = "^CONTENT-TYPE:.*$"
    contentTypeFlg = False
    contentTypeFrameFlg = False
    line = data.decode('UTF-8').split("\r\n")
    for l in line:
        if re.match(pattern, l.upper().replace(' ','')):
            contentTypeFlg = True
            if re.match("^multipart/x-mixed-replace; boundary=frame$",l.split(":")[1].strip()):
                contentTypeFrameFlg = True
            break
    return (contentTypeFlg, contentTypeFrameFlg)

def searchWebSocketUpdateHeader(servsock:socket.socket) -> bytes:
    retData = b''
    firstHeadCount = 0
    while True:
        tmpdata = servsock.recv(BUF_SZIE)
        retData += tmpdata
        if analysisWebSocketUpdateHeader(tmpdata):
            break
        firstHeadCount += 1
        if firstHeadCount > 10:
            break
    return retData


def analysisWebSocketUpdateHeader(responseHeader:bytes) -> bool:
    pattern = "^UPGRADE:WEBSOCKET$"
    line = responseHeader.decode('UTF-8').split("\r\n")
    for l in line:
        if re.match(pattern, l.upper().replace(' ','')):
            return True
    return False


def isBadResponse(statusLine:str) -> bool:
    pattern = "^(4|5)\d{2}$"
    if re.match(pattern, statusLine.split(" ")[1].replace(" ","")):
        print("Error Response")
        return True
    return False

def analysisResponseHeader(servsock:socket.socket, data:bytes, statusLine:str) -> bytes:
    responseData = b''
    pattern = "^3\d{2}$"
    if re.match(pattern, statusLine.split(" ")[1].replace(" ","")):
        return data
    else:
        return recurciveAnalysisRes(servsock, data)
        # responseData += data
        # conlen = getContentLength(responseData)
        # print(conlen)
        # if conlen > 0:
        #     judgeResponseHeader(responseData)
   
        # data = servsock.recv(BUF_SZIE)

def recurciveAnalysisRes(servsock:socket.socket, data:bytes) -> bytes:
    conlen = getContentLength(data)
    if conlen > 0:
        if judgeResponseHeader(conlen, data):
            return data
        else:
            tmpdata = servsock.recv(BUF_SZIE)
            data += tmpdata
            return recurciveAnalysisRes(servsock, data)
    else:
        tmpdata = servsock.recv(BUF_SZIE)
        data += tmpdata
        return recurciveAnalysisRes(servsock, data)


def getContentLength(data:bytes) -> int:
    pattern = "^CONTENT-LENGTH:.*$"
    line = data.decode('UTF-8').split("\r\n")
    for l in line:
        print(l)
        if re.match(pattern, l.upper().replace(' ','')):
            return int(l.split(":")[1].replace(' ',''))
    
    return 0

def judgeResponseHeader(contentLength:int, data:bytes) -> bool:
    dataLine = data.decode('UTF-8').split("\r\n\r\n")
    for l in dataLine:
        # print("++++++++Judge++++++++")
        # print(len(l))
        # print(l)
        # print("+++++++++++++++++++++")
        if len(l) == contentLength:
            return True
    return False