import hashlib

def FormatDQuote(value):
    strLen = len(value)
    if strLen >=2:
        if value[0] == "\"" and value[strLen-1] == "\"":
            value = value[1:strLen-1]
        elif value[0] == "'" and value[strLen-1] == "'":
            value = value[1:strLen-1]
    
    return "\"%s\"" % value.replace("\"","\\\"")


def FormatWithoutQuote(value):
    strLen = len(value)
    if strLen >=2:
        if value[0] == "\"" and value[strLen-1] == "\"":
            value = value[1:strLen-1]
        elif value[0] == "'" and value[strLen-1] == "'":
            value = value[1:strLen-1]
    
    return value

def FormatSQuote(value):
    strLen = len(value)
    if strLen >=2:
        if value[0] == "\"" and value[strLen-1] == "\"":
            value = value[1:strLen-1]
        elif value[0] == "'" and value[strLen-1] == "'":
            value = value[1:strLen-1]
    
    return "\'%s\'" % value.replace("\"","\\\"")

def FirstCharUpper(str):
    return str[:1].upper() + str[1:]

def GetMd5(str):
    return hashlib.md5(str.encode()).hexdigest()

def GetMd5ByLen(s):
    return hashlib.md5(s.encode()).hexdigest() + str(len(s))