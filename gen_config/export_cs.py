import os

from utils import io_utils
from utils import string_utils

import gen_config.config
import gen_config.define

from gen_config import export_json

def Export(configParse):
    fileName = configParse.configName

    export_json.Export(gen_config.config.csDataOutPath,configParse,gen_config.define.ExportTarget.cs)

    exportSheetDatas = []
    for sheetData in configParse.sheetDatas:
        if configParse.parseExport.IsExportSheetTarget(sheetData.name,gen_config.define.ExportTarget.cs):
            exportSheetDatas.append(sheetData)


    filePath = gen_config.config.csCodeOutPath + configParse.configName + ".cs"

    io_utils.CreateFolderByFile(filePath)

    file = open(filePath,encoding="utf-8", mode="w")

    file.write("using SimpleJSON;\n")
    file.write("using System.Collections.Generic;\n")

    file.write("public class %s : CfgBase\n" % (configParse.configName))
    file.write("{\n")


    for sheetData in exportSheetDatas:
        WriteSheet(file,sheetData,fileName)

    WriteGetSheet(file,configParse,exportSheetDatas)


    file.write("}")

    file.flush()
    file.close()




    # WriteGetSheet(configParse,exportSheetDatas)

    # for sheetData in exportSheetDatas:
    #     WriteSheet(sheetData,fileName)


