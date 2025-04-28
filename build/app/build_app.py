import os
import sys
import traceback
import time
import threading
import datetime
import re

from utils import io_utils
from utils import svn_utils
from utils import thread_utils
from utils import path_utils

import build.app.define
import build.define
import build.config

from build.app import build_app_process

import utils.value_utils as value_utils

from utils.exception import LogException

def Build(params):
    #CopyBaseSetting(params)

    io_utils.CleanFolder(build.define.luaWarpPath)

    build_app_process.StartProcess()

    state = os.system(build.app.define.executeCmd)

    if state != 0:
        print("->")
        print("    启动unity失败")
        build_app_process.SetThreadExit(True)

    while state == 0 and not build_app_process.threadComplete:
        #TODO:做超时判定，超时还未完成，就是异常退出的情况
        pass



def CopyBaseSetting(params):
    baseSettingFile = build.define.buildInfo["客户端工程目录"] + build.define.baseSettingFile

    config = None
    try:
        config = io_utils.LoadJson(baseSettingFile)
    except Exception as e:
        raise LogException("BaseSetting加载失败[%s][%s]" % (baseSettingFile,str(e)))


    args = params["-args"]
    if args == "":args = config["args"]

    content = "{\n"
    content += "    \"debug\":false,\n"
    content += "    \"app_version\":\"%s\",\n" % config["app_version"]
    content += "    \"cs_version\":\"%s\",\n" % config["cs_version"]
    content += "    \"channel\":\"%s\",\n" % params["-channel"]
    content += "    \"args\":\"%s\",\n" % args
    content += "    \"url\":\"%s\",\n" % str(config["url"])
    content += "    \"remote\":%s,\n" % str(config["remote"]).lower()
    content += "    \"check_update\":%s,\n" % str(config["check_update"]).lower()
    content += "    \"res_debug\":false,\n"
    content += "    \"lua_debug\":false,\n"
    content += "    \"assets_setup\":%s\n" % str(config["assets_setup"]).lower()
    content += "}"

    io_utils.WriteAllText(baseSettingFile,content)