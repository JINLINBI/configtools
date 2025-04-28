from utils import path_utils
from utils import io_utils
import base.define

configPath = ""
luaOutPath = ""
goOutPath = ""
languagePath = ""


csCodeOutPath = ""
csDataOutPath = ""

def ReadConfig():
    #读取环境配置
    global configPath
    global luaOutPath
    global goOutPath
    global languagePath
    global csCodeOutPath
    global csDataOutPath

    confPath = path_utils.GetConfPath("gen_config/config/config.json")

    config = None
    try:
        config = io_utils.LoadJson(confPath)
    except Exception as e:
        raise Exception("配置加载失败[%s][%s]" % (confPath,str(e)))

    configPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["配置路径"])
    luaOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["lua输出路径"])
    goOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["go输出路径"])
    languagePath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["多语言路径"])

    csCodeOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["cs代码输出路径"])
    csDataOutPath = io_utils.GetAbsPathByRoot(base.define.rootPath,config["cs数据输出路径"])