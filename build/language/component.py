import threading
import uuid
import re
import random
import time
import os
import traceback

import build.define
import build.config
import build.language.define

import unity_cli.utils

from build.app import build_app

from utils import io_utils
from utils import value_utils
from utils import path_utils

from utils.exception import LogException


threadExit = False
threadComplete = False
threadHandler = None

def OnCommand():
    return "build.language","编译语言包"

def OnAwake():
    pass

def OnExecute(params):
    paramsLen = len(params)
    if paramsLen < 3:
        raise LogException("参数异常")

    build.define.platform = params[1]

    if not build.define.IsPlatformType(build.define.platform):
        raise LogException("错误的平台[%s]" % build.define.platform)

    build.config.ReadConfig()
    build.define.buildInfo = build.config.buildInfos[build.define.platform]

    if not io_utils.ExistFile(build.config.UNITY_PATH):
        raise LogException("Unity运行程序不存在[%s]" % build.config.UNITY_PATH)

    if not io_utils.ExistFolder(build.define.buildInfo["资源工程目录"]):
        raise LogException("资源工程目录不存在[%s]" % build.define.buildInfo["资源工程目录"])

    if build.utils.ProjectRuning(build.define.buildInfo["资源工程目录"]):
        raise LogException("资源工程正在运行[%s]" % build.define.buildInfo["资源工程目录"])

    build.define.outPath = build.utils.GetOutPath(build.define.buildInfo["资源工程目录"] + "Assets/")
    build.define.logFile = build.define.outPath + build.define.localLogFile

    print("编译语言包环境:")
    print("    unity运行程序:" + build.config.UNITY_PATH)
    print("    资源工程目录:" + build.define.buildInfo["资源工程目录"])
    print("    输出目录:" + build.define.outPath)
    print("    log文件:" +build.define.logFile)


    variableParams = ParseParams(params[2:])

    build.define.buildId = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random())))

    runMode = "release"
    if "-debug" in variableParams:runMode = "-debug"

    executeCmd = build.language.define.buildCmd % (
        build.config.UNITY_PATH,
        build.define.buildInfo["资源工程目录"],
        build.utils.GetRunMode(runMode),
        build.define.buildId,
        build.define.platform,
        "false" if not ("-channelSubPrefix" in variableParams) else variableParams["-channelSubPrefix"],
        "" if not ("-channel" in variableParams) else variableParams["-channel"],
        variableParams["-language"],
        "false" if not ("-noticeError" in variableParams) else variableParams["-noticeError"])

    print("->")
    print("    uuid:" + build.define.buildId)
    print("    编译平台:" + build.define.platform)
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
    print("编译流程:")
    print("    正在启动unity")

    buildThread = threading.Thread(target=AssetProcessThread)
    buildThread.daemon = True
    buildThread.start()

def AssetProcessThread():
    while (not threadExit):
        data = io_utils.SafeLoadJson(build.define.logFile)
        if not data or data["uuid"] != build.define.buildId:
            continue

        if ("error" in data) and data["error"] and ("errorLog" in data):
            print("->")
            print("编译语言包异常:" +  data["errorLog"].replace("/r/n","\n         "))
            break

        try:
            threadHandler(data)
        except Exception as e:
            print("->")
            print("编译语言包线程异常:%s[堆栈:%s]" % (str(e),traceback.format_exc()))
            break
        
        time.sleep(1)

    global threadComplete
    threadComplete = True

def CheckStartUnity(data):
    if not ("uuid" in data):
        return

    if data["uuid"] != build.define.buildId:
        return

    print("    正在编译语言包")

    global threadHandler
    threadHandler = CheckComplete

def CheckComplete(data):
    if not ("buildComplete" in data) or not data["buildComplete"]:
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
        raise LogException("编译语言包需要输入[-language]参数")

    return params

def OnComplete():
    pass

def OnHelp():
    return "\
[build.language 平台 -language=语言列表]       编译语言包\
动态参数:\n\
    [-debug](显示unity)\n\
    [-cmd](打印执行命令)" 
