import os
import json
import re
import traceback

from proto import parse_proto
from proto import export_proto_go
from proto import export_proto_lua
from utils import io_utils
from utils import path_utils

import proto.config
import proto.define

from utils.exception import LogException

def OnCommand():
    return "proto","生成协议"

def OnAwake():
    pass

def OnExecute(params):
    proto.config.ReadConfig()

    if not io_utils.ExistFolder(proto.config.protoFilePath):
        raise LogException("协议路径不存在[%s]" % proto.config.protoFilePath)

    if proto.define.isExportLua and not io_utils.ExistFolder(proto.config.luaOutPath):
        raise LogException("lua输出路径不存在[%s]" % proto.config.luaOutPath)

    if proto.define.isExportGo and not io_utils.ExistFolder(proto.config.goOutPath):
        raise LogException("go输出路径不存在[%s]" % proto.config.goOutPath)

    print("协议信息:")
    print("    协议路径:" + proto.config.protoFilePath)
    if proto.define.isExportLua:
        print("    lua输出路径:" + proto.config.luaOutPath)
    if proto.define.isExportGo:
        print("    go输出路径:" + proto.config.goOutPath)

    print("->")
    print("    读取协议文件")
    GetProtoFiles()
    print("    解析通用文件")
    ParseCommonFiles()
    print("    解析协议文件")
    ParseFiles()
    print("    导出协议文件")
    ExportFiles()
    print("    完成")

def GetProtoFiles():
    files = io_utils.GetFiles(proto.config.protoFilePath,"proto")

    for file in files:
        (_, name) = os.path.split(file)
        name = os.path.splitext(name)[0]

        localPath = io_utils.RejectPath(file,proto.config.protoFilePath)

        isCommon = localPath.startswith("common/")

        if isCommon:
            proto.define.commonProtoFiles[name] = localPath
        else:
            proto.define.protoFiles[name] = localPath

def ParseCommonFiles():
    proto.define.commonFileParses = []
    for _,localPath in proto.define.commonProtoFiles.items():
        fileParse = parse_proto.ParseProto(localPath,True)
        fileParse.Parse()
        proto.define.commonFileParses.append(fileParse)

    for fileParse in proto.define.commonFileParses:
        fileParse.CheckFileFieldType()

def ParseFiles():
    for _,localPath in proto.define.protoFiles.items():
        fileParse = parse_proto.ParseProto(localPath,False)
        fileParse.Parse()
        fileParse.CheckFileFieldType()
        proto.define.commonFileParses.append(fileParse)

def ExportFiles():
    io_utils.CleanFolder(proto.config.luaOutPath)
    io_utils.CleanFolder(proto.config.goOutPath)
    for fileParse in proto.define.commonFileParses:
        if proto.define.isExportGo:
            export_proto_go.ExportFile(fileParse)
        
        if proto.define.isExportLua and not fileParse.isCommon:
            export_proto_lua.ExportFile(fileParse)

def OnComplete():
    proto.define.protoFiles = {}
    proto.define.commonProtoFiles = {}
    proto.define.allTypes = {}
    proto.define.commonTypes = {}
    proto.define.fileParses = {}
    proto.define.commonFileParses = {}

def OnHelp():
    return "\
[proto]           生成协议"