def WriteGetSheet(file,configParse,exportSheetDatas):
    #filePath = gen_config.config.csCodeOutPath + configParse.configName + ".cs"

    #io_utils.CreateFolderByFile(filePath)

    #file = open(filePath,encoding="utf-8", mode="w")

    #file.write("using SimpleJSON;\n")
    #file.write("using System.Collections.Generic;\n")


    #file.write("public class %s : CfgBase\n" % (configParse.configName))
    #file.write("{\n")
    file.write("    Dictionary<string, CfgDetail[]>  datas = new Dictionary<string, CfgDetail[]>();\n")
    file.write("    Dictionary<string, Dictionary<string, Dictionary<object, CfgDetail[]>>> dataIndex = new Dictionary<string, Dictionary<string, Dictionary<object, CfgDetail[]>>>();\n")

    #加载方法
    file.write("    public override void Load(JSONNode buf)\n")
    file.write("    {\n")

    for i,sheetData in enumerate(exportSheetDatas):
        if i != 0:
            file.write("\n")

        exportInfos = configParse.parseExport.GetExportInfo(sheetData.name,gen_config.define.ExportTarget.cs)

        file.write("        datas.Add(\"%s\", new CfgDetail[buf[\"%s\"][\"data\"].Count]);\n" % (sheetData.name,sheetData.name))
        file.write("        dataIndex.Add(\"%s\", new Dictionary<string, Dictionary<object, CfgDetail[]>>());\n\n" % (sheetData.name))

        file.write("        dataIndex[\"%s\"].Add(\"index\",new Dictionary<object, CfgDetail[]>());\n\n" % (sheetData.name))
      
        file.write("        for (int i = 0; i < buf[\"%s\"][\"data\"].Count; i++)\n" % (sheetData.name))
        file.write("        {\n")
        file.write("            JSONNode item = buf[\"%s\"][\"data\"][i];\n" % (sheetData.name))
        file.write("            %s cfg = new %s(item);\n" % ((sheetData.name,sheetData.name)))
        file.write("            datas[\"%s\"][i] = cfg;\n" % (sheetData.name))
        file.write("            CfgDetail[] cfgDetails = new CfgDetail[] { cfg };\n")
        file.write("            dataIndex[\"%s\"][\"index\"].Add(i,cfgDetails);\n" % (sheetData.name))
        file.write("        }\n")

        file.write("\n")

        

        for v in exportInfos["exportInfos"]:
            indexKey = v["indexKey"]
            keys = indexKey.replace(",","_")

            keyRead = None
            if len(v["fieldTypes"]) == 1 and v["fieldTypes"][0] == gen_config.define.FieldType.int:
                keyRead = "int.Parse(v.Key)"
            else:
                keyRead = "(string)v.Key"

            file.write("        dataIndex[\"%s\"].Add(\"%s\",new Dictionary<object, CfgDetail[]>());\n" % (sheetData.name,keys))
            file.write("        foreach(var v in buf[\"%s\"][\"index\"][\"%s\"])\n" % (sheetData.name,keys))
            file.write("        {\n")

            file.write("            CfgDetail[] cfgDetails;\n")
            file.write("            if(v.Value.IsArray)\n")
            file.write("            {\n")
            file.write("                cfgDetails = new CfgDetail[v.Value.Count];\n")

            file.write("                for (int i = 0; i < v.Value.Count; i++)\n")
            file.write("                {\n")
            file.write("                    cfgDetails[i] = datas[\"%s\"][v.Value[i]];\n" % sheetData.name)
            file.write("                }\n")

            file.write("            }\n")
            file.write("            else\n")
            file.write("            {\n")
            file.write("                cfgDetails = new CfgDetail[]{datas[\"%s\"][v.Value]};\n" % sheetData.name)
            file.write("            }\n")
            file.write("            dataIndex[\"%s\"][\"%s\"].Add(%s, cfgDetails);\n" % (sheetData.name,keys,keyRead))
            
            file.write("        }\n")


    file.write("    }\n")


    #获取方法
    file.write("\n")
    file.write("    public override int Get(string sheetName, string keyIndex, object key,out CfgDetail[] cfgDetails)\n")
    file.write("    {\n")
    file.write("        cfgDetails = null;\n")
    file.write("        if (!dataIndex.ContainsKey(sheetName))\n")
    file.write("        {\n")
    file.write("            return 1;\n")
    file.write("        }\n")
    file.write("\n")
    file.write("        if (!dataIndex[sheetName].ContainsKey(keyIndex))\n")
    file.write("        {\n")
    file.write("            return 2;\n")
    file.write("        }\n")
    file.write("\n")
    file.write("        if (!dataIndex[sheetName][keyIndex].TryGetValue(key, out cfgDetails))\n")
    file.write("        {\n")
    file.write("            return 3;\n")
    file.write("        }\n")
    file.write("        else\n")
    file.write("        {\n")
    file.write("            return 0;\n")
    file.write("        }\n")
    file.write("    }\n")


    #获取数量
    file.write("\n")
    file.write("    public override int GetNum(string sheetName)\n")
    file.write("    {\n")

    file.write("        if(datas.ContainsKey(sheetName))\n")
    file.write("        {\n")
    file.write("            return datas[sheetName].Length;\n")
    file.write("        }\n")
    file.write("        return 0;\n")
    file.write("    }\n")


    # file.write("}")

    # file.flush()
    # file.close()

def WriteSheet(file,sheetData,fileName):
    #filePath = gen_config.config.csCodeOutPath + fileName + "." + sheetData.name + ".cs"

    #io_utils.CreateFolderByFile(filePath)

    #file = open(filePath,encoding="utf-8", mode="w")

    #file.write("using SimpleJSON;\n")
    #file.write("using System.Collections.Generic;\n")
    
    file.write("    public class %s : CfgDetail\n" % (sheetData.name))
    file.write("    {\n")

    for _,fieldName in sheetData.fieldAttrsCol.items():
        typeFormat = GetTypeFormat(sheetData.fieldAttrs[fieldName].typeAttr)
        if typeFormat != None:
            file.write("        public readonly %s %s;\n" % (typeFormat,fieldName))


    file.write("\n")


    file.write("        public %s(JSONNode buf)\n" % (sheetData.name))
    file.write("        {\n")

    maxAttrNum = len(sheetData.fieldAttrsCol)
    for i,fieldName in sheetData.fieldAttrsCol.items():
        readFormat = GetReadFormat(1,"            ",fieldName,"buf[\"%s\"]" % fieldName,sheetData.fieldAttrs[fieldName].typeAttr)
        if readFormat != None:
            file.write("            %s = %s%s" % (fieldName,readFormat,("\n" if i == maxAttrNum - 1 else "\n")))

    file.write("        }\n")

    file.write("    }\n")

    file.write("\n")


    # file.flush()
    # file.close()


