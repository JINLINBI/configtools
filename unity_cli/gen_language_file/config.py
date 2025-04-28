import json

import build.define
import base.define
from utils import path_utils
from utils import io_utils

UNITY_PATH = ""
buildInfo = {}

def ReadConfig():
    global UNITY_PATH
    global buildInfo

    confPath = path_utils.GetConfPath("unity_cli/gen_language_file/config/config.json")

    config = None
    try:
        config = io_utils.LoadJson(confPath)
    except Exception as e:
        raise Exception("配置加载失败[%s][%s]" % (confPath,str(e)))

    buildInfo["工程目录"] = io_utils.GetAbsPathByRoot(base.define.rootPath,config["工程目录"])

    UNITY_PATH = config["unity"]