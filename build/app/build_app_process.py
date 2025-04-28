import threading
import traceback
import time

threadExit = False
threadComplete = False
threadHandler = None

import build.utils
import build.define
import build.app.define


def StartProcess():
    global threadExit
    threadExit = False

    global threadComplete
    threadComplete = False

    global threadHandler
    threadHandler = CheckStartUnity

    print("->")
    print("出包流程:")
    print("    正在启动unity")

    buildThread = threading.Thread(target=AssetProcessThread)
    buildThread.daemon = True
    buildThread.start()


def AssetProcessThread():
    while (not threadExit):
        data = build.utils.GetLogFile(build.define.logFile)
        if not data or data["uuid"] != build.define.buildId:
            continue

        if ("error" in data) and data["error"] and ("errorLog" in data):
            print("->")
            print("打包异常:" +  data["errorLog"].replace("/r/n","\n         "))
            break

        try:
            threadHandler(data)
        except Exception as e:
            print("->")
            print("打包线程异常:%s[堆栈:%s]" % (str(e),traceback.format_exc()))
            break
        
        time.sleep(1)

    global threadComplete
    threadComplete = True


def CheckStartUnity(data):
    if not ("uuid" in data):
        return

    if data["uuid"] != build.define.buildId:
        return

    print("    正在生成首包资源")

    global threadHandler
    threadHandler = CheckGenAssets

def CheckGenAssets(data):
    if not ("genAssetsComplete" in data) or not data["genAssetsComplete"]:
        return
    
    global threadHandler

    print("    正在生成LuaWrap")
    threadHandler = CheckGenLuaWrap


def CheckGenLuaWrap(data):
    if not ("genLuaWrapComplete" in data) or not data["genLuaWrapComplete"]:
        return

    print("    正在刷新工程")

    global threadHandler
    threadHandler = CheckAssetRefresh

def CheckAssetRefresh(data):
    if not ("assetRefreshComplete" in data) or not data["assetRefreshComplete"]:
        return
    
    print("    正在生成客户端")

    global threadHandler
    threadHandler = CheckComplete

def CheckComplete(data):
    if not ("buildComplete" in data) or not data["buildComplete"]:
        return

    print("    完成")
    SetThreadExit(True)

def SetThreadExit(flag):
    global threadExit
    threadExit = flag