import os

from utils import io_utils
from utils import string_utils
import gen_config.config
import gen_config.define

def Export(configParse):
    fileName = configParse.configName
    filePath = gen_config.config.luaOutPath + fileName + ".lua"

    io_utils.CreateFolderByFile(filePath)

    file = open(filePath,encoding="utf-8", mode="w")

    file.write("local %s = {\n" % fileName)

    exportSheetDatas = []
    for sheetData in configParse.sheetDatas:
        if configParse.parseExport.IsExportSheetTarget(sheetData.name,gen_config.define.ExportTarget.lua):
            exportSheetDatas.append(sheetData)

    for sheetData in exportSheetDatas:
        file.write("\n")
        exportInfos = configParse.parseExport.GetExportInfo(sheetData.name,gen_config.define.ExportTarget.lua)
        WriteSheet(file,sheetData,exportInfos["exportInfos"],exportInfos["params"],fileName)

    # file.write("\n")
    # file.write("local sheetFunc = \n{")
    # for sheetData in exportSheetDatas:
    #     file.write("\n")
    #     exportInfos = configParse.parseExport.GetExportInfo(sheetData.name,gen_config.define.ExportTarget.lua)
    #     WriteGetSheet(file,exportInfos["exportInfos"],sheetData.name)
    # file.write("}\n")

    # WriteGet(file,fileName)

    file.write("}\n")
    file.write("\n")

    file.write("return " + fileName)

    file.flush()
    file.close()

def WriteSheet(file,sheetData,exportInfos,exportParams,fileName):
    file.write("--%s\n" % sheetData.name)
    file.write("    %s_num = %s,\n" % (sheetData.name,len( sheetData.fieldValues )))

    fieldKeys = {} #[]
    checkIndexKeys = {}
    keyToIndexValue = {}

    exportIndexs = {}
    writeDatas = []
    for index,rowData in enumerate(sheetData.fieldValues):
        fieldExportList = []
        for _,fieldName in sheetData.fieldAttrsCol.items():
            valueFormat = GetFieldFormat(fileName,rowData[fieldName],sheetData.fieldAttrs[fieldName])
            fieldExportList.append( "%s=%s" % ( fieldName,valueFormat ) )

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

            keyToIndexValue[indexKey][key].append(str(index + 1))
            
    for v in exportInfos:
        indexKey = v["indexKey"]
        if not (indexKey in exportIndexs):
            exportIndexs[indexKey] = []

        if  indexKey in fieldKeys:
            for key in fieldKeys[indexKey]:
                if v["group"]:
                    exportIndexs[indexKey].append("[%s]={%s}" % (key,",".join(keyToIndexValue[indexKey][key])))
                else:
                     exportIndexs[indexKey].append("[%s]=%s" % (key,keyToIndexValue[indexKey][key][0]))
                        

    WriteSheetData(file,exportParams["mode"],writeDatas,sheetData,fileName)
    WriteExportIndex(file,fileName,sheetData,exportInfos,exportIndexs)

def WriteSheetData(file,mode,writeDatas,sheetData,fileName):
    if mode == "index":
        file.write("    %s = {\n" % sheetData.name)
        # file.write("    {\n")
        for index, data in enumerate(writeDatas):
            file.write("        [%s] = %s,\n" % (index + 1,data))
        file.write("    },\n")

        # file.write("\n")
        # file.write("function %s.%s_index(index)\n" % (fileName,sheetData.name))
        # file.write("    return %s[index]\n" % sheetData.name)
        # file.write("end\n")
    elif mode == "func":
        file.write("local %s ={}\n" % sheetData.name)
        file.write("local function %s_func(index)\n" % sheetData.name)
        for index, data in enumerate(writeDatas):
            file.write("    if index == %s then return %s end\n" % (index + 1,data))
        file.write("end\n")

        file.write("\n")
        file.write("function %s.%s_index(index)\n" % (fileName,sheetData.name))
        file.write("    local data = %s[index]\n" % sheetData.name)
        file.write("    if data then return data end\n")
        file.write("    data = %s_func(index)\n" % sheetData.name)
        file.write("    if not data then return nil end\n")
        file.write("    %s[index] = data\n" % sheetData.name)
        file.write("    return data\n")
        file.write("end\n")
    elif mode == "str":
        file.write("local %s ={}\n" % sheetData.name)
        file.write("local %s_str =\n" % sheetData.name)
        file.write("{\n")
        for index, data in enumerate(writeDatas):
            file.write("    [%s] = [[%s]],\n" % (index + 1,data))
        file.write("}\n")

        file.write("\n")
        file.write("function %s.%s_index(index)\n" % (fileName,sheetData.name))
        file.write("    local data = %s[index]\n" % sheetData.name)
        file.write("    if data then return data end\n")
        file.write("    local dataStr = %s_str[index]\n" % sheetData.name)
        file.write("    if not dataStr then return nil end\n")
        file.write("    data = loadstring(string.format('return %s',dataStr))()\n")
        file.write("    %s_str[index] = nil\n" % sheetData.name)
        file.write("    %s[index] = data\n" % sheetData.name)
        file.write("    return data\n")
        file.write("end\n")
    
    # file.write("\n")
    # file.write("function %s.%s_set(index,data)\n" % (fileName,sheetData.name))
    # file.write("    %s[index] = data\n" % sheetData.name)
    # file.write("end\n")

    # file.write("\n")
    # file.write("function %s.%s_num()\n" % (fileName,sheetData.name))
    # file.write("    return %s_num\n" % sheetData.name)
    # file.write("end\n")

