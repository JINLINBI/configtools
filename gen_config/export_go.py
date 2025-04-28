import os

from utils import io_utils
from utils import string_utils

import gen_config.config
import gen_config.define

def Export(configParse):

    fileName = configParse.configName#io_utils.GetFileNameWithoutExtension(configParse.localPath)
    #filePath = gen_config.define.goOutPath + fileName + ".go"

    #io_utils.CreateFolderByFile(filePath)

   

    #file = open(filePath,encoding="utf-8", mode="w")

    #file.write("package config\n")

    for sheetData in iter(configParse.sheets):
        #file.write("\n")
        exportRules = configParse.exportRules[sheetData.name]["server"]
        WriteSheet(sheetData,exportRules,fileName)


def WriteSheet(sheetData,exportRules,fileName):
    filePath = gen_config.config.goOutPath + fileName + "/" + sheetData.name + ".go"
    io_utils.CreateFolderByFile(filePath)

    file = open(filePath,encoding="utf-8", mode="w")

    file.write("package %s\n" % sheetData.name)
    file.write("\n")

    structName = sheetData.name.title().replace("_","")

    file.write("type %s struct {\n" % structName)

    for _,fieldName in sheetData.fieldAttrsCol.items():
        fieldAttr = sheetData.fieldAttrs[fieldName]

        if fieldAttr.typeAttr.type == gen_config.define.FieldType.lua:
            continue
       
        file.write("    %s %s\n" % (fieldAttr.upperName,GetType(fieldAttr.typeAttr)))

    file.write("}\n")

    file.write("\n")
    file.write("var %s = []%s {\n" % (sheetData.name,structName))

    index = 0
    exportIndexs = {}
    for rowData in sheetData.fieldValues:
        index = index + 1
        fieldExportList = []

        for _,fieldName in sheetData.fieldAttrsCol.items():
            fieldAttr = sheetData.fieldAttrs[fieldName]
            if fieldAttr.typeAttr.type == gen_config.define.FieldType.lua:
                continue

            valueFormat = GetFieldFormat(rowData[fieldName],fieldAttr.typeAttr,"        ")
            fieldExportList.append( "        %s : %s" % ( fieldAttr.upperName,valueFormat ) )

        file.write( "    %s {\n%s\n%s},\n" % (structName,"\n".join(fieldExportList),"    "))

        for v in exportRules:
            key = GetExportKey(v["fields"],rowData)
            indexValue = "%s:%s" % (key,index)
            #if index % 10 == 0:indexValue += "\n    "
            indexKey = v["indexKey"]
            exist = indexKey in exportIndexs
            if exist == False:
                exportIndexs[indexKey] = []

            exportIndexs[indexKey].append(indexValue)


    file.write("}\n")   #配置数据写入完毕


    file.write("\n")
    file.write("func Get%sCount() int {\n" % structName)
    file.write("    return len(%s)\n" % sheetData.name)
    file.write("}\n")

    file.write("\n")
    file.write("func Get%sByINDEX(index int) (%s,bool) {\n" % (structName,structName))
    file.write("    if index >= len(%s) { return %s{}, false }\n" % (sheetData.name,structName))
    file.write("    return %s[index], true\n" % sheetData.name)
    file.write("}\n")

    for v in exportRules:
        indexKey = v["indexKey"]
        firstChat = indexKey[0]
        keys = indexKey.title().replace("_","")
        firstLowerKeys = firstChat + keys[1:]

        indexList = exportIndexs[indexKey]

        keyType = gen_config.define.FieldType.string
        if len(v["fields"]) == 1:
            fieldName  = v["fields"][0]
            configValue = rowData[fieldName]
            keyType = configValue.type

        file.write("\n")
        file.write("var %s = map[%s]int {\n    %s,\n}" % (firstLowerKeys,keyType,",".join(indexList) ))
        file.write("\n")

        file.write("func Get%sBy%s(key %s) (%s,bool) {\n" % (structName,keys,keyType,structName))
        file.write("    index,ok := %s[key]\n" % (firstLowerKeys))
        file.write("    return %s[index],ok\n" % sheetData.name)
        file.write("}\n")



    file.flush()
    file.close()


def GetExportKey(fieldList,rowData):
    if len(fieldList) == 1 :
        fieldName  = fieldList[0]
        configValue = rowData[fieldName]
        if configValue.type == gen_config.define.FieldType.int:
            return configValue.value
        elif configValue.type == gen_config.define.FieldType.string:
            return string_utils.FormatWrite(configValue.value)

    fieldValueList = []
    for fieldName in iter(fieldList):
        configValue = rowData[fieldName]
        value = "_"
        if configValue.type == gen_config.define.FieldType.int:
            value = str(configValue.value)
        elif configValue.type == gen_config.define.FieldType.string:
            return string_utils.FormatWrite(configValue.value)

        fieldValueList.append(value)
        
    return "\"%s\"" % "_".join(fieldValueList)

def GetType(typeAttr):
    if typeAttr.type == gen_config.define.FieldType.int:
        return "int"
    elif typeAttr.type == gen_config.define.FieldType.float:
        return "float32"
    elif typeAttr.type == gen_config.define.FieldType.string:
        return "string"
    elif typeAttr.type == gen_config.define.FieldType.bool:
        return "bool"
    elif typeAttr.type == gen_config.define.FieldType.list:
        return "[]" + GetType( typeAttr.opts["type"] )
    elif typeAttr.type == gen_config.define.FieldType.dict:
        key = GetType(typeAttr.opts["key"])
        value = GetType(typeAttr.opts["value"])
        return "map[%s]%s" % (key,value)
    elif typeAttr.type == gen_config.define.FieldType.mix:
        return "interface{}"

def GetFieldFormat(configValue,typeAttr,space):
    if configValue.type == gen_config.define.FieldType.int:
        return str(configValue.value) + ","
    elif configValue.type == gen_config.define.FieldType.float:
        return str(configValue.value) + ","
    elif configValue.type == gen_config.define.FieldType.string:
        return string_utils.FormatWrite(configValue.value)
    elif configValue.type == gen_config.define.FieldType.bool:
        if configValue.value:
            return "true,"
        else:
            return "false," 
    elif configValue.type == gen_config.define.FieldType.list:
        fieldExports = []
        valueType = typeAttr.opts["type"]
        typeStr = GetType(valueType)
        
        if valueType.type == gen_config.define.FieldType.mix:
            valueType = typeAttr

        for v in configValue.value:
            value = GetFieldFormat(v,valueType,space + "    ")
            fieldExports.append( "%s" % (value) )

        return "[]%s{\n%s%s\n%s}," % (typeStr,space + "    ","".join(fieldExports),space)
    elif configValue.type == gen_config.define.FieldType.dict:
        fieldExports = []
        typeStr = GetType(typeAttr)

        valueType = typeAttr.opts["value"]
        if valueType.type == gen_config.define.FieldType.mix:
            valueType = typeAttr

        for keyName in configValue.opts["valueList"]:
            keValue = configValue.value[keyName]
            key   = GetDictKey(keValue["key"])
            value = GetFieldFormat(keValue["value"],valueType,space + "    ")
            fieldExports.append("%s%s : %s\n" % (space + "    ",key,value))
            
        return "%s {\n%s%s}," % (typeStr,"".join(fieldExports),space)




def GetDictKey(configValue):
    if configValue.type == gen_config.define.FieldType.int:
        return configValue.value
    elif configValue.type == gen_config.define.FieldType.string:
        return string_utils.FormatWrite(configValue.value)