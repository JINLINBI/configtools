import gen_config.define
import gen_config.utils

def ParseValue(value,typeAttr,error):
    configValue = None
    
    if typeAttr.type == gen_config.define.FieldType.int:
        configValue = ParseInt(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.float:
        configValue = ParseFloat(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.string:
        configValue = ParseString(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.bool:
        configValue = ParseBool(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.lua:
        configValue = ParseLua(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.mix:
        configValue = ParseMix(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.list:
        configValue = ParseList(value,typeAttr,error)
    elif typeAttr.type == gen_config.define.FieldType.dict:
        configValue = ParseDict(value,typeAttr,error)
    
    if configValue.value == None:
        error("解析数据异常，类型不匹配[目标类型:%s][配置数据:%s]" % (typeAttr.type,value))
    
    return configValue


def ParseInt(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.int
    if value == "":
        configValue.value = 0
    else:
        configValue.value = gen_config.utils.GetInt(value)
    return configValue

def ParseFloat(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.float
    if value == "":
        configValue.value = 0.0
    else:
        configValue.value = gen_config.utils.GetFloat(value)
    return configValue

def ParseString(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.string
    configValue.value = str( gen_config.utils.GetValue(value) )
    if configValue.value.find("\n") != -1:
        configValue.value = str.replace(configValue.value,'\n','\\n')
    return configValue

def ParseBool(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.bool
    if value == "":
        configValue.value = False
    else:
        configValue.value = gen_config.utils.GetBool(value)
    return configValue

def ParseLua(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.lua
    configValue.value = value
    return configValue

def ParseMix(value,typeAttr,error):
    mixTypeAttr,newValue = GetValueType(value,True,error)
    if newValue == None:
        newValue = value
    configValue = ParseValue(newValue,mixTypeAttr,error)
    return configValue

def ParseList(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.list
    configValue.value = []

    if value == "":
        return configValue
    
    if value.find(",\n") != -1:
        value = str.replace(value,',\n',',')

    valueTypeAttr = typeAttr.opts["type"]

    if gen_config.define.IsBaseFieldType(valueTypeAttr.type):
        splitDatas = SplitData(value,False,error)
        for v in splitDatas:
            configValue.value.append(ParseValue(v,valueTypeAttr,error))
    elif valueTypeAttr.type == gen_config.define.FieldType.list:
        splitDatas = SplitData(value,True,error)
        for v in splitDatas:
            configValue.value.append(ParseValue(v,valueTypeAttr,error))
    elif valueTypeAttr.type == gen_config.define.FieldType.dict:
        splitDatas = SplitData(value,True,error)
        for v in splitDatas:
            configValue.value.append(ParseValue(v,valueTypeAttr,error))
    elif valueTypeAttr.type == gen_config.define.FieldType.mix:
        _,_ = GetValueType(value,False,error)
        splitDatas = SplitData(value,False,error)
        for v in splitDatas:
            data = v
            if data != "":
                mixTypeAttr,newValue = GetValueType(data,False,error)

                if newValue == None:
                    newValue = data

                newDataLen = len(newValue)
                if newValue[0] == "{" and newValue[newDataLen-1] == "}": 
                    newValue = newValue[1:newDataLen-1]
                        
                if newValue != "":
                    configValue.value.append(ParseValue(newValue,mixTypeAttr,error))
    return configValue

def ParseDict(value,typeAttr,error):
    configValue = gen_config.define.ConfigValue()
    configValue.type = gen_config.define.FieldType.dict
    configValue.value = {}
    configValue.opts["valueList"] = []

    if value == "":
        return configValue
    
    if value.find(",\n") != -1:
        value = str.replace(value,',\n',',')

    keyTypeAttr = typeAttr.opts["key"]
    valueTypeAttr = typeAttr.opts["value"]

    if gen_config.define.IsBaseFieldType(valueTypeAttr.type):
        keyValues = SplitData(value,False,error)

        for v in keyValues:
            dictKeyStr,dictValueStr = GetDict(v)
            if not dictKeyStr:
                error("解析数据异常，dict不存在key值[目标类型:%s][配置数据:%s]" % (typeAttr.type,v))

            dictKey = ParseValue(dictKeyStr,keyTypeAttr,error)
            dictValue = ParseValue(dictValueStr,valueTypeAttr,error)

            if dictKey.value in configValue.value:
                error("解析数据异常，dict重复定义元素[%s]" % (v) )

            configValue.value[dictKey.value] = {"key":dictKey,"value":dictValue}
            configValue.opts["valueList"].append(dictKey.value)
    elif valueTypeAttr.type == gen_config.define.FieldType.list:
        splitDatas = SplitData(value,False,error)

        for v in splitDatas:
            dictKeyStr,dictValueStr = GetDict(v)

            if not dictKeyStr:
                error("解析数据异常，dict不存在key值[目标类型:%s][配置数据:%s]" % (typeAttr.type,v))

            valueLen = len(dictValueStr)
            if dictValueStr[0] != "{" or dictValueStr[valueLen-1] != "}":
                error("解析数据异常，数据结构错误[%s](首尾应该是{})" % (dictValueStr) )
            elif valueLen > 2 and ( dictValueStr[1] == "," or dictValueStr[valueLen-2] == ","):
                error("解析数据异常，首尾不应该出现逗号[%s]" % (dictValueStr) )
            else:
                dictValueStr = dictValueStr[1:valueLen-1]

            dictKey = ParseValue(dictKeyStr,keyTypeAttr,error)
            dictValue = ParseValue(dictValueStr,valueTypeAttr,error)

            if dictKey.value in configValue.value:
                error("解析数据异常，dict重复定义元素[%s]" % (v) )

            configValue.value[dictKey.value] = {"key":dictKey,"value":dictValue}
            configValue.opts["valueList"].append(dictKey.value)
    elif valueTypeAttr.type == gen_config.define.FieldType.dict:
        splitDatas = SplitData(value,False,error)
        for v in splitDatas:
            dictKeyStr,dictValueStr = GetDict(v)

            if not dictKeyStr:
                error("解析数据异常，dict不存在key值[目标类型:%s][配置数据:%s]" % (typeAttr.type,v))

            valueLen = len(dictValueStr)
            if dictValueStr[0] != "{" or dictValueStr[valueLen-1] != "}":
                error("解析数据异常，数据结构错误[%s](首尾应该是{})" % (dictValueStr) )
            elif valueLen > 2 and ( dictValueStr[1] == "," or dictValueStr[valueLen-2] == ","):
                error("解析数据异常，首尾不应该出现逗号[%s]" % (dictValueStr) )
            else:
                dictValueStr = dictValueStr[1:valueLen-1]

            dictKey = ParseValue(dictKeyStr,keyTypeAttr,error)
            dictValue = ParseValue(dictValueStr,valueTypeAttr,error)

            if dictKey.value in configValue.value:
                error("解析数据异常，dict重复定义元素[%s]" % (v))
                    
            configValue.value[dictKey.value] = {"key":dictKey,"value":dictValue}
            configValue.opts["valueList"].append(dictKey.value)
    elif valueTypeAttr.type == gen_config.define.FieldType.mix:
        splitDatas = SplitData(value,False,error)
        for v in splitDatas:
            dictKeyStr,dictValueStr = GetDict(v)

            if not dictKeyStr:
                error("解析数据异常，dict不存在key值[目标类型:%s][配置数据:%s]" % (typeAttr.type,v))

            mixKeyTypeAttr,_ = GetValueType(dictKeyStr,False,error)

            if not gen_config.define.IsDictKeyType(mixKeyTypeAttr.type):
                error("解析数据异常，dict字段key类型错误[%s](支持int、string)" % (data))

            dictKey = ParseValue(dictKeyStr,mixKeyTypeAttr,error)

            if dictKey.value in configValue.value:
                error("解析数据异常，dict重复定义元素[%s]" % (v))

            data = dictValueStr

            if data != "":
                mixValueTypeAttr,newMixValue = GetValueType(data,False,error)
                if newMixValue == None:newMixValue = data

                newMixDataLen = len(newMixValue)
                if newMixValue[0] == "{" and newMixValue[newMixDataLen-1] == "}":
                    newMixValue = newMixValue[1:newMixDataLen-1]
                        
                if newMixValue != "":
                    dictValue = ParseValue(newMixValue,mixValueTypeAttr,error)
                    configValue.value[dictKey.value] = {"key":dictKey,"value":dictValue}
                    configValue.opts["valueList"].append(dictKey.value)

    return configValue

def SplitData(data,clip,error):
    dataLen = len(data)
    if dataLen <= 0:
        return []

    dataList = []
    parseString = ""
    matchString = ""
    isMatching = False
    isStringMatching = False
    matchCount = 0

    index = 0
    while index < dataLen:
        char = data[index]
        parseString = parseString + char

        if isStringMatching:
            if char == "\\" and index+1 < dataLen and data[index+1] == "\"":
                matchString = matchString +  "\\\""
                index += 1
            elif char == "\"":
                isStringMatching = False
            else:
                matchString = matchString + char
        elif isMatching:
            if char == "{":
                matchString = matchString + char
                matchCount = matchCount + 1
            elif char == "}" and matchCount > 1:
                matchString = matchString + char
                matchCount = matchCount - 1
            elif char == "}" and matchCount == 1:
                matchString = matchString + char
                isMatching = False
            else:
                matchString = matchString + char
        elif not isMatching:
            if char == "\"":
                isStringMatching = True
            elif char == "{":
                matchString = matchString + char
                matchCount = 1
                isMatching = True
            elif char=="," and matchString != "" and index + 1 < dataLen:
                dataList.append(matchString)
                matchString = ""
            elif char=="," and matchString != "" and index + 1 >= dataLen:
                error("解析数据异常，分割数据时逗号格式异常[%s](禁止首尾出现逗号,禁止连续2个逗号)" % (parseString))
            elif char == "," and matchString == "":
                error("解析数据异常，分割数据时逗号格式异常[%s](禁止首尾出现逗号,禁止连续2个逗号)" % (parseString))
            else:
                matchString = matchString + char
        
        index += 1

    if isMatching or isStringMatching:
        error("解析数据异常，分割数据时数据匹配异常[%s]" % (parseString))

    if len(matchString) > 0:
        dataList.append(matchString)
    
    #print("切割后的数据",dataList)

    if clip:
        for i in range(0,len(dataList)):
            item = dataList[i] 
            itemLen = len(item)

            if clip and item[0] == "{" and item[itemLen-1] == "}":
                dataList[i] = item[1:itemLen-1]
            elif clip and (item[0] != "{" or item[itemLen-1] != "}"):
                error("解析数据异常，分割数据时结构错误[%s](首尾应该是{})" % (item))

    return dataList


def GetValueType(value,isRoot,error):
    typeAttr = gen_config.define.FieldTypeAttr()
    valueType = gen_config.utils.GetMixNumberType(value)
    if valueType != None:
        typeAttr.type = valueType
        return typeAttr,None

    boolValue = gen_config.utils.GetMixBoolValue(value)
    if boolValue != None:
        typeAttr.type = gen_config.define.FieldType.bool
        return typeAttr,boolValue

    dataList = SplitData(value,False,error)
    dataLen = len(dataList)

    isDict = False
    isList = False
    for data in iter(dataList):
        if data[0] == "{" and data[len(data)-1] == "}":
            if dataLen > 1 or isRoot:
                isList = True
                continue

            childContent = data[1:len(data)-1]
            childDataList = SplitData(childContent,False,error)

            for childData in iter(childDataList):
                if childData[0] == "{" and childData[len(childData)-1] == "}":
                    isList = True
                else:
                    key,_ = GetDict(childData)
                    if key != None:
                        isDict = True
                    else:
                        isList = True
        else:
            key,_ = GetDict(data)
            if key != None:
                isDict = True
            elif dataLen > 1:
                isList = True

        if isDict and isList:
            error("解析数据异常，list和dict不允许是相同层级[%s]" % value)
        
    if isDict:
        typeAttr.type = gen_config.define.FieldType.dict

        keyTypeAttr = gen_config.define.FieldTypeAttr()
        keyTypeAttr.type = gen_config.define.FieldType.mix
        typeAttr.opts["key"] = keyTypeAttr

        valueTypeAttr = gen_config.define.FieldTypeAttr()
        valueTypeAttr.type = gen_config.define.FieldType.mix
        typeAttr.opts["value"] = valueTypeAttr
    elif isList or dataLen > 1:
        typeAttr.type = gen_config.define.FieldType.list

        valueTypeAttr = gen_config.define.FieldTypeAttr()
        valueTypeAttr.type = gen_config.define.FieldType.mix

        typeAttr.opts["type"] = valueTypeAttr
    else:
        typeAttr.type = gen_config.define.FieldType.string
        
    return typeAttr,None

def GetDict(data):
    if data == "" or len(data) < 3:
        return None,None

    markIndex = -1
    isStrMatch = False

    for index in range(0,len(data)):
        char = data[index]
        if char == "=" and not isStrMatch:
            markIndex = index
            break

        if char == "\"":
            isStrMatch = bool(1 - isStrMatch)

    if markIndex == -1 or markIndex == 0 or markIndex == len(data) - 1:
        return None,None

    key = data[0:markIndex].strip()
    value = data[markIndex+1:len(data)].strip()

    return key,value