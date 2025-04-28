import re
import difflib

import gen_config.config
import gen_config.define
from utils import io_utils
from gen_config import parse_field_index
from gen_config import parse_config
from gen_config import export_lua
from gen_config import export_json
from gen_config import export_cs
from gen_config import export_go
from gen_config import export_language
from utils import path_utils
from utils.exception import LogException


def OnCommand():
    return "config","生成配置表"

def OnAwake():
    pass

def OnExecute(params):
    paramsLen = len(params)
    if paramsLen < 2:
        raise LogException("参数异常")

    parseParams = ParseParams(params[1:])

    gen_config.config.ReadConfig()

    if not io_utils.ExistFolder(gen_config.config.configPath):
        raise LogException("配置路径不存在[%s]" % gen_config.config.configPath)

    if gen_config.config.luaOutPath != "" and not io_utils.ExistFolder(gen_config.config.luaOutPath):
        raise LogException("lua输出路径不存在[%s]" % gen_config.config.luaOutPath)
    
    if gen_config.config.csCodeOutPath != "" and not io_utils.ExistFolder(gen_config.config.csCodeOutPath):
        raise LogException("cs代码输出路径不存在[%s]" % gen_config.config.csCodeOutPath)
    
    if gen_config.config.csDataOutPath != "" and not io_utils.ExistFolder(gen_config.config.csDataOutPath):
        raise LogException("cs数据输出路径不存在[%s]" % gen_config.config.csDataOutPath)

    #if not io_utils.ExistFolder(gen_config.config.goOutPath):
    #    raise LogException("go输出路径不存在[%s]" % gen_config.config.goOutPath)

    print("配置信息:")
    print("    配置路径:" + gen_config.config.configPath)
    print("    多语言路径:" + gen_config.config.languagePath)
    print("    lua输出路径:" + gen_config.config.luaOutPath)
    print("    go输出路径:" + gen_config.config.goOutPath)

    print("    cs代码输出路径:" + gen_config.config.csCodeOutPath)
    print("    cs数据输出路径:" + gen_config.config.csDataOutPath)

    GetConfigs()

    configName = params[paramsLen - 1]
    if configName == ".":
        configName = None

    checkMD5 = True

    if  params[1] == "-v":
        PrintSimilar(configName)
        return
    elif "-b" in parseParams:
        checkMD5 = False

    gen_config.define.parseFieldIndex = parse_field_index.ParseFieldIndex(gen_config.define.globalIndexFile)
    gen_config.define.parseFieldIndex.ParseFile()


    if "-i18n" in parseParams:
        gen_config.define.i18n = True
    elif params[1] == "-i18n_gen":
        gen_config.define.languages = params[2].split(":")
        print("->")
        genFiles = {}
        for fileName,_ in gen_config.define.configs.items():
            flag = GenI18nConfig(fileName)
            if flag:
                genFiles[fileName] = True
        CleanI18nConfigFile(genFiles)
        return

    if configName != None:
        if configName in gen_config.define.configs:
            print("->")
            GenConfig(configName,checkMD5)
        else:
            raise LogException("不存在配置表[%s]" % configName)
    else:
        print("->")
        for fileName,_ in gen_config.define.configs.items():
            GenConfig(fileName,checkMD5)

def OnComplete():
    gen_config.define.configs = {}
    gen_config.define.parseFieldIndex = None

def OnHelp():
    return "\
[config .]            生成全部配置\n\
[config xxx]          生成指定配置\n\
[config -v .]         查看目录下的所有配置\n\
[config -v xxx]       查看目录下相似的指定配置"