def GetTypeFormat(fieldTypeAttr):
    fieldType = fieldTypeAttr.type
    if fieldType == gen_config.define.FieldType.int:
        return "int"
    elif fieldType == gen_config.define.FieldType.float:
        return "float"
    elif fieldType == gen_config.define.FieldType.string:
        return "string"
    elif fieldType == gen_config.define.FieldType.bool:
        return "bool"
    elif fieldType == gen_config.define.FieldType.list:
        return "List<%s>" % GetTypeFormat(fieldTypeAttr.opts["type"])
    elif fieldType == gen_config.define.FieldType.dict:
        return "Dictionary<%s,%s>" % (GetTypeFormat(fieldTypeAttr.opts["key"]),GetTypeFormat(fieldTypeAttr.opts["value"]))
    elif fieldType == gen_config.define.FieldType.mix:
        return "object"
    elif fieldType == gen_config.define.FieldType.lua:
        return None
    
def GetReadFormat(depthIndex,startswith,fieldName,fieldRead,fieldTypeAttr):
    fieldType = fieldTypeAttr.type
    if fieldType == gen_config.define.FieldType.int:
        return "(int)%s;" % fieldRead
    elif fieldType == gen_config.define.FieldType.float:
        return "(float)%s;" % fieldRead
    elif fieldType == gen_config.define.FieldType.string:
        return "(string)%s;" % fieldRead
    elif fieldType == gen_config.define.FieldType.bool:
        return "(bool)%s;" % fieldRead
    elif fieldType == gen_config.define.FieldType.list:
        loopIndexName = "v%s" % depthIndex
        valName = "val%s" % depthIndex
        readFormat = "new List<%s>();\n" % GetTypeFormat(fieldTypeAttr.opts["type"])
        readFormat += "%sforeach (var %s in %s)\n" % (startswith,loopIndexName,fieldRead)
        readFormat += "%s{\n" % startswith
        readFormat += "%s    var %s = %s\n" % (startswith,valName,GetReadFormat(depthIndex + 1,startswith + "    ",valName,loopIndexName + ".Value",fieldTypeAttr.opts["type"] ))
        readFormat += "%s    %s.Add(val%s);\n" % (startswith,fieldName,depthIndex)
        readFormat += "%s}" % startswith
        return readFormat
    elif fieldType == gen_config.define.FieldType.dict:
        loopIndexName = "v%s" % depthIndex
        keyName = "key%s" % depthIndex
        valName = "val%s" % depthIndex
        readFormat = "new Dictionary<%s,%s>();\n" % (GetTypeFormat(fieldTypeAttr.opts["key"]),GetTypeFormat(fieldTypeAttr.opts["value"]))
        readFormat += "%sforeach (var %s in %s)\n" % (startswith,loopIndexName,fieldRead)
        readFormat += "%s{\n" % startswith
        readFormat += "%s    %s %s = %s.Key;\n" % (startswith,GetTypeFormat(fieldTypeAttr.opts["key"]),keyName,loopIndexName)
        readFormat += "%s    %s %s = %s\n" % (startswith,GetTypeFormat(fieldTypeAttr.opts["value"]),valName,GetReadFormat(depthIndex + 1,startswith + "    ",valName,loopIndexName + ".Value",fieldTypeAttr.opts["value"] ))
        readFormat += "%s    %s.Add(key%s,val%s);\n" % (startswith,fieldName,depthIndex,depthIndex)
        readFormat += "%s}" % startswith
        return readFormat
    elif fieldType == gen_config.define.FieldType.mix:
        return "ParseValue(%s);" % fieldRead
    elif fieldType == gen_config.define.FieldType.lua:
        return None