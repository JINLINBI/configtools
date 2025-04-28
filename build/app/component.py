import threading
import uuid
import re
import random
import time

import build.define
import build.config
import build.app.define

from build.app import build_app

from utils import io_utils
from utils import value_utils
from utils import path_utils

from utils.exception import LogException

def OnCommand():
    return "build.app","生成客户端"

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
    
    if not io_utils.ExistFolder(build.define.buildInfo["客户端工程目录"]):
        raise LogException("客户端工程目录不存在[%s]" % build.define.buildInfo["客户端工程目录"])

    if build.utils.ProjectRuning(build.define.buildInfo["客户端工程目录"]):
        raise LogException("客户端工程正在运行[%s]" % build.define.buildInfo["客户端工程目录"])

    build.define.outPath = build.utils.GetOutPath(build.define.buildInfo["客户端工程目录"] + "Assets/")
    build.define.logFile = build.define.outPath + build.define.localLogFile
    build.define.luaWarpPath = build.define.buildInfo["客户端工程目录"] + build.define.localLuaWarpPath

    print("出包环境:")
    print("    unity运行程序:" + build.config.UNITY_PATH)
    print("    客户端工程目录:" + build.define.buildInfo["客户端工程目录"])
    print("    LuaWrap目录:" + build.define.luaWarpPath)
    print("    输出目录:" + build.define.outPath)
    print("    log文件:" +build.define.logFile)

    variableParams = ParseParams(build.define.platform,params[2:])

    build.define.buildId = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random())))

    build.define.runMode = "release"
    if "-debug" in variableParams:build.define.runMode = "-debug"

    outName = None
    outFile = None
    if build.define.platform == build.define.PlatformType.win:
        outName = "app.exe"
        outFile = "%sapp/%s" % (build.define.outPath,outName)
    elif build.define.platform == build.define.PlatformType.android:
        nowTime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        outName = nowTime + ".apk"
        outFile = "%sapp/%s/%s" %(build.define.outPath,variableParams["-channel"],outName)

    build.app.define.executeCmd = build.app.define.buildCmd % (
        build.config.UNITY_PATH,
        build.define.buildInfo["客户端工程目录"],
        build.utils.GetRunMode(build.define.runMode),
        build.define.buildId,
        build.define.platform,
        outName,
        variableParams["-assetsLen"],
        variableParams["-channel"],
        variableParams["-gameName"],
        "false" if not ("-channelSubPrefix" in variableParams) else variableParams["-channelSubPrefix"],
        variableParams["-baseSettingFile"],
        "true" if not ("-isSyncUpdate" in variableParams) else variableParams["-isSyncUpdate"])

    print("->")
    print("    uuid:" + build.define.buildId)
    print("    打包平台:" + build.define.platform)
    print("    首包资源大小:%s(mb)" % str(variableParams["-assetsLen"]))
    print("    输出文件:" + outFile)
    print("    运行模式:" + build.define.runMode)
    if "-cmd" in variableParams:
        print("    执行命令:" +  build.app.define.executeCmd)

    build_app.Build(variableParams)

def ParseParams(platform,inParams):
    params = {}

    for param in inParams:
        infos = param.split("=")
        infoLen = len(infos)
        key = infos[0]

        if key == "-assetsLen":
            if infoLen != 2:
                raise LogException("解析参数错误[%s]" % param)
            
            assetLength = value_utils.GetInt(infos[1])
            if assetLength == None:
                raise LogException("解析参数错误[%s]" % param)

            params["-assetsLen"] = assetLength
        elif key == "-args":
            if infoLen != 2:
                raise LogException("解析参数错误[%s]" % param)

            params["-args"] = infos[1]
        elif key == "-channel":
            if infoLen != 2:
                raise LogException("解析参数错误[%s]" % param)

            if not bool(re.search('^[a-z]*$',infos[1])):
                raise LogException("解析参数错误[%s]（渠道只能是小写字母）" % param)

            params["-channel"] = infos[1]
        elif key == "-gameName":
            if infoLen != 2:
                raise LogException("解析参数错误[%s]" % param)

            params["-gameName"] = infos[1]
        elif len(infos) == 2:
            params[key] = infos[1]
        else:
            params[param] = param

    if not ("-channel" in params):
        raise LogException("打包需要输入[-channel]参数")

    if not ("-gameName" in params):
        raise LogException("打包需要输入[-gameName]参数")
    
    if not ("-baseSettingFile" in params):
        raise LogException("打包需要输入[-baseSettingFile]参数")

    if not ("-assetsLen" in params):
        params["-assetsLen"] = 0

    if not ("-args" in params):
        params["-args"] = ""

    return params


def OnComplete():
    pass

def OnHelp():
    return "\
[build.app win -channel:渠道名 -gameName:游戏名字]       打包win平台资源\n\
[build.app android -channel:渠道名 -gameName:游戏名字]   打包andorid平台资源\n\
动态参数:\n\
    [-assetsLen:内置资源大小](拷贝资源到客户端,MB单位,-1为全部拷贝)\n\
    [-args:内容](自定义参数)\n\
    [-c](清理LuaWrap)\n\
    [-debug](显示unity)\n\
    [-cmd](打印执行命令)" 