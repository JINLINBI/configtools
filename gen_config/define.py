

configs = {}

#全局字段索引
parseFieldIndex = None
languages = None
i18n = False
globalIndexFile = "index.xls"
localIndexSheet = "索引"
localExportSheet = "导出"

class FieldType:
	none   = "none"
	int    = "int"
	float  = "float"
	string = "string"
	bool   = "bool"
	list   = "list"
	dict   = "dict"
	mix    = "mix"
	lua    = "lua"

def IsFieldType(fieldType):
	if fieldType == FieldType.int:return True
	if fieldType == FieldType.float:return True
	if fieldType == FieldType.string:return True
	if fieldType == FieldType.bool:return True
	if fieldType == FieldType.list:return True
	if fieldType == FieldType.dict:return True
	if fieldType == FieldType.mix:return True
	if fieldType == FieldType.lua:return True
	return False

def IsBaseFieldType(fieldType):
	if fieldType == FieldType.int:return True
	if fieldType == FieldType.float:return True
	if fieldType == FieldType.string:return True
	if fieldType == FieldType.bool:return True
	return False

def IsDictKeyType(fieldType):
	if fieldType == FieldType.int:return True
	if fieldType == FieldType.string:return True
	return False

def IsExportKeyType(fieldType):
	if fieldType == FieldType.int:return True
	if fieldType == FieldType.string:return True
	return False


class SheetData:
	def __init__(self):
		self.name = ""
		self.srcName = ""
		self.fieldAttrs = {}
		self.fieldAttrsCol = {}
		self.fieldValues = []

class FieldAttr:
	def __init__(self):
		self.name = ""
		self.upperName = ""
		self.configName = ""
		self.configType = ""
		self.desc = ""
		self.typeAttr = None
		self.default = None
		self.indexType = None
		self.i18n = False
		self.col = None

class FieldTypeAttr:
	def __init__(self):
		self.type = FieldType.none
		self.opts = {}

class ConfigValue:
	def __init__(self):
		self.type = FieldType.none
		self.value = None
		self.srcValue = None
		self.opts = {}

class ExportTarget:
	lua   = "lua"
	go    = "go"
	cs     = "cs"


