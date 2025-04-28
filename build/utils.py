from utils import io_utils
from utils import path_utils
import json

import build.define

from utils.exception import LogException

def ProjectRuning(projectPath):
    lockFile = projectPath + build.define.unityLockfile

    if not io_utils.ExistFile(lockFile):
        return False
    
    try:
        io_utils.DeleteFile(lockFile)
        return False
    except:
        return True

def GetRunMode(runMode):
    if runMode == "release":
        return " -quit -batchmode"
    else:
        return ""

def GetLogFile(logFile):
    if not io_utils.ExistFile(logFile):
        return None

    try:
        file = open(logFile, encoding='utf-8')
        content = file.read()
        file.close()
        return json.loads(content)
    except:
        return None

def GetOutPath(projectPath):
    buildFile = io_utils.GetAbsPath(projectPath + build.define.buildFilePath)

    config = None
    try:
        config = io_utils.LoadJson(buildFile)
    except Exception as e:
        raise LogException("打包配置加载失败[%s][%s]" % (buildFile,str(e)))

    if not ("输出路径" in config):
        raise LogException("打包配置(输出路径)，不存在[{0}]" % (buildFile))

    return io_utils.GetAbsPathByRoot(projectPath,config["输出路径"]) + build.define.platform + "/"

def GetCdnPath(projectPath):
    buildFile = io_utils.GetAbsPath(projectPath + build.define.buildFilePath)

    config = None
    try:
        config = io_utils.LoadJson(buildFile)
    except Exception as e:
        raise LogException("打包配置加载失败[%s][%s]" % (buildFile,str(e)))

    if not ("cdn路径" in config):
        raise LogException("打包配置(cdn路径)，不存在[{0}]" % (buildFile))

    if config["cdn路径"] == "":
        return ""
    else:
        return io_utils.GetAbsPathByRoot(projectPath,config["cdn路径"]) + build.define.platform + "/"

def GetProjectCompanyName(projectPath):
    projectSettingsFile = io_utils.GetAbsPath(projectPath + "ProjectSettings/ProjectSettings.asset")

    