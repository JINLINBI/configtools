import traceback
import xlrd
import re

import gen_config.define
import gen_config.config
import gen_config.utils
import gen_config.parse_export

from gen_config import parse_field_index
from gen_config import parse_config_value
from utils import io_utils

from utils.exception import LogException

class ParseConfig:
    def __init__(self,configName,localPath):
        self.configName = configName
        self.localPath = localPath
        self.fullPath =  gen_config.config.configPath + localPath
        self.sheetDatas = []
        self.sheetDataByName = {}
        self.sheetNames = {}
        self.workbook = None
        self.parseExport = gen_config.parse_export.ParseExport(localPath,self.ErrorRowCol)
        self.parseFieldIndex = parse_field_index.ParseFieldIndex(localPath)

        self.readSheet = None
        self.readRow = 0
        self.readCol = 0

    def Parse(self):
        self.workbook = xlrd.open_workbook(self.fullPath)

        exportSheet = self.GetSheet(gen_config.define.localExportSheet)
        if not exportSheet:
            return

        indexSheet = self.GetSheet(gen_config.define.localIndexSheet)
        if indexSheet:
            self.parseFieldIndex.ParseSheet(indexSheet)

        sheetInfos = []
        for sheet in self.workbook.sheets():
            sheetName = sheet.name
            if sheetName == gen_config.define.localExportSheet or sheetName == gen_config.define.localIndexSheet:
                continue

            descIndex = sheetName.find("(")
            if descIndex != -1 and sheetName[len(sheetName)-1] == ")":
                sheetName = sheetName[0:descIndex]
        
            if sheetName == self.configName:
                raise LogException("解析配置异常，sheet命名和配置表命名不允许一致[%s:%s]" % (self.localPath,sheetName))

            if not bool(re.search('^[a-z0-9_]*$',sheetName)) or not sheetName[0].islower() or sheetName[len(sheetName)-1] == "_":
                raise LogException("解析配置异常，sheet命名错误[%s:%s](只允许出现小写字母、下划线，并且首字母小写字母、尾字母不能为下划线)" % (self.localPath,sheetName))

            flag = self.ParseSheetDefine(sheet,sheetName)
            if flag:
                sheetInfos.append({"sheet":sheet,"sheetName":sheetName})

        if len(self.sheetDatas) <= 0:
            return

        self.parseExport.Parse(exportSheet,self.sheetDataByName)

        if not self.parseExport.IsExport():
            return

        for sheetInfo in sheetInfos:
            sheetName = sheetInfo["sheetName"]
            if self.parseExport.IsExportSheet(sheetName):
                self.ParseSheetData(sheetInfo["sheet"],sheetName)

    def ParseSheetDefine(self,sheet,sheetName):
        self.readSheet = sheet

        if sheet.nrows + 1 <= 3 or sheet.ncols + 1 <= 0:
            return False

        existSheet = sheetName in self.sheetDataByName

        sheetData = None
        if existSheet:
            sheetData = self.sheetDataByName[sheetName]
            self.CheckSheetDefSame(sheet,sheetData)
            return True

        sheetData = gen_config.define.SheetData()
        sheetData.name = sheetName
        sheetData.srcName = sheet.name

        for col in range(0,sheet.ncols):
            fieldAttr = self.ParseSheetFieldAttr(sheet,col)

            fieldName = fieldAttr.name
            if fieldName == "":
                continue

            if fieldName in sheetData.fieldAttrs:
                self.ErrorRowCol("解析配置异常，重复定义字段[%s]" % (fieldName),3,col+1)
                
            sheetData.fieldAttrsCol[col] = fieldName
            sheetData.fieldAttrs[fieldName] = fieldAttr
            
        self.sheetDataByName[sheetData.name] = sheetData
        self.sheetDatas.append(sheetData)
        return True

    def ParseSheetData(self,sheet,sheetName):
        self.readSheet = sheet

        sheetData = self.sheetDataByName[sheetName]
        for row in range(3,sheet.nrows):
            if self.IsPassRow(sheet,row):
                continue
            
            rowDatas = {}

            for col in range(0,sheet.ncols):
                self.readRow = row + 1
                self.readCol = col + 1

                if not (col in sheetData.fieldAttrsCol):
                    continue
                
                fieldName = sheetData.fieldAttrsCol[col]
                fieldAttr = sheetData.fieldAttrs[fieldName]

                srcValue = str(sheet.cell_value(row,col))
                configValue = srcValue

                if configValue == "" and fieldAttr.default != None:
                    configValue = fieldAttr.default

                if fieldAttr.indexType != None and configValue != "":
                    indexValue = self.GetFieldIndex(fieldAttr.indexType,configValue)
                    if indexValue != None:
                        configValue = indexValue
                    else:
                        self.Error("解析配置异常，字段找不到索引[%s]" % (configValue))
                elif fieldAttr.indexType != None and configValue == "":
                    indexValue = self.GetFieldIndexByDefault(fieldAttr.indexType)
                    if indexValue != None:
                        configValue = indexValue
                fieldValue = parse_config_value.ParseValue(configValue,fieldAttr.typeAttr,self.Error) #self.ParseConfigValue(configValue,fieldAttr.typeAttr)
                rowDatas[fieldAttr.name] = fieldValue

            sheetData.fieldValues.append(rowDatas)
    
    def IsPassRow(self,sheet,row):
        configValue = sheet.cell_value(row,0)
        return configValue == ""
    
    def GetFieldIndex(self,indexType,indexName):
        field = self.parseFieldIndex.GetFieldIndex(indexType,indexName)
        if field == None:
            field = gen_config.define.parseFieldIndex.GetFieldIndex(indexType,indexName)

        if field != None:
            return field["value"]
        else:
            return None
    
    def GetFieldIndexByDefault(self,indexType):
        field = self.parseFieldIndex.GetFieldIndexByDefault(indexType)
        if field == None:
            field = gen_config.define.parseFieldIndex.GetFieldIndexByDefault(indexType)

        if field != None:
            return field["value"]
        else:
            return None
    
    def ExistFieldIndexType(self,indexType):
        if self.parseFieldIndex.ExistFieldIndexType(indexType):
            return True
        elif gen_config.define.parseFieldIndex.ExistFieldIndexType(indexType):
            return True
        else:
            return False
    
    def ExistFieldIndex(self,indexType,indexName):
        if self.parseFieldIndex.ExistFieldIndex(indexType,indexName):
            return True
        elif gen_config.define.parseFieldIndex.ExistFieldIndex(indexType,indexName):
            return True
        else:
            return False

    def CheckSheetDefSame(self,sheet,sameSheetData):
        for col in range(0,sheet.ncols):
            fieldType = sheet.cell_value(1,col)
            fieldName = sheet.cell_value(2,col)

            existCol = col in sameSheetData.fieldAttrsCol

            if fieldName == "" and not existCol:
                continue

            if not existCol :
                self.ErrorRowCol("解析配置异常，重复sheet列数错位[对比sheet:%s]" % (sameSheetData.srcName),0,col+1)

            existFieldName = sameSheetData.fieldAttrsCol[col]
            fieldAttr = sameSheetData.fieldAttrs[existFieldName]

            if fieldType != fieldAttr.configType :
                self.ErrorRowCol("解析配置异常，重复sheet字段类型不一致[对比sheet:%s]" % (sameSheetData.srcName),2,col+1)

            if fieldName != fieldAttr.configName :
                self.ErrorRowCol("解析配置异常，重复sheet字段命名不一致[对比sheet:%s]" % (sameSheetData.srcName),3,col+1)

    def ParseSheetFieldAttr(self,sheet,col):
        fieldAttr = gen_config.define.FieldAttr()
        fieldAttr.col = col

        fieldName = sheet.cell_value(2,col)
        if fieldName == "":
            return fieldAttr
        
        if isinstance(fieldName, float):
            self.ErrorRowCol("解析配置异常，字段命名不允许是数字[%s]" % (fieldName),3,col+1)

        if not bool(re.search('^[a-zA-Z0-9]*$',fieldName)) or not fieldName[0].islower():
            self.ErrorRowCol("解析配置异常，字段命名错误[%s](只允许出现大小写字母、数字，并且首字母是小写字母)" % (fieldName),3,col+1)
        
        if fieldName == "index" or fieldName == "set" or fieldName == "num":
            self.ErrorRowCol("解析配置异常，字段命名不允许为关键字[%s](关键字为index、set、num)" % (fieldName),3,col+1)

        infoStr = str(sheet.cell_value(0,col))
        infos = infoStr.split(",")
        for info in iter(infos):
            infoParams = info.split("=")
            if infoParams[0] == "i18n":
                fieldAttr.i18n = True
            elif len(infoParams) == 1:
                fieldAttr.desc = infoParams[0]
            elif infoParams[0] == "索引":
                fieldAttr.indexType = infoParams[1]
            elif infoParams[0] == "默认值":
                fieldAttr.default = infoParams[1]

            
        
        if fieldAttr.indexType != None and not self.ExistFieldIndexType(fieldAttr.indexType):
            self.ErrorRowCol("解析配置异常，定义了空的索引类型[%s]" % (fieldAttr.indexType),1,col+1)
        elif fieldAttr.indexType != None and fieldAttr.default != None and not self.ExistFieldIndex(fieldAttr.indexType,fieldAttr.default):
            self.ErrorRowCol("解析配置异常，定义了不存在的默认索引值[%s]" % (fieldAttr.default),1,col+1)

        fieldType = sheet.cell_value(1,col)

        fieldAttr.typeAttr = self.ParseFieldType(fieldType,sheet.name,col+1)

        fieldAttr.configName = fieldName
        fieldAttr.configType = fieldType

        fieldAttr.name = fieldName
        fieldAttr.upperName = fieldName[0].title() + fieldName[1:]

        return fieldAttr
    
    def ParseFieldType(self,fieldType,sheetName,col):
        if isinstance(fieldType, float):
            self.ErrorRowCol("解析配置异常，字段类型不允许为数字[%s]" % (gen_config.utils.GetNumber(fieldType)),2,col)

        fieldTypeAttr = gen_config.define.FieldTypeAttr()
        typeLen = len(fieldType)
        if typeLen <= 0:
            self.ErrorRowCol("解析配置异常，字段类型为空",2,col)

        if fieldType.find("list[") == 0 and fieldType[typeLen - 1] == "]":
            fieldTypeAttr.type = gen_config.define.FieldType.list
    
            valueType = fieldType[5:typeLen-1]

            typeAttr = self.ParseFieldType(valueType,sheetName,col)
            fieldTypeAttr.opts["type"] = typeAttr
        elif fieldType.find("dict[") == 0 and fieldType[typeLen - 1] == "]":
            fieldTypeAttr.type = gen_config.define.FieldType.dict
            keyValueStr = fieldType[5:typeLen-1]

            keyIndex = keyValueStr.find(",")

            if keyIndex == -1:
                self.ErrorRowCol("解析配置异常，dict字段格式错误[%s](应该用逗号分割)" % (fieldType),2,col)

            keyType = keyValueStr[0:keyIndex]
            valueType = keyValueStr[keyIndex+1:len(keyValueStr)]
            
            if not gen_config.define.IsDictKeyType(keyType):
                self.ErrorRowCol("解析配置异常，dict字段key类型错误[%s](支持int、string)" % (fieldType),2,col)

            keyTypeAttr = gen_config.define.FieldTypeAttr()
            keyTypeAttr.type = keyType

            valueTypeAttr = self.ParseFieldType(valueType,sheetName,col)

            fieldTypeAttr.opts["key"] = keyTypeAttr
            fieldTypeAttr.opts["value"] = valueTypeAttr
        elif fieldType == gen_config.define.FieldType.mix:
            fieldTypeAttr.type = gen_config.define.FieldType.mix
            
            typeAttr = gen_config.define.FieldTypeAttr()
            typeAttr.type = gen_config.define.FieldType.mix

            fieldTypeAttr.opts["type"] = typeAttr
            fieldTypeAttr.opts["key"] = typeAttr
            fieldTypeAttr.opts["value"] = typeAttr
        elif gen_config.define.IsFieldType(fieldType):
            fieldTypeAttr.type = fieldType
        else:
            self.ErrorRowCol("解析配置异常，字段类型无法识别[%s]" % (fieldType),2,col)
                
        return fieldTypeAttr
    
    def GetSheet(self,sheetName):
        sheet = None
        try:
            sheet =self.workbook.sheet_by_name(sheetName)
        finally:
            return sheet
        
    def IsExportTarget(self,target):
        return self.parseExport.IsExportTarget(target)

    def Error(self,err):
        colName = gen_config.utils.ExcelNumToColName(self.readCol)
        raise LogException("%s(%s:%s:%s行,%s列(%s))" % (err,self.localPath,self.readSheet.name,self.readRow,self.readCol,colName))
    
    def ErrorRowCol(self,err,row,col,sheetName=None):
        colName = gen_config.utils.ExcelNumToColName(col)
        if not sheetName:sheetName = self.readSheet.name
        raise LogException("%s(%s:%s:%s行,%s列(%s))" % (err,self.localPath,sheetName,row,col,colName))