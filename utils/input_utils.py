import threading
import datetime
from utils import thread_utils
import time

inputStr = None
inputing = False
inputThread = None

def WaitInput(time,msg):
    global inputStr
    inputStr = None

    global inputThread

    inputThread = threading.Thread(target=InputThread,args=(msg,))
    inputThread.start()

    beginTime = datetime.datetime.now()

    while inputThread:
        if inputStr != None:
            break

        if time != None and time > 0:
            lastTime = datetime.datetime.now() - beginTime
            if lastTime.seconds >= time:
                print("输入超时")
                thread_utils.StopThread(inputThread)
                break

    return inputStr

def CancelInput():
    global inputThread

    if not inputThread:
        return

    print("取消了线程",str(inputThread))
    time.sleep(1)
    thread_utils.StopThread(inputThread)
    inputThread = None

def InputThread(msg):
    global inputStr
    inputStr = input(msg)