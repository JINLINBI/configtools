import threading
import uuid
import random

import build.define
import build.config
import build.asset.define
from build.asset import build_asset
from utils import io_utils
from utils import value_utils
from utils import path_utils
from utils.exception import LogException

def OnCommand():
    return "build.asset","打包资源"

def OnAwake():
    pass

def OnExecute(params):
    paramsLen = len(params)
    if paramsLen < 2:
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

    print("编译环境:")
    print("    unity运行程序:" + build.config.UNITY_PATH)
    print("    资源工程目录:" + build.define.buildInfo["资源工程目录"])
    print("    输出目录:" + build.define.outPath)
    print("    log文件:" +build.define.logFile)

    variableParams = ParseParams(params[2:])

    build.define.buildId = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random())))

    build.define.runMode = "release"
    if "-debug" in variableParams:build.define.runMode = "-debug"

    build.asset.define.executeCmd = build.asset.define.buildCmd % (
        build.config.UNITY_PATH,
        build.define.buildInfo["资源工程目录"],
        build.utils.GetRunMode(build.define.runMode),
        build.define.buildId,
        build.define.platform,
        "false" if not ("-channelSubPrefix" in variableParams) else variableParams["-channelSubPrefix"],
        "" if not ("-channel" in variableParams) else variableParams["-channel"],
        "false" if not ("-noticeError" in variableParams) else variableParams["-noticeError"])

    print("->")
    print("    uuid:" + build.define.buildId)
    print("    编译平台:" + build.define.platform)
    print("    运行模式:" + build.define.runMode)
    if "-cmd" in variableParams:
        print("    执行命令:" + build.asset.define.executeCmd)

    build_asset.Build(variableParams)

def ParseParams(inParams):
    params = {}

    for param in inParams:
        infos = param.split("=")
        key = infos[0]

        if len(infos) == 2:
            params[key] = infos[1]
        else:
            params[param] = param

    return params


def OnComplete():
    pass

def OnHelp():
    return "\
[build.asset 平台]            打包(win、android、ios)平台资源\n\
动态参数:\n\
    [-debug](显示unity)\n\
    [-cmd](打印执行命令)"