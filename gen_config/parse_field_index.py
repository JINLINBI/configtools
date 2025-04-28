import xlrd
import re

from utils import io_utils
import gen_config.config
from gen_config.utils import ErrorRowCol
from utils.exception import LogException

class ParseFieldIndex:
	def __init__(self,localPath):
		self.localPath = localPath
		self.fieldIndexs = {}
		self.fieldIndexToSheet = {}

	def ParseFile(self):
		filePath = gen_config.config.configPath + self.localPath
		if not io_utils.ExistFile(filePath):
			return

		workbook = xlrd.open_workbook(filePath)
		for sheet in workbook.sheets():
			self.ParseSheet(sheet)

	def ParseSheet(self,sheet):
		if sheet.ncols <= 1 or sheet.nrows <= 1:
			return

		indexType = ""

		for row in range(0,sheet.nrows):
			key = sheet.cell_value(row,0)

			if isinstance(key, float):
				ErrorRowCol("解析索引异常，第一列不允许为数字[%s]" % key,row+1,1,self.localPath,sheet.name)

			if key == "":
				indexType = ""
				continue

			if key[0] == "[" and key[len(key)-1] == "]":
				indexType = key[1:len(key)-1]

				if indexType in self.fieldIndexToSheet:
					sheetName = self.fieldIndexToSheet[indexType]
					ErrorRowCol("解析索引异常，重复定义索引类型[%s][冲突sheet:%s]" % (indexType,sheetName),row+1,1,self.localPath,sheet.name)
				
				self.fieldIndexs[indexType] = {}
				self.fieldIndexs[indexType]["data"] = {}
				self.fieldIndexs[indexType]["num"] = 0
				self.fieldIndexs[indexType]["default"] = None

				self.fieldIndexToSheet[indexType] = sheet.name
				continue

			if indexType == "":
				ErrorRowCol("解析索引异常，缺失索引类型[%s]" % key,row+1,1,self.localPath,sheet.name)

			if key in self.fieldIndexs[indexType]:
				ErrorRowCol("解析索引异常，重复定义索引Key[%s]" % (key),row+1,1,self.localPath,sheet.name)

			if not bool(re.search('^[a-zA-Z0-9()\u4e00-\u9fff]*$', key)):
				ErrorRowCol("解析索引异常，索引Key命名错误[%s](只允许出现大小写字母、数字、中文)" % key,row+1,1,self.localPath,sheet.name)

			value = sheet.cell_value(row,1)
			if value == "":
				ErrorRowCol("解析索引异常，索引值为空[%s]" % key,row+1,2,self.localPath,sheet.name)
			
			if isinstance(value, float) and value % 1 == 0:
				value = int(value)

			self.fieldIndexs[indexType]["data"][key] = { "value":value,"sheetName":sheet.name,"row":row +1,"col":1 }
			self.fieldIndexs[indexType]["num"] += 1
			if not self.fieldIndexs[indexType]["default"]:
				self.fieldIndexs[indexType]["default"] = key

	def GetFieldIndex(self,indexType,key):
		if not (indexType in self.fieldIndexs):
			return None
		elif key in self.fieldIndexs[indexType]["data"]:
			return self.fieldIndexs[indexType]["data"][key]
		else:
			return None
	
	def GetFieldIndexByDefault(self,indexType):
		if not (indexType in self.fieldIndexs):
			return None
		else:
			defaultKey = self.fieldIndexs[indexType]["default"]
			return self.fieldIndexs[indexType]["data"][defaultKey]
	
	def ExistFieldIndexType(self,indexType):
		if not (indexType in self.fieldIndexs):
			return False
		else:
			return self.fieldIndexs[indexType]["num"] > 0
	
	def ExistFieldIndex(self,indexType,key):
		if not (indexType in self.fieldIndexs):
			return False
		else:
			return key in self.fieldIndexs[indexType]["data"]
