import sys

from utils import io_utils

import base.define

def GetDataPath():
    curPath = io_utils.GetAbsPath(io_utils.GetPathDirectory(sys.argv[0]))
    return curPath + "data/"

def GetConfPath(localPath):
    return base.define.rootPath + localPath

def GetCachePath(localPath):
    return io_utils.GetAbsPath(base.define.cachePath + localPath)