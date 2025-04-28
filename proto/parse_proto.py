import re

import proto.define
import proto.config
from utils.exception import LogException

class ParseProto:
    def __init__(self,filePath,isCommon):
        self.filePath = filePath
        self.isCommon = isCommon
        self.readState = proto.define.ReadState.none
        self.types = {}
        self.dataList = []
        self.parseData = None
        self.parseFieldStruct = []
        self.line = ""
        self.lineNum = 0

    def Parse(self):
        fullPath = proto.config.protoFilePath + self.filePath

        for line in open(fullPath,"r",encoding="utf-8"):
            self.lineNum += 1
            line = line.lstrip().rstrip().rstrip("\n")
            if line == "":continue
            
            annotationIndex = line.find("//")
            if annotationIndex == 0:
                continue
            elif annotationIndex != -1:
                line = line[0:annotationIndex]
                line = line.lstrip().rstrip().rstrip("\n")
                
                if line[ len(line) - 1 ] == ",":
                    raise LogException("解析异常,不能以\",\"号结尾[%s:%s][%s]" % ( self.filePath, self.lineNum,line))

            self.line = line

            if len(self.parseFieldStruct) > 0:
                self.ReadFieldStruct()
            elif self.readState == proto.define.ReadState.none:
                self.StateNone()
            elif self.readState == proto.define.ReadState.read_enum:
                self.StateReadEnum()
            elif self.readState == proto.define.ReadState.read_struct:
                self.StateReadStruct()
            elif self.readState == proto.define.ReadState.read_proto:
                self.StateReadProto()
            elif self.readState == proto.define.ReadState.read_proto_in:
                self.StateReadProtoIn()
            elif self.readState == proto.define.ReadState.read_proto_out:
                self.StateReadProtoOut()

        if self.readState != proto.define.ReadState.none:
            raise LogException("文件结尾异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))
    
    def StateNone(self):
        defAttr = self.line.split(" ")
        attrLen = len(defAttr)

        if defAttr[0] == "enum":
            typeName = defAttr[1]

            if not bool(re.search('^[a-zA-Z0-9]*$',typeName)) or not typeName[0].isupper():
                raise LogException("[enum]定义名字出错[%s:%s][错误命名:\"%s\"]（只允许出现 [\"a-z、A-Z、0-9\"],并且首字母为大写）" % ( self.filePath, self.lineNum,typeName))
            
            if defAttr[attrLen-1] != "{":
                raise LogException("[enum]定义出错,异常的结束尾(应该以\"{\"结尾)[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))
            
            if attrLen != 4:
                raise LogException("[enum]定义数量异常[%s:%s][%s]" % ( self.filePath,self.lineNum,self.line))

            if not proto.define.IsFieldType(defAttr[2]):
                raise LogException("[enum]定义的值类型异常[%s:%s][%s]" % ( self.filePath,self.lineNum,self.line))

            self.parseData = proto.define.EnumData()
            self.parseData.name = typeName
            self.parseData.valueType = defAttr[2]
            self.UpdateState(proto.define.ReadState.read_enum)
            self.AddType(typeName,self.parseData)
        elif defAttr[0] == "struct":
            typeName = defAttr[1]

            if not bool(re.search('^[a-zA-Z0-9]*$',typeName)) or not typeName[0].isupper():
                raise LogException("[struct]定义名字出错[%s:%s][错误命名:\"%s\"]（只允许出现 [\"a-z、A-Z、0-9\"],并且首字母为大写）" % ( self.filePath, self.lineNum,typeName))
            
            if defAttr[attrLen-1] != "{":
                raise LogException("[struct]定义出错,异常的结束尾(应该以\"{\"结尾)[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))
        
            if attrLen != 3:
                raise LogException("[struct]定义数量异常[%s:%s][%s]" % ( self.filePath,self.lineNum,self.line))

            self.parseData = proto.define.StructData()
            self.parseData.name = typeName
            self.UpdateState(proto.define.ReadState.read_struct)
            self.AddType(typeName,self.parseData)
        elif defAttr[0] == "proto":
            if self.isCommon:
                raise LogException("[proto]禁止在common文件夹中定义[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            if attrLen != 3:
                raise LogException("[proto]定义出错,描述数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            if not defAttr[1].isdigit():
                raise LogException("[proto]定义出错,协议ID不是整形[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            if defAttr[2] != "{":
                raise LogException("[proto]定义出错,异常的结束尾(应该以\"{\"结尾)[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            self.parseData = proto.define.ProtoData()
            self.parseData.id = int(defAttr[1])
            self.UpdateState(proto.define.ReadState.read_proto)
        else:
            raise LogException("未知的定义内容[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

        self.dataList.append(self.parseData)

    def StateReadEnum(self):
        fieldAttr = self.line.split("=")
        self.FormatStrings(fieldAttr)
        attrLen = len(fieldAttr)

        if attrLen == 1 and fieldAttr[0] == "}":
            self.UpdateState(proto.define.ReadState.none)
            return
        
        if attrLen != 2:
            raise LogException("[enum]定义出错,定义数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))
        
        self.parseData.enumList.append( {"key" : fieldAttr[0], "value" : fieldAttr[1]})

    def StateReadStruct(self):
        fieldAttrs = self.line.split(" ")
        self.FormatStrings(fieldAttrs)
        attrLen = len(fieldAttrs)

        if attrLen == 1 and fieldAttrs[0] == "}":
            self.UpdateState(proto.define.ReadState.none)
            return

        fieldData = self.GetFieldData(fieldAttrs,attrLen)
        self.parseData.fieldList.append(fieldData)

    def StateReadProto(self):
        fieldAttrs = self.line.split(" ")
        self.FormatStrings(fieldAttrs)
        attrLen = len(fieldAttrs)

        if attrLen == 1 and fieldAttrs[0] == "}":
            self.UpdateState(proto.define.ReadState.none)
            return

        if attrLen != 2:
            raise LogException("[proto]定义出错,定义数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

        if fieldAttrs[0] != "in" and fieldAttrs[0] != "out":
            raise LogException("[proto]定义出错,无法识别的描述[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

        if fieldAttrs[1] != "{":
            raise LogException("[proto]定义出错,异常的结束尾(应该以\"{\"结尾)[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

        if fieldAttrs[0] == "in":
            self.UpdateState(proto.define.ReadState.read_proto_in)
        elif fieldAttrs[0] == "out":
            self.UpdateState(proto.define.ReadState.read_proto_out)

    def StateReadProtoIn(self):
        fieldAttrs = self.line.split(" ")
        self.FormatStrings(fieldAttrs)
        attrLen = len(fieldAttrs)

        if attrLen == 1 and fieldAttrs[0] == "}":
            self.UpdateState(proto.define.ReadState.read_proto)
            return

        fieldData = self.GetFieldData(fieldAttrs,attrLen)
        self.parseData.inList.append(fieldData)

    def StateReadProtoOut(self):
        fieldAttrs = self.line.split(" ")
        self.FormatStrings(fieldAttrs)
        attrLen = len(fieldAttrs)

        if attrLen == 1 and fieldAttrs[0] == "}":
            self.UpdateState(proto.define.ReadState.read_proto)
            return

        fieldData = self.GetFieldData(fieldAttrs,attrLen)
        self.parseData.outList.append(fieldData)

    def ReadFieldStruct(self):
        fieldAttrs = self.line.split(" ")
        self.FormatStrings(fieldAttrs)
        attrLen = len(fieldAttrs)

        if attrLen == 1 and fieldAttrs[0] == "}":
            self.parseFieldStruct.pop()
        else:
            structData = self.parseFieldStruct[-1]
            fieldData = self.GetFieldData(fieldAttrs,attrLen)
            structData.fieldList.append(fieldData)
    
    def AddType(self,typeName,data):
        existKey = typeName in proto.define.allTypes
        localExistKey = typeName in self.types
        if existKey or localExistKey:
            raise LogException("[type]数据存在相同命名[%s:%s][%s]" % ( self.filePath,self.lineNum,typeName))

        self.types[typeName] = data
        proto.define.allTypes[typeName] = data
        if self.isCommon:
            proto.define.commonTypes[typeName] = self.parseData
    
    def GetFieldData(self,fieldAttrs,attrLen):
        if attrLen < 2:
            raise LogException("字段定义数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

        fieldData = proto.define.FieldData()
        fieldData.name = fieldAttrs[0]

        if not bool(re.search('^[a-zA-Z0-9]*$',fieldData.name)) or not fieldData.name[0].islower():
            raise LogException("字段名异常[%s:%s][\"%s\"]（只允许出现 [\"a-z、A-Z、0-9\"],并且首字母为小写）" % ( self.filePath, self.lineNum,fieldData.name))

        fieldData.line = self.line
        fieldData.lineNum = self.lineNum
        fieldData.type = fieldAttrs[1]

        if fieldData.type == "list":
            if attrLen != 3:
                raise LogException("list字段定义数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            fieldData.opts["type"] = fieldAttrs[2]
        elif fieldData.type == "dict":
            if attrLen != 4:
                raise LogException("dict字段定义数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            if not proto.define.IsDictKeyType(fieldAttrs[2]):
                raise LogException("dict定义错误的Key类型[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))

            fieldData.opts["key"] = fieldAttrs[2]
            fieldData.opts["value"] = fieldAttrs[3]
        else:
            if attrLen != 2:
                raise LogException("字段数量异常[%s:%s][%s]" % ( self.filePath, self.lineNum,self.line))
        
        if fieldAttrs[attrLen-1] == "{":
            structData = proto.define.StructData()
            fieldData.typeStruct = structData
            self.parseFieldStruct.append(structData)

        return fieldData

    def CheckFileFieldType(self):
        for data in self.dataList:
            if data.type == proto.define.DefType.enum:
                continue
            elif data.type == proto.define.DefType.struct:
                self.CheckFieldTypes(data.fieldList)
            elif data.type == proto.define.DefType.proto:
                self.CheckFieldTypes(data.inList)
                self.CheckFieldTypes(data.outList)
            else:
                raise LogException("未知的数据类型[%s][%s]" % (self.filePath,data.type))
    
    def CheckFieldTypes(self,fieldList):
        for field in fieldList:
            if field.typeStruct != None:
                field.defType = proto.define.DefType.inline_struct
                self.CheckFieldTypes(field.typeStruct.fieldList)
            else:
                flag = self.CheckFieldType(field)
                if not flag:
                    raise LogException("字段类型不存在[%s:%s][%s]" % (self.filePath,field.lineNum,field.line))

    def CheckFieldType(self,field):
        fieldType = field.type
        if field.type == "list":
            fieldType = field.opts["type"]
        elif field.type == "dict":
            fieldType = field.opts["value"]

        if proto.define.IsFieldType(fieldType):
            field.defType = proto.define.DefType.base
            return True
        
        if (fieldType in proto.define.commonTypes):
            field.defType = proto.define.commonTypes[fieldType].type
            return True

        if (fieldType in self.types):
            field.defType = self.types[fieldType].type
            return True

        return False

    def UpdateState(self,state):
        self.readState = state

    def FormatStrings(self,strList):
        for i in range(len(strList)):
            strList[i] = strList[i].lstrip().rstrip()