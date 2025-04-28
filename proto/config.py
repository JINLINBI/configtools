from utils import path_utils
from utils import io_utils
import base.define


protoFilePath = ""
goOutPath = ""
goPackageName = ""
goByteUtilsPath = ""
goByteUtilsName = ""
csOutPath = ""
clientOutPath = ""

def ReadConfig():
    global protoFilePath
    global goOutPath
    global goPackageName
    global goByteUtilsPath
    global goByteUtilsName
    global csOutPath
    global clientOutPath

    confPath = path_utils.GetConfPath("proto/config/config.json")

    config = None
    try:
        config = io_utils.LoadJson(confPath)
    except Exception as e:
        raise Exception("配置加载失败[%s][%s]" % (confPath,str(e)))

    protoFilePath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["协议路径"])

    goOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["go输出路径"])
    goPackageName = config["go包名"]
    goByteUtilsPath = config["go字节处理类路径"]
    goByteUtilsName = config["go字节处理类名"]

    csOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["CS输出路径"])

    clientOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["客户端输出路径"])