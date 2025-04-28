import os

from utils import io_utils
from utils import string_utils
import gen_config.config
import gen_config.define

def Export(exportPath,configParse,exportTarget):
    fileName = configParse.configName
    filePath = exportPath + fileName + ".json"

    io_utils.CreateFolderByFile(filePath)

    file = open(filePath,encoding="utf-8", mode="w")

    file.write("{\n")

    exportSheetDatas = []
    for sheetData in configParse.sheetDatas:
        if configParse.parseExport.IsExportSheetTarget(sheetData.name,exportTarget):
            exportSheetDatas.append(sheetData)

    maxLen = len(exportSheetDatas)
    for i,sheetData in enumerate(exportSheetDatas):
        if i != 0:
            file.write("\n")
            
        exportInfos = configParse.parseExport.GetExportInfo(sheetData.name,exportTarget)

        file.write("    \"%s\":\n" % sheetData.name)
        file.write("    {\n")

        WriteSheet(file,sheetData,exportInfos["exportInfos"],exportInfos["params"],fileName)

        file.write("    }%s\n" % ("" if i == maxLen - 1 else ","))

    # file.write("\n")
    # file.write("local sheetFunc = \n{")
    # for sheetData in exportSheetDatas:
    #     file.write("\n")
    #     exportInfos = configParse.parseExport.GetExportInfo(sheetData.name,gen_config.define.ExportTarget.lua)
    #     WriteGetSheet(file,exportInfos["exportInfos"],sheetData.name)



    file.write("}\n")


    file.flush()
    file.close()

def WriteSheet(file,sheetData,exportInfos,exportParams,fileName):
    fieldKeys = {} #[]
    checkIndexKeys = {}
    keyToIndexValue = {}

    exportIndexs = {}
    writeDatas = []
    for index,rowData in enumerate(sheetData.fieldValues):
        fieldExportList = []
        for _,fieldName in sheetData.fieldAttrsCol.items():
            if sheetData.fieldAttrs[fieldName].typeAttr.type == gen_config.define.FieldType.lua:
                continue
            valueFormat = GetFieldFormat(fileName,rowData[fieldName],sheetData.fieldAttrs[fieldName])
            fieldExportList.append( "\"%s\":%s" % ( fieldName,valueFormat ) )

        writeDatas.append("{%s}" % ",".join(fieldExportList))

        
        for v in exportInfos:
            indexKey = v["indexKey"]
            
            key = GetExportKey(v["fields"],rowData)
            if not (indexKey in checkIndexKeys):
                checkIndexKeys[indexKey] = {}
                fieldKeys[indexKey] = []
                keyToIndexValue[indexKey] = {}
            
            if not (key in checkIndexKeys[indexKey]):
                checkIndexKeys[indexKey][key] = True
                fieldKeys[indexKey].append(key)
                keyToIndexValue[indexKey][key] = []

            keyToIndexValue[indexKey][key].append(str(index))
            
    for v in exportInfos:
        indexKey = v["indexKey"]
        if not (indexKey in exportIndexs):
            exportIndexs[indexKey] = []

        if  indexKey in fieldKeys:
            for key in fieldKeys[indexKey]:
                if v["group"]:
                    exportIndexs[indexKey].append("\"%s\":[%s]" % (key,",".join(keyToIndexValue[indexKey][key])))
                else:
                    exportIndexs[indexKey].append("\"%s\":%s" % (key,keyToIndexValue[indexKey][key][0]))
                        

    
    file.write("        \"data\":\n")
    file.write("        [\n")
    WriteSheetData(file,exportParams["mode"],writeDatas,sheetData,fileName)
    file.write("        ],\n")
    

    file.write("        \"index\":\n")
    file.write("        {\n")
    WriteExportIndex(file,fileName,sheetData,exportInfos,exportIndexs)
    file.write("        }\n")


def WriteSheetData(file,mode,writeDatas,sheetData,fileName):
    maxLen = len(writeDatas)
    for i, data in enumerate(writeDatas):
        file.write("           %s%s\n" % (data,"" if i == maxLen - 1 else ","))

def WriteExportIndex(file,fileName,sheetData,exportInfos,exportIndexs):
    maxLen = len(exportInfos)
    for i, v in enumerate(exportInfos):
        indexKey = v["indexKey"]
        keys = indexKey.replace(",","_")

        indexList = None
        if indexKey in exportIndexs:
            indexList = exportIndexs[indexKey]
        else:
            indexList = []

        file.write("            \"%s\":\n" % keys)
        file.write("            {\n")
        file.write("                %s\n" % ",".join(indexList))
        file.write("            }%s\n" % ("" if i == maxLen - 1 else ","))

def GetExportKey(fieldList,rowData):
    if len(fieldList) == 1 :
        fieldName  = fieldList[0]
        configValue = rowData[fieldName]
        return configValue.value
    else:
        fieldValueList = []
        for fieldName in iter(fieldList):
            configValue = rowData[fieldName]
            value = configValue.value
            fieldValueList.append(str(value))

        return "%s" % "_".join(fieldValueList)

def GetFieldFormat(fileName,configValue,fieldAttr):
    if configValue.type == gen_config.define.FieldType.int:
        return str(configValue.value)
    elif configValue.type == gen_config.define.FieldType.float:
        return str(configValue.value)
    elif configValue.type == gen_config.define.FieldType.string:
        fieldValue = string_utils.FormatDQuote(configValue.value)
        return fieldValue
    elif configValue.type == gen_config.define.FieldType.bool:
        if configValue.value:
            return "true"
        else:
            return "false"
    elif configValue.type == gen_config.define.FieldType.list:
        fieldExports = []
        for value in configValue.value:
            fieldExports.append( GetFieldFormat(fileName,value,fieldAttr) )
        return "[%s]" % ",".join(fieldExports)
    elif configValue.type == gen_config.define.FieldType.dict:
        fieldExports = []
        for keyName in configValue.opts["valueList"]:
            keValue = configValue.value[keyName]
            key = GetDictKey(keValue["key"])
            value = GetFieldFormat(fileName,keValue["value"],fieldAttr)
            fieldExports.append("\"%s\":%s" % (key,value))
            
        return "{%s}" % ",".join(fieldExports)
    elif configValue.type == gen_config.define.FieldType.lua:
        return configValue.value

def GetDictKey(configValue):
    if configValue.type == gen_config.define.FieldType.int:
        return configValue.value
    elif configValue.type == gen_config.define.FieldType.string:
        return string_utils.FormatSQuote(configValue.value)