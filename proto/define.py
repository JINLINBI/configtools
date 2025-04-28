from enum import Enum
 
# 继承枚举类
class ReadState(Enum):
    none = 0
    read_enum = 2 #开始读取枚举
    read_struct = 4 #读取结构
    read_proto = 6
    read_proto_in = 7,
    read_proto_out = 8,

class FieldType():
    string = "string"
    bool = "bool"
    int8 = "int8"
    uint8 = "uint8"
    int16 = "int16"
    uint16 = "uint16"
    int32 = "int32"
    uint32 = "uint32"
    float = "float"
    double = "double"

def TypeTo(fieldType):
    if fieldType == FieldType.float:
        return "float32"
    elif fieldType == FieldType.double:
        return "float64"
    else:
        return fieldType

def IsFieldType(fieldType):
    if fieldType == FieldType.string:
        return True
    elif fieldType == FieldType.bool:
        return True
    elif fieldType == FieldType.int8:
        return True
    elif fieldType == FieldType.uint8:
        return True
    elif fieldType == FieldType.int16:
        return True
    elif fieldType == FieldType.uint16:
        return True
    elif fieldType == FieldType.int32:
        return True
    elif fieldType == FieldType.uint32:
        return True
    elif fieldType == FieldType.float:
        return True
    elif fieldType == FieldType.double:
        return True
    else:
        return False

def IsDictKeyType(keyType):
    if keyType == FieldType.string:
        return True
    elif keyType == FieldType.int8:
        return True
    elif keyType == FieldType.uint8:
        return True
    elif keyType == FieldType.int16:
        return True
    elif keyType == FieldType.uint16:
        return True
    elif keyType == FieldType.int32:
        return True
    elif keyType == FieldType.uint32:
        return True
    else:
        return False

class DefType():
    base = "base"
    enum = "enum"
    struct = "struct"
    inline_struct = "inline_struct"
    proto = "proto"


def IsDefType(defType):
    if defType == DefType.enum:
        return True
    elif defType == DefType.struct:
        return True
    else:
        return False
    

class EnumData:
    def __init__(self):
        self.type = DefType.enum
        self.name = ""
        self.enumList = []
        self.valueType = ""

class StructData:
    def __init__(self):
        self.type = DefType.struct
        self.name = ""
        self.fieldList = []

class ProtoData:
    def __init__(self):
        self.type = DefType.proto
        self.id = -1
        self.inList = []
        self.outList = []

class FieldData:
    def __init__(self):
        self.name = ""
        self.line = ""
        self.lineNum = 0
        self.type = ""
        self.typeStruct = None
        self.opts = {}
        self.defType = ""

protoFilePath = ""
goOutPath = ""
luaOutPath = ""
goPackageName = ""

protoFiles = {}
commonProtoFiles = {}

allTypes = {}
commonTypes = {}

fileParses = {}
commonFileParses = {}

isExportGo = False
isExportClient = True
isExportCS = False