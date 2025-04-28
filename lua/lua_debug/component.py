from utils import io_utils
from utils import path_utils
from utils.exception import LogException

import base.define

luaPath = ""
dataPath = ""
httpPath = ""

def OnCommand():
    return "lua.debug","生成lua调试文件索引"

def OnAwake():
    pass

def OnExecute(params):
    ReadConfig()

    if not io_utils.ExistFolder(luaPath):
        raise LogException("lua路径不存在[%s]" % luaPath)

    if not io_utils.ExistFolder(dataPath):
        raise LogException("data路径不存在[%s]" % dataPath)

    if not io_utils.ExistFolder(httpPath):
        raise LogException("http路径不存在[%s]" % httpPath)

    indexFile = httpPath + "lua_files.json"

    print("配置信息:")
    print("    lua路径:" + luaPath)
    print("    data路径:" + dataPath)
    print("    http路径:" + httpPath)
    print("    索引文件:" + indexFile)

    file = open(indexFile,'w')
    
    file.write("{\n")

    luaFiles = io_utils.GetFiles(luaPath,"lua")
    for luaFile in luaFiles:
        localPath = io_utils.RejectPath(luaFile,httpPath)
        luaLocalPath = io_utils.RejectPath(luaFile,luaPath)
        file.write("    \"%s\":\"%s\",\n" % (localPath,luaLocalPath))

    dataFiles = io_utils.GetFiles(dataPath,"lua")
    for dataFile in dataFiles:
        localPath = io_utils.RejectPath(dataFile,httpPath)
        dataLocalPath = io_utils.RejectPath(dataFile,dataPath)
        file.write("    \"%s\":\"data/%s\",\n" % (localPath,dataLocalPath))

    file.write("}")

    file.flush()
    file.close()

    print("->")
    print("    完成")

def OnComplete():
    pass

def OnHelp():
    return "\
[lua.debug]          生成lua调试文件索引"

def ReadConfig():
    global luaPath
    global dataPath
    global httpPath

    confPath = path_utils.GetConfPath("lua/lua_debug/config/config.json")

    config = None
    try:
        config = io_utils.LoadJson(confPath)
    except Exception as e:
        raise Exception("配置加载失败[%s][%s]" % (confPath,str(e)))

    luaPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["lua路径"])
    dataPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["data路径"])
    httpPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["http路径"])
