import os
import json
import re
import traceback

from proto import parse_proto
from proto import export_proto_go
from proto import export_proto_lua
from utils import io_utils
from utils import path_utils
import base.define

import proto.config
import proto.define

from utils.exception import LogException

protoIndexs = {}

def OnCommand():
    return "proto","生成协议"

def OnAwake():
    pass

def OnExecute(params):
    proto.config.ReadConfig()

    if not io_utils.ExistFolder(proto.config.protoFilePath):
        raise LogException("协议路径不存在[%s]" % proto.config.protoFilePath)

    if proto.define.isExportClient and not io_utils.ExistFolder(proto.config.clientOutPath):
        raise LogException("客户端输出路径不存在[%s]" % proto.config.clientOutPath)

    if proto.define.isExportCS and not io_utils.ExistFolder(proto.config.csOutPath):
        raise LogException("cs输出路径不存在[%s]" % proto.config.csOutPath)

    print("协议信息:")
    print("    协议路径:" + proto.config.protoFilePath)
    if proto.define.isExportClient:
        print("    客户端输出路径:" + proto.config.clientOutPath)
    if proto.define.isExportCS:
        print("    cs输出路径:" + proto.config.csOutPath)

    print("->")

    files = io_utils.GetFiles(proto.config.protoFilePath,"proto")

    ParseProtoMapping(files)

    if proto.define.isExportClient:
        io_utils.CreateFolder(proto.config.clientOutPath)
        io_utils.CleanFolder(proto.config.clientOutPath)
        GenClientProtos(files)

    if proto.define.isExportCS:
        io_utils.CreateFolder(proto.config.csOutPath)
        io_utils.CleanFolder(proto.config.csOutPath)
        GenCSProtos(files)

    print("    完成")


def ParseProtoMapping(files):
    global protoIndexs
    protoIndexs["c2s"] = {}
    protoIndexs["s2c"] = {}
    protoIndexs["file"] = [] #sheetData.fieldValues.append(rowDatas)

    for file in files:
        protoIndexs["file"].append(io_utils.GetFileNameWithoutExtension(file))
        for line in open(file,"r",encoding="utf-8"):
            if line.startswith("message"):
                lineInfos = line.split(" ")
                msgName = lineInfos[1]
                msgNameInfo = msgName.split("_")
                if len(msgNameInfo) == 2:
                    code = msgNameInfo[1]
                    if msgNameInfo[0].endswith("Req"):
                        protoIndexs["c2s"][code] = msgName
                    elif msgNameInfo[0].endswith("Resp"):
                        protoIndexs["s2c"][code] = msgName

def GenClientProtos(files):
    for file in files:
        fileName = io_utils.GetFileNameWithoutExtension(file)
        destFile = proto.config.clientOutPath + fileName + ".pb"
        cmd = "%sproto/bin/protoc.exe -I=%s --descriptor_set_out=%s %s" % (base.define.rootPath,proto.config.protoFilePath,destFile,file)
        os.system(cmd)

    filePath = proto.config.clientOutPath + "proto_index.lua"
    file = open(filePath,encoding="utf-8", mode="w")

    file.write("local indexData = {} \n")
    file.write("\n")

    file.write("indexData.recv =\n")
    file.write("{\n")
    for code,msgName in protoIndexs["s2c"].items():
        file.write("    [%s] = \"%s\",\n" % (code,msgName))
    file.write("}\n")

    file.write("\n")

    file.write("indexData.send =\n")
    file.write("{\n")
    for code,msgName in protoIndexs["c2s"].items():
        file.write("    [%s] = \"%s\",\n" % (code,msgName))
    file.write("}\n")

    file.write("\n")

    file.write("indexData.file =\n")
    file.write("{\n")
    for fileName in protoIndexs["file"]:
        file.write("    \"%s\",\n" % fileName)
    file.write("}\n")

    file.write("\n")

    file.write("return indexData")

    file.flush()
    file.close()

def GenCSProtos(files):
    for file in files:
        cmd = "%sproto/bin/3.5.1/protoc.exe -I=%s --csharp_out=%s %s" % (base.define.rootPath,proto.config.protoFilePath,proto.config.csOutPath,file)
        os.system(cmd)

    filePath = proto.config.csOutPath + "ProtoIndex.cs"
    file = open(filePath,encoding="utf-8", mode="w")

    file.write("using System.Collections.Generic;\n")

    file.write("public class ProtoIndex\n")
    file.write("{\n")

    file.write("    public readonly static Dictionary<string, string> recv = new Dictionary<string, string>\n")
    file.write("    {\n")
    for code,msgName in protoIndexs["s2c"].items():
        file.write("        {\"%s\",\"%s\"},\n" % (code,msgName))
    file.write("    };\n")

    file.write("\n")

    file.write("    public readonly static Dictionary<string, int> send = new Dictionary<string, int>\n")
    file.write("    {\n")
    for code,msgName in protoIndexs["c2s"].items():
        file.write("        {\"%s\",%s},\n" % (msgName,code))
    file.write("    };\n")

    file.write("}")

    file.flush()
    file.close()

    

def OnComplete():
    pass

def OnHelp():
    return "\
[proto]           生成协议"