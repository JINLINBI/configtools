import os

from utils import io_utils
from utils import string_utils
import gen_config.config
import gen_config.define


class ExportLanguage:
    def __init__(self,configParse):
        self.configParse = configParse
        self.hashs = []
        self.hashToText = {}

    def Parse(self):
        exportSheetDatas = []
        for sheetData in self.configParse.sheetDatas:
            if self.configParse.parseExport.IsExportSheet(sheetData.name):
                exportSheetDatas.append(sheetData)

        for sheetData in exportSheetDatas:
            self.ParseSheetLanguageText(sheetData)

    def ParseSheetLanguageText(self,sheetData):
        for _,rowData in enumerate(sheetData.fieldValues):
            for _,fieldName in sheetData.fieldAttrsCol.items():
                self.ParseFieldLanguageText(rowData[fieldName],sheetData.fieldAttrs[fieldName])

    def ParseFieldLanguageText(self,configValue,fieldAttr):
        if configValue.type == gen_config.define.FieldType.string:
            fieldValue = configValue.value
            if fieldAttr.i18n:
                md5 = string_utils.GetMd5ByLen(fieldValue)
                if (md5 in self.hashToText) == False:
                    self.hashToText[md5] = fieldValue
                    self.hashs.append(md5)
        elif configValue.type == gen_config.define.FieldType.list:
            for value in configValue.value:
                self.ParseFieldLanguageText(value,fieldAttr)
        elif configValue.type == gen_config.define.FieldType.dict:
            for keyName in configValue.opts["valueList"]:
                keValue = configValue.value[keyName]
                self.ParseFieldLanguageText(keValue["value"],fieldAttr)
    
    def IsExport(self):
        return len(self.hashs) > 0
    
    def Export(self,filePath):
        localLanguageInfos = None

        if io_utils.ExistFile(filePath):
            try:
                localLanguageInfos = io_utils.LoadJson(filePath)
            except Exception as e:
                raise Exception("已有的多语言配置加载失败，请手动修复[%s][%s]" % (filePath,str(e)))
        else:
            io_utils.CreateFolderByFile(filePath)
            localLanguageInfos = []

        existLanguageInfos = []
        checkExistLanguageIInfos = {}
        for v in localLanguageInfos:
            if v["key"] in self.hashToText:
                srcText = v["text"]
                newText = str.replace(v["text"],'\n','\\n').replace("\"","\\\"")
                existLanguageInfos.append({"key":v["key"],"text":newText})
                checkExistLanguageIInfos[v["key"]] = True

        newLanguageInfos = []
        for hash in self.hashs:
            if (hash in checkExistLanguageIInfos) == False:
                srcText = self.hashToText[hash]
                newText = str.replace(srcText,"\"","\\\"")
                newLanguageInfos.append({"key":hash,"text":newText})

        file = open(filePath,encoding="utf-8", mode="w")

        file.write("[\n")

        newMaxLen = len(newLanguageInfos)

        existMaxLen = len(existLanguageInfos)
        for i,v in enumerate(existLanguageInfos):
            file.write("    {\"key\":\"%s\",\"text\":\"%s\"}%s\n" % (v["key"],v["text"], "" if i == existMaxLen - 1 and newMaxLen == 0 else ","))

        for i,v in enumerate(newLanguageInfos):
            file.write("    {\"key\":\"%s\",\"text\":\"(待翻译)%s\"}%s\n" % (v["key"],v["text"], "" if i == newMaxLen - 1 else ","))

        file.write("]")
        file.flush()
        file.close()

# def Export(configParse,filePath):
#     oldLangInfos = None
    
#     if io_utils.ExistFile(filePath):
#         try:
#             oldLangInfos = io_utils.LoadJson(filePath)
#         except Exception as e:
#             raise Exception("已有的多语言配置加载失败，请手动修复[%s][%s]" % (filePath,str(e)))
#     else:
#         io_utils.CreateFolderByFile(filePath)
#         oldLangInfos = []

#     langHashs = []
#     langHashToStr = {}

#     exportSheetDatas = []
#     for sheetData in configParse.sheetDatas:
#         if configParse.parseExport.IsExportSheet(sheetData.name):
#             exportSheetDatas.append(sheetData)

#     for sheetData in exportSheetDatas:
#         ParseSheetLangStr(sheetData,langHashs,langHashToStr)


#     existLangInfos = []
#     existLandInfoDict = {}
#     for v in oldLangInfos:
#         if v["key"] in langHashToStr:
#             existLangInfos.append({"key":v["key"],"text":"\"" + str.replace(v["text"],'\n','\\n')+ "\""})
#             existLandInfoDict[v["key"]] = True

#     newLangInfos = []
#     for hash in langHashs:
#         if (hash in existLandInfoDict) == False:
#             newLangInfos.append({"key":hash,"text":langHashToStr[hash]})

#     #写入
#     if len(langHashs) > 0:
#         file = open(filePath,encoding="utf-8", mode="w")

#         file.write("[\n")

#         newMaxLen = len(newLangInfos)

#         existMaxLen = len(existLangInfos)
#         for i,v in enumerate(existLangInfos):
#             file.write("    {\"key\":\"%s\",\"text\":%s}%s\n" % (v["key"],v["text"], "" if i == existMaxLen - 1 and newMaxLen == 0 else ","))

        
#         if existMaxLen > 0 and newMaxLen > 0:
#             file.write("    <---以下为新增翻译内容--->\n")

#         for i,v in enumerate(newLangInfos):
#             file.write("    {\"key\":\"%s\",\"text\":%s}%s\n" % (v["key"],v["text"], "" if i == newMaxLen - 1 else ","))

#         file.write("]")
#         file.flush()
#         file.close()

#         return True

#     return False
    
    
# def ParseSheetLangStr(sheetData,langHashs,langHashToStr):
#     for _,rowData in enumerate(sheetData.fieldValues):
#         for _,fieldName in sheetData.fieldAttrsCol.items():
#             ParseFieldLangStr(rowData[fieldName],sheetData.fieldAttrs[fieldName],langHashs,langHashToStr)
               

# def ParseFieldLangStr(configValue,fieldAttr,langHashs,langHashToStr):
#     if configValue.type == gen_config.define.FieldType.string:
#         fieldValue = configValue.value
#         if fieldAttr.i18n:
#             md5 = string_utils.GetMd5ByLen(fieldValue)
#             if (md5 in langHashToStr) == False:
#                 langHashToStr[md5] = "\"" +  fieldValue + "\""
#                 langHashs.append(md5)
#     elif configValue.type == gen_config.define.FieldType.list:
#         for value in configValue.value:
#             ParseFieldLangStr(value,fieldAttr,langHashs,langHashToStr)
#     elif configValue.type == gen_config.define.FieldType.dict:
#         for keyName in configValue.opts["valueList"]:
#             keValue = configValue.value[keyName]
#             ParseFieldLangStr(keValue["value"],fieldAttr,langHashs,langHashToStr)