def GenConfig(configName,checkMD5):
    localPath = gen_config.define.configs[configName]
    fullPath = gen_config.config.configPath + localPath

    cacheMD5File = path_utils.GetCachePath("gen_config/md5/" + localPath)
    cacheMD5 = io_utils.ReadAllText(cacheMD5File)
    curMD5 = io_utils.GetFileMD5(fullPath)


    if checkMD5 and cacheMD5 != "" and cacheMD5 == curMD5:
        print("    " + configName + "(已跳过)")
        return
    else:
        print("    " + configName)
    
    configParse = parse_config.ParseConfig(configName,localPath)
    configParse.Parse()

    if gen_config.config.luaOutPath != "" and configParse.IsExportTarget(gen_config.define.ExportTarget.lua):
        export_lua.Export(configParse)

    if gen_config.config.csCodeOutPath != "" and configParse.IsExportTarget(gen_config.define.ExportTarget.cs):
        export_cs.Export(configParse)
    
    io_utils.CreateFolderByFile(cacheMD5File)
    io_utils.WriteAllText(cacheMD5File,curMD5)


def GenI18nConfig(configName):
    print("    " + configName)

    localPath = gen_config.define.configs[configName]
    
    configParse = parse_config.ParseConfig(configName,localPath)
    configParse.Parse()

    exportLanguage = export_language.ExportLanguage(configParse)
    exportLanguage.Parse()

    if not exportLanguage.IsExport():
        return False

    for language in gen_config.define.languages:
        filePath = gen_config.config.languagePath + language  + "/config/" + configParse.configName + ".json"
        exportLanguage.Export(filePath)

    return True

def CleanI18nConfigFile(genFiles):
    for language in gen_config.define.languages:
        files = io_utils.GetFiles(gen_config.config.languagePath + language  + "/config/","json")
        for file in files:
            if file.endswith("prefab.json"):
                continue

            fileName = io_utils.GetFileNameWithoutExtension(file)
            if not (fileName in genFiles):
                io_utils.DeleteFile(file)

def GetConfigs():
    files = io_utils.GetFiles(gen_config.config.configPath,"xls")
    for file in files:
        fileName = io_utils.GetFileNameWithoutExtension(file)
        
        if fileName.startswith("~$") or io_utils.GetFileName(file) == gen_config.define.globalIndexFile:
            continue

        fileNameLen = len(fileName)

        localPath = io_utils.RejectPath(file,gen_config.config.configPath)

        descIndex = fileName.find("(")
        if descIndex != -1 and fileName[fileNameLen-1] == ")":
            fileName = fileName[0:descIndex]

        if fileName in gen_config.define.configs:
            raise LogException("配置表命名冲突[%s]" % fileName)

        if not bool(re.search('^[a-z0-9_]*$', fileName))\
            or not fileName[0].islower() or fileName[len(fileName)-1] == "_"\
            or fileName.find("__") != -1:
            raise LogException("配置表命名异常[%s](只允许出现小写字母、下划线，并且首字母小写字母、尾字母不能为下划线，不能连续出现2个下划线)" % localPath)

        gen_config.define.configs[fileName] = localPath

def PrintSimilar(configName):
    print("->")
    maxNum = None
    if configName:
        maxNum = 3

    similarConfigs = []
    for name,localPath in gen_config.define.configs.items():
        if configName != None:
            similar = difflib.SequenceMatcher(None, configName, name).quick_ratio()
            if similar > 0.0:similarConfigs.append({ "similar":similar,"configName":name,"path":localPath } )
        else:
            similarConfigs.append({ "similar":0,"configName":name,"path":localPath } )

    similarConfigs = sorted(similarConfigs,key=lambda x:x["similar"],reverse=True)

    similarNum = len(similarConfigs)
    if similarNum <= 0:
        return

    printNum = similarNum
    if configName != None and maxNum != None and printNum > maxNum:
        printNum = maxNum

    for i in range(0,printNum):
        name = similarConfigs[i]["configName"]
        localPath = similarConfigs[i]["path"]
        print("    " + localPath)

def ParseParams(inParams):
    params = {}

    for param in inParams:
        infos = param.split("=")
        key = infos[0]

        if len(infos) == 2:
            params[key] = infos[1]
        else:
            params[param] = param

    return params