import json

import build.define
import base.define
from utils import path_utils
from utils import io_utils

UNITY_PATH = ""
buildInfos = {}

def ReadConfig():
    global UNITY_PATH
    global buildInfos

    confPath = path_utils.GetConfPath("build/config/config.json")

    config = None
    try:
        config = io_utils.LoadJson(confPath)
    except Exception as e:
        raise Exception("配置加载失败[%s][%s]" % (confPath,str(e)))
    
    buildInfos[build.define.PlatformType.win] = {}
    buildInfos[build.define.PlatformType.android] = {}
    buildInfos[build.define.PlatformType.ios] = {}

    platform = build.define.PlatformType.win
    buildInfos[platform]["资源工程目录"] = io_utils.GetAbsPathByRoot(base.define.rootPath,config[platform]["资源工程目录"])
    buildInfos[platform]["客户端工程目录"] = io_utils.GetAbsPathByRoot(base.define.rootPath,config[platform]["客户端工程目录"])

    platform = build.define.PlatformType.android
    buildInfos[platform]["资源工程目录"] = io_utils.GetAbsPathByRoot(base.define.rootPath,config[platform]["资源工程目录"])
    buildInfos[platform]["客户端工程目录"] = io_utils.GetAbsPathByRoot(base.define.rootPath,config[platform]["客户端工程目录"])

    UNITY_PATH = config["unity"]