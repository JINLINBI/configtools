import gen_config.define
from utils.exception import LogException

def GetValue(value):
    try:
        temp = float(value)
        if temp % 1 == 0:return int(temp)
    except:
        return value


def GetInt(value):
    try:
        temp = float(value)
        if temp % 1 == 0:
            return int(temp)
        else:
            return None
    except:
        return None

def GetFloat(value):
    try:
        temp = float(value)
        return temp
    except:
        return None

def GetBool(value):
    try:
        v = str(value)
        if v == "是" or v == "true":
            return True
        elif v == "否" or v == "false":
            return False

        v = GetInt(value)
        if v == None:
            return None
        elif v == 1 :
            return True
        elif v == 0 :
            return False
        else:
            return False

    except:
        return None

def GetNumber(value):
    try:
        temp = float(value)
        if temp % 1 == 0:return int(temp)
    except:
        return None


def GetMixNumberType(value):
    try:
        temp = float(value)
        if temp % 1 == 0:
            return gen_config.define.FieldType.int
        else:
            return gen_config.define.FieldType.float
    except:
            return None

def GetMixBoolValue(value):
    if value == "true" or value == "false":
        return value
    else:
        return None


def ExcelColNameToNum(colName):
    if type(colName) is not str:
        return colName
    col = 0
    power = 1
    for i in range(len(colName)-1,-1,-1):
        ch = colName[i]
        col += (ord(ch)-ord('A')+1)*power
        power *= 26
    return col

def ExcelNumToColName(num):
    if type(num) is not int:
        return num
    str = ''
    while(not(num//26 == 0 and num % 26 == 0)):
        temp = 25
        if(num % 26 == 0):
            str += chr(temp+65)
        else:
            str += chr(num % 26 - 1 + 65)
        num //= 26
    return str[::-1]

def ErrorRowCol(err,row,col,localPath,sheetName):
	colName = gen_config.utils.ExcelNumToColName(col)
	raise LogException("%s(%s:%s:%s行,%s列(%s))" % (err,localPath,sheetName,row,col,colName))