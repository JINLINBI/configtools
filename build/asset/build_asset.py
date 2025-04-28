import uuid
import json
import threading
import time
import datetime
import os
import traceback
import sys

import build.define
import build.config
import build.utils
import build.asset.define

from utils import io_utils
from utils import time_utils
from utils import svn_utils
from utils import thread_utils
from utils import input_utils

executeCmd = None

#流程
threadExit = False
threadComplete = False

threadHandler = None

luaBeginTime = None
luaLastTime = None

resBeginTime = None
resLastTime = None

def Build(params):
    StartProcess()

    state = os.system(build.asset.define.executeCmd)
    if state != 0:
        print("->")
        print("    启动unity失败")
        SetThreadExit(True)

    while state == 0 and not threadComplete:
        pass

def StartProcess():
    global threadExit
    threadExit = False

    global threadComplete
    threadComplete = False

    global threadHandler
    threadHandler = CheckStartUnity

    global luaBeginTime
    luaBeginTime = None

    global resBeginTime
    resBeginTime = None

    print("->")
    print("编译流程:")
    print("    正在启动unity")

    buildThread = threading.Thread(target=AssetProcessThread)
    buildThread.daemon = True
    buildThread.start()


def AssetProcessThread():
    while (not threadExit):
        data = build.utils.GetLogFile(build.define.logFile)
        if not data or data["uuid"] != build.define.buildId:
            continue

        if ("error" in data) and data["error"] and ("errorLog" in data):
            print("                                                                                            ",end="\r\n")
            print("->")
            print("编译异常:" +  data["errorLog"].replace("/r/n","\n         "))
            break

        try:
            threadHandler(data)
        except Exception as e:
            print("                                                                                            ",end="\r\n")
            print("->")
            print("编译线程异常:%s[堆栈:%s]" % (str(e),traceback.format_exc()))
            break
        
        time.sleep(1)

    global threadComplete
    threadComplete = True

#步骤一：启动Unity
def CheckStartUnity(data):
    if not ("uuid" in data):
        return

    if data["uuid"] != build.define.buildId:
        return

    print("    正在解析编译文件")

    global threadHandler
    threadHandler = CheckBuildParse

#步骤二：解析编译文件
def CheckBuildParse(data):
    if not ("parseComplete" in data) or not data["parseComplete"]:
        return

    print("->")
    print("    资源版本:" + str(data["version"]))
    print("    lua文件数量:" + str(data["luaFileNum"]))
    print("    lua文件编译数量:" + str(data["outLuaFileNum"]))
    print("    res文件数量:" + str(data["resFileNum"]))
    print("    res文件编译数量:" + str(data["outResFileNum"]))

    beginTime = datetime.datetime.now()

    global luaLastTime
    luaLastTime = datetime.datetime.now() - beginTime

    global resLastTime
    resLastTime = datetime.datetime.now() - beginTime

    global threadHandler
    threadHandler = CheckLuaToBegin

    print("->")
    print("    正在编译脚本&配置")

def CheckLuaToBegin(data):
    global luaBeginTime
    if ("luaBuilding" in data) and data["luaBuilding"]:
        luaBeginTime = datetime.datetime.now()
        
        global threadHandler
        threadHandler = CheckLuaToComplete

#步骤三：Lua进度
def CheckLuaToComplete(data):
    if ("luaBuildComplete" in data) and data["luaBuildComplete"]:
        h,m,s = time_utils.GetFormat_h_m_s(time_utils.GetTimeInterval(luaBeginTime))
        print("        %02d:%02d:%02d" % (h, m, s))

        print("    正在编译资源")

        global threadHandler
        threadHandler = CheckResProgressToBegin

def CheckResProgressToBegin(data):
    global resBeginTime
    if ("resBuilding" in data) and data["resBuilding"]:
        resBeginTime = datetime.datetime.now()
        
        global threadHandler
        threadHandler = CheckResProgressToPipelineReady

def CheckResProgressToPipelineReady(data):
    if not CheckResProgressComplete(data) and ("resBuildPipelineReady" in data) and data["resBuildPipelineReady"]:
        print("        Pipeline准备")

        global threadHandler
        threadHandler = CheckResProgressToPipelineOut

def CheckResProgressToPipelineOut(data):
    if not CheckResProgressComplete(data) and ("resBuildPipelineOut" in data) and data["resBuildPipelineOut"]:
        print("        Pipeline输出")

        global threadHandler
        threadHandler = CheckResProgressToComplete

#步骤四：Res进度
def CheckResProgressToComplete(data):
    CheckResProgressComplete(data)

def CheckResProgressComplete(data):
    if ("resBuildComplete" in data) and data["resBuildComplete"]:
        h,m,s = time_utils.GetFormat_h_m_s(time_utils.GetTimeInterval(resBeginTime))
        print("        %02d:%02d:%02d" % (h, m, s))

        print("->")
        print("    正在同步资源版本")

        global threadHandler
        threadHandler = CheckSync

        return True
    else:
        return False


#步骤四：同步
def CheckSync(data):
    if ("syncComplete" in data) and data["syncComplete"]:
        global threadHandler
        threadHandler = CheckBuildComplete

def CheckBuildComplete(data):
    if ("buildComplete" in data) or data["buildComplete"]:
        SetThreadExit(True)
        print("    完成")
    

def SetThreadExit(flag):
    global threadExit
    threadExit = flag