def WriteExportIndex(file,fileName,sheetData,exportInfos,exportIndexs):
    for v in exportInfos:
        indexKey = v["indexKey"]
        keys = indexKey.replace(",","_")

        indexList = None
        if indexKey in exportIndexs:
            indexList = exportIndexs[indexKey]
        else:
            indexList = []

        # file.write("\n")
        file.write("    %s_%s = {\n        %s\n    },\n" % (sheetData.name,keys,",".join(indexList) ))
        # file.write("\n")
        
        # if v["group"]:
        #     file.write("local %s_%s_data = {}\n" % (sheetData.name,keys))
        #     file.write("function %s.%s_%s(key)\n" % (fileName,sheetData.name,keys))
        #     file.write("    if %s_%s_data[key] then\n" % (sheetData.name,keys))
        #     file.write("        return %s_%s_data[key]\n" % (sheetData.name,keys))
        #     file.write("    end\n")
            

        #     file.write("    local indexs = %s_%s[key]\n" % (sheetData.name,keys))
        #     file.write("    local datas = {}\n")
        #     file.write("    for _,index in ipairs(indexs) do\n")
        #     file.write("        table.insert(datas,%s.%s_index(index))\n" % (fileName,sheetData.name))
        #     file.write("    end\n")
            
        #     file.write("      %s_%s_data[key] = datas\n" % (sheetData.name,keys))
        #     file.write("     return datas\n")
        #     file.write("end\n")
        # else:
        #     file.write("function %s.%s_%s(key)\n" % (fileName,sheetData.name,keys))
        #     file.write("    local index = %s_%s[key]\n" % (sheetData.name,keys))
        #     file.write("    return %s.%s_index(index)\n" % (fileName,sheetData.name))
        #     file.write("end\n")

        

def WriteGetSheet(file,exportRules,sheetName):
    # file.write("    [\"%s\"] = \n    {\n" % (sheetName))

    # file.write("        [\"index\"] = \"%s_index\",\n" % (sheetName) )
    # file.write("        [\"@num\"] = \"%s_num\",\n" % (sheetName))
    # file.write("        [\"@set\"] = \"%s_set\",\n" % (sheetName))

    for v in exportRules:
        file.write("        [\"%s\"] = \"%s_%s\",\n" % ( v["indexKey"],sheetName,v["indexKey"].replace(",","_")) )
    
    # file.write("    },\n")

def WriteGet(file,fileName):
    file.write("\n")
    file.write("function %s.Get(sheetName,keyIndex,key)\n" % fileName)
    file.write("    local funcIndexs = sheetFunc[sheetName]\n")
    file.write("    if not funcIndexs then return nil,1 end\n")
    file.write("    local funName = funcIndexs[keyIndex]\n")
    file.write("    if not funName then return nil,2 end\n")
    file.write("    return %s[funName](key),nil\n" % fileName)
    file.write("end\n")

    file.write("\n")
    file.write("function %s.Set(sheetName,index,data)\n" % fileName)
    file.write("    if not index or not data then return false end\n")
    file.write("    local funcIndexs = sheetFunc[sheetName]\n")
    file.write("    if not funcIndexs then return false end\n")
    file.write("    local funName = funcIndexs[\"@set\"]\n")
    file.write("    %s[funName](index,data)\n" % fileName)
    file.write("    return true\n")

    file.write("end\n")

    file.write("\n")
    file.write("function %s.GetNum(sheetName)\n" % fileName)
    file.write("    local funcIndexs = sheetFunc[sheetName]\n")
    file.write("    if not funcIndexs then return 0 end\n")
    file.write("    local funName = funcIndexs[\"@num\"]\n")
    file.write("    return %s[funName]()\n" % fileName)
    file.write("end\n")

def GetExportKey(fieldList,rowData):
    if len(fieldList) == 1 :
        fieldName  = fieldList[0]
        configValue = rowData[fieldName]
        if configValue.type == gen_config.define.FieldType.int:
            return configValue.value
        elif configValue.type == gen_config.define.FieldType.string:
            return string_utils.FormatSQuote(configValue.value)

    fieldValueList = []
    for fieldName in iter(fieldList):
        configValue = rowData[fieldName]
        value = None
        if configValue.type == gen_config.define.FieldType.int:
            value = str(configValue.value)
        elif configValue.type == gen_config.define.FieldType.string:
            value = string_utils.FormatWithoutQuote(configValue.value)

        fieldValueList.append(value)
        
    return "\'%s\'" % "_".join(fieldValueList)

def GetFieldFormat(fileName,configValue,fieldAttr):
    if configValue.type == gen_config.define.FieldType.int:
        return str(configValue.value)
    elif configValue.type == gen_config.define.FieldType.float:
        return str(configValue.value)
    elif configValue.type == gen_config.define.FieldType.string:
        fieldValue = string_utils.FormatDQuote(configValue.value)
        if gen_config.define.i18n and fieldAttr.i18n:
            return "CTI18N(\"%s\",\"%s\",%s)" % (fileName,string_utils.GetMd5ByLen(configValue.value),fieldValue)
        else:
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
        return "{%s}" % ",".join(fieldExports)
    elif configValue.type == gen_config.define.FieldType.dict:
        fieldExports = []
        for keyName in configValue.opts["valueList"]:
            keValue = configValue.value[keyName]
            key = GetDictKey(keValue["key"])
            value = GetFieldFormat(fileName,keValue["value"],fieldAttr)
            fieldExports.append("[%s]=%s" % (key,value))
            
        return "{%s}" % ",".join(fieldExports)
    elif configValue.type == gen_config.define.FieldType.lua:
        return configValue.value

def GetDictKey(configValue):
    if configValue.type == gen_config.define.FieldType.int:
        return configValue.value
    elif configValue.type == gen_config.define.FieldType.string:
        return string_utils.FormatSQuote(configValue.value)