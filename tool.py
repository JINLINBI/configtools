import sys
import types
import os
import traceback
import pathlib

sys.path.append(os.path.dirname(__file__))

import base.define
from utils.exception import LogException

from utils import io_utils
import gen_config.component
import proto.component
import build.asset.component
import build.app.component
import build.language.component
import lua.lua_debug.component
import proto.protobuf.component


import unity_cli.gen_language_file.component

base.define.rootFile = io_utils.GetFilePath(__file__)
base.define.rootPath = io_utils.GetPathDirectory(base.define.rootFile)


home = str(pathlib.Path.home())
if sys.platform == "win32":
    base.define.cachePath = home + "/AppData/Roaming/" + base.define.appName
elif sys.platform == "linux":
    base.define.cachePath = home + "/.local/share/" + base.define.appName
elif sys.platform == "darwin":
    base.define.cachePath = home + "/Library/Application Support/" + base.define.appName
base.define.cachePath = io_utils.GetAbsPath(base.define.cachePath)

commands = {}

#注册工具组件
components = []
def InitCommand():
    components.append(build.asset.component)
    components.append(build.app.component)
    components.append(build.language.component)
    components.append(gen_config.component)
    components.append(proto.protobuf.component)
    components.append(lua.lua_debug.component)
    components.append(unity_cli.gen_language_file.component)


def CommandHelper(command=None):
    if not command:
        for component in components:
            command,tips = component.OnCommand()
            tplt = "{0:{2}<20}{1:{2}<100}"
            print(tplt.format(str.format("[%s]"%command),tips,chr(32)))
    else:
        component = commands[command]
        print("帮助:\n%s" % (component.OnHelp()))

def BindCommand():
    for component in components:
        filePath = io_utils.GetFilePath(component.__file__)

        if not ("OnCommand" in dir(component)) or not isinstance(component.OnCommand,types.FunctionType):
            raise Exception("组件OnCommand方法异常[%s]" % filePath)

        if not ("OnAwake" in dir(component)) or not isinstance(component.OnAwake,types.FunctionType):
            raise Exception("组件OnAwake方法异常[%s]" % filePath)

        if not ("OnExecute" in dir(component)) or not isinstance(component.OnExecute,types.FunctionType):
            raise Exception("组件OnExecute方法异常[%s]" % filePath)

        if not ("OnComplete" in dir(component)) or not isinstance(component.OnComplete,types.FunctionType):
            raise Exception("组件OnComplete方法异常[%s]" % filePath)

        if not ("OnHelp" in dir(component)) or not isinstance(component.OnComplete,types.FunctionType):
            raise Exception("组件OnHelp方法异常[%s]" % filePath)

        command,_ = component.OnCommand()

        if not isinstance(command,str) or command == "":
            raise Exception("组件OnCommand方法返回值错误[%s]" % filePath)

        component.OnAwake()
        commands[command] = component

InitCommand()
BindCommand()

#print("->")
print("运行环境:")
print("    根目录:" + base.define.rootPath)
print("    缓存目录:" + base.define.cachePath)

if len(sys.argv) > 1:
    params = sys.argv[1:]
    paramLen = len(params)
    command = sys.argv[1]
    if command == "-v" :
        CommandHelper()
    elif command in commands and paramLen == 2 and params[1] == "-v":
        CommandHelper(command)
    elif command in commands:
        try:
            commands[command].OnExecute(params)
        except LogException as e:
            print()
            print("Error：" + str(e))
            os.system("pause")
        except Exception as e:
            print()
            print("Error：" + traceback.format_exc())
            os.system("pause")
        
        commands[command].OnComplete()
    elif command != "":
        print("    无法识别的命令:" + command)
    
    print(base.define.line + ">")
    print()
else:
    print("请输入执行命令")