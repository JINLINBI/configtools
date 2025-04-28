import gen_config.define
import gen_config.config
import gen_config.utils

from gen_config import parse_field_index
from gen_config import parse_config_value

from utils.exception import LogException


class ParseExport:
    def __init__(self,localPath,error):
        self.localPath = localPath
        self.error = error
        self.exportInfos = {}

    def Parse(self,sheet,sheetDataByName):
        if sheet.nrows + 1 <= 3 or sheet.ncols + 1 <= 0:
            return
        
        for col in range(0,sheet.ncols):
            exportSheetName = str(sheet.cell_value(0,col))
            if exportSheetName == "":
                continue
        
            if not (exportSheetName in sheetDataByName):
                self.error("导出信息异常，不存在要导出的sheet表[%s]" % (exportSheetName),1,col + 1)

            exportTarget = str(sheet.cell_value(1,col))
            if exportTarget == "" or not self.CheckExportTarget(exportTarget):
                self.error("导出信息异常，无效的导出目标[%s](支持lua、go)" % (exportTarget),2,col + 1)

            if not (exportSheetName in self.exportInfos):
                self.exportInfos[exportSheetName] = {}
            
            if exportTarget in self.exportInfos[exportSheetName]:
                self.error("导出信息异常，重复定义导出目标][%s]" % (exportTarget),2,col + 1)

            exportParamStr = str(sheet.cell_value(2,col))
            exportParams = self.ParseExportParam(exportParamStr,3,col + 1)
            self.CheckExportParam(exportTarget,exportParams,3,col + 1)

            self.exportInfos[exportSheetName][exportTarget] = {}
            self.exportInfos[exportSheetName][exportTarget]["params"] = exportParams
            self.exportInfos[exportSheetName][exportTarget]["exportInfos"] = []

            sheetData = sheetDataByName[exportSheetName]

            tempSortExportFields = {}
            for row in range(3,sheet.nrows):
                exportFieldStr = str(sheet.cell_value(row,col))
                if exportFieldStr == "":
                    continue

                exportFieldStrLen = len(exportFieldStr)
                if exportFieldStr[0] == "," or exportFieldStr[exportFieldStrLen - 1] == "," or exportFieldStr.find(",,") != -1:
                    self.error("导出信息异常，导出字段格式错误[%s](首尾不能为逗号、不同连续出现2个逗号)" % (exportFieldStr),row + 1,col + 1)
                
                if exportFieldStr.find("，") != -1:
                    self.error("导出信息异常，导出字段出现中文逗号[%s]" % (exportFieldStr),row + 1,col + 1)

                
                paramsStr = None
                descIndex = exportFieldStr.find("[")
                exportFieldParams = {}
                if descIndex != -1 and exportFieldStr[len(exportFieldStr)-1] == "]":
                    paramsStr = exportFieldStr[descIndex + 1:len(exportFieldStr)-1]
                    exportFieldStr = exportFieldStr[0:descIndex]

                if paramsStr != None:
                    for info in iter(paramsStr.split(",")):
                        exportFieldParams[info] = info
                        
                
                sortExportFieldStr = "".join((lambda x: (x.sort(), x)[1])(list(exportFieldStr)))
                if sortExportFieldStr in tempSortExportFields:
                    self.error("导出信息异常，重复定义导出字段[%s]" % (exportFieldStr),row+1,3)
                else:
                    tempSortExportFields[sortExportFieldStr] = True
                
                exportFields = exportFieldStr.split(",")
                exportFieldTypes = []
                for field in iter(exportFields):
                    if not (field in sheetData.fieldAttrs):
                        self.error("导出信息异常，不存在导出字段[%s]" % (field),row + 1,col + 1)

                    fieldType = sheetData.fieldAttrs[field].typeAttr.type
                    if not gen_config.define.IsExportKeyType(fieldType):
                        self.error("导出信息异常，无效的导出字段类型[%s](支持int、string)" % (field),row + 1,col + 1)
                    else:
                        exportFieldTypes.append(fieldType)

                exportInfo = {"indexKey":exportFieldStr,"fields":exportFields,"fieldTypes":exportFieldTypes,"group":"group" in exportFieldParams}
                self.exportInfos[exportSheetName][exportTarget]["exportInfos"].append(exportInfo)
    
    def CheckExportParam(self,exportTarget,exportParams,row,col):
        if exportTarget == gen_config.define.ExportTarget.lua:
            if not ("mode" in exportParams):
                self.error("导出信息异常，mode参数缺失",row,col)
            elif exportParams["mode"] != "index" and exportParams["mode"] != "func" and exportParams["mode"] != "str":
                self.error("导出信息异常，mode参数无效[%s](支持index、func、str)" % exportParams["mode"],row,col)
    
    def ParseExportParam(self,exportParamStr,row,col):
        exportParams = {}

        if exportParamStr == "":
            return exportParams
        
        exportParamInfos = exportParamStr.split(",")
        for info in iter(exportParamInfos):
            exportParamInfos = info.split("=")
            if len(exportParamInfos) != 2:
                self.error("导出信息异常，参数格式错误[%s]" % (exportParamStr),3,col + 1)
            elif exportParamInfos[0] in exportParams:
                self.error("导出信息异常，重复定义导出参数[%s]" % (exportParamStr),3,col + 1)
            else:
                exportParams[exportParamInfos[0]] = exportParamInfos[1]
        
        return exportParams
                
    def CheckExportTarget(self,exportTarget):
        if exportTarget == gen_config.define.ExportTarget.lua:
            return True
        elif exportTarget == gen_config.define.ExportTarget.go:
            return True
        elif exportTarget == gen_config.define.ExportTarget.cs:
            return True
        else:
            return False
    
    def IsExport(self):
        return len(self.exportInfos) > 0
    
    def IsExportSheet(self,sheetName):
        return sheetName in self.exportInfos

    def IsExportTarget(self,exportTarget):
        for _,v in self.exportInfos.items():
            if exportTarget in v:
                return True
        return False
    
    def IsExportSheetTarget(self,sheetName,exportTarget):
        if not self.IsExportSheet(sheetName):
            return False
        return exportTarget in self.exportInfos[sheetName]


    def GetExportInfo(self,sheetName,exportTarget):
        return self.exportInfos[sheetName][exportTarget]
    