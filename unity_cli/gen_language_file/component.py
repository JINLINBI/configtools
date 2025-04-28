import threading
import uuid
import re
import random
import time
import os
import traceback

import unity_cli.gen_language_file.config
import unity_cli.gen_language_file.define

import unity_cli.utils

from build.app import build_app

from utils import io_utils
from utils import value_utils
from utils import path_utils

from utils.exception import LogException


buildId = ""
logFile = ""
executeCmd = ""

threadExit = False
threadComplete = False
threadHandler = None

def OnCommand():
    return "unity_cli.gen_language_file","生成多语言文件"

def OnAwake():
    pass

def OnExecute(params):
    global buildId
    global logFile
    global executeCmd

    paramsLen = len(params)
    if paramsLen < 2:
        raise LogException("参数异常")

    unity_cli.gen_language_file.config.ReadConfig()

    if not io_utils.ExistFile(unity_cli.gen_language_file.config.UNITY_PATH):
        raise LogException("Unity运行程序不存在[%s]" % unity_cli.gen_language_file.config.UNITY_PATH)
    
    if not io_utils.ExistFolder(unity_cli.gen_language_file.config.buildInfo["工程目录"]):
        raise LogException("工程目录不存在[%s]" % unity_cli.gen_language_file.config.buildInfo["工程目录"])

    if unity_cli.utils.ProjectRuning(unity_cli.gen_language_file.config.buildInfo["工程目录"]):
        raise LogException("工程正在运行[%s]" % unity_cli.gen_language_file.config.buildInfo["工程目录"])

    # build.define.outPath = build.utils.GetOutPath(build.define.buildInfo["客户端工程目录"] + "Assets/")
    # build.define.logFile = build.define.outPath + build.define.localLogFile
    # build.define.luaWarpPath = build.define.buildInfo["客户端工程目录"] + build.define.localLuaWarpPath
    
    logFile = unity_cli.gen_language_file.config.buildInfo["工程目录"] + unity_cli.gen_language_file.define.localLogFile

    print("生成多语言文件环境:")
    print("    unity运行程序:" + unity_cli.gen_language_file.config.UNITY_PATH)
    print("    工程目录:" + unity_cli.gen_language_file.config.buildInfo["工程目录"])
    print("    log文件:" + logFile)


    variableParams = ParseParams(params[1:])

    buildId = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random())))

    runMode = "release"
    if "-debug" in variableParams:runMode = "-debug"

    executeCmd = unity_cli.gen_language_file.define.buildCmd % (
        unity_cli.gen_language_file.config.UNITY_PATH,
        unity_cli.gen_language_file.config.buildInfo["工程目录"],
        unity_cli.utils.GetRunMode(runMode),
        buildId,
        variableParams["-language"])

    print("->")
    print("    uuid:" + buildId)
    print("    运行模式:" + runMode)
    print("    生成语言:" + variableParams["-language"])
    if "-cmd" in variableParams:
        print("    执行命令:" +  executeCmd)

    StartProcess()


    state = os.system(executeCmd)

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

    print("->")
    print("生成流程:")
    print("    正在启动unity")

    buildThread = threading.Thread(target=AssetProcessThread)
    buildThread.daemon = True
    buildThread.start()

def AssetProcessThread():
    while (not threadExit):
        data = io_utils.SafeLoadJson(logFile)
        if not data or data["uuid"] != buildId:
            continue

        if ("error" in data) and data["error"] and ("errorLog" in data):
            print("->")
            print("生成多语言文件异常:" +  data["errorLog"].replace("/r/n","\n         "))
            break

        try:
            threadHandler(data)
        except Exception as e:
            print("->")
            print("生成多语言文件线程异常:%s[堆栈:%s]" % (str(e),traceback.format_exc()))
            break
        
        time.sleep(1)

    global threadComplete
    threadComplete = True

def CheckStartUnity(data):
    if not ("uuid" in data):
        return

    if data["uuid"] != buildId:
        return

    print("    正在生成多语言文件")

    global threadHandler
    threadHandler = CheckComplete

def CheckComplete(data):
    if not ("genComplete" in data) or not data["genComplete"]:
        return

    print("    完成")
    SetThreadExit(True)

def SetThreadExit(flag):
    global threadExit
    threadExit = flag

def ParseParams(inParams):
    params = {}

    for param in inParams:
        infos = param.split("=")
        if len(infos) == 2:
            params[infos[0]] = infos[1]
        else:
            params[param] = param

    if not ("-language" in params):
        raise LogException("生成多语言文件需要输入[-language]参数")

    return params

def OnComplete():
    pass

def OnHelp():
    return "\
[unity_cli.gen_language_file -language=语言列表]       生成多语言文件\
动态参数:\n\
    [-debug](显示unity)\n\
    [-cmd](打印执行命令)" 
