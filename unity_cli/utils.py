from utils import io_utils
from utils import path_utils
import json

import unity_cli.define

from utils.exception import LogException

def ProjectRuning(projectPath):
    lockFile = projectPath + unity_cli.define.unityLockfile

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