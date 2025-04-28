from utils import io_utils
from utils import string_utils

import proto.define
import proto.config

index = 0

def ExportFile(fileParse):
    fileName = io_utils.GetFileNameWithoutExtension(fileParse.filePath)
    outFile = proto.config.goOutPath + fileName + ".go"
    io_utils.CreateFolderByFile(outFile)

    file = open(outFile,encoding="utf-8", mode="w")
    file.write("package %s\n" % proto.config.goPackageName)
    file.write("\n")
    file.write("import \"%s\"\n" % proto.config.goByteUtilsPath)

    for data in fileParse.dataList:
        if data.type == proto.define.DefType.enum:
            WriteEnum(file,data)
        elif data.type == proto.define.DefType.struct:
            WriteStruct(file,data)
        elif data.type == proto.define.DefType.proto:
            WriteProtoIn(file,data)
            WriteProtoOut(file,data)

    file.flush()
    file.close()

def WriteEnum(file,enum):
    #定义
    file.write("\n")
    file.write("type %s %s\n" % (enum.name,enum.valueType))
    file.write("const(\n")
    for field in enum.enumList:
        file.write("    %s_%s %s = %s\n" % (enum.name,string_utils.FirstCharUpper(field["key"]),enum.name,field["value"]))
    file.write(")\n")

    #写入
    file.write("\n")
    file.write("func (e *%s) Write(stream *%s.ByteStream) {\n" % (enum.name,proto.config.goByteUtilsName))
    file.write("    stream.%s( %s(*e) )\n" % (GetWriteFun(enum.valueType),enum.valueType))
    file.write("}\n")

    #读取
    file.write("\n")
    file.write("func (e *%s) Read(stream *%s.ByteStream) {\n" % (enum.name,proto.config.goByteUtilsName))
    file.write("    *e = %s( stream.%s() ) \n" % (enum.name,GetReadFun(enum.valueType)))
    file.write("}\n")


def WriteStruct(file,struct):
    ResetIndex()
    #定义
    file.write("\n")
    file.write("type %s struct {\n" % (struct.name))
    for field in struct.fieldList:
        WriteFieldDef(file,field,"    ")
    file.write("}\n")
    #写入
    file.write("\n")
    file.write("func (s *%s) Write(stream *%s.ByteStream) {\n" % (struct.name,proto.config.goByteUtilsName))
    for i, field in enumerate(struct.fieldList):
        if i > 0: file.write("\n")
        WriteField(file,field,"s.","","    ")
    file.write("}\n")
    #读取
    file.write("\n")
    file.write("func (s *%s) Read(stream *%s.ByteStream) {\n" % (struct.name,proto.config.goByteUtilsName))
    for i, field in enumerate(struct.fieldList):
        if i > 0: file.write("\n")
        ReadField(file,field,"s.","","    ")
    file.write("}\n")

def WriteProtoIn(file,protoData):
    ResetIndex()
    #定义
    file.write("\n")
    file.write("type In%s struct {\n" % (str(protoData.id)))
    for field in protoData.inList:
        WriteFieldDef(file,field,"    ")
    file.write("}\n")
    #获取类型方法
    file.write("\n")
    file.write("func (in *In%s) GetType() string {\n" % (protoData.id))
    file.write("    return \"In%s\"\n" % (protoData.id))
    file.write("}\n")
    #Marshal
    file.write("\n")
    file.write("func (in *In%s) Marshal() ([]byte, error) {\n" % (protoData.id))
    file.write("    return nil,nil\n")
    file.write("}\n")

    file.write("\n")
    file.write("func (in *In%s) Unmarshal(data []byte) error {\n" % (protoData.id))
    file.write("    stream := %s.NewByteStream()\n" % proto.config.goByteUtilsName)
    file.write("    stream.SetBytes(data)\n")
    for i, field in enumerate(protoData.inList):
        if i > 0: file.write("\n")
        ReadField(file,field,"in.","","    ")
    file.write("    return nil\n")
    file.write("}\n")

def WriteProtoOut(file,protoData):
    ResetIndex()
    #定义
    file.write("\n")
    file.write("type Out%s struct {\n" % (str(protoData.id)))
    for field in protoData.outList:
        WriteFieldDef(file,field,"    ")
    file.write("}\n")
    #获取类型方法
    file.write("\n")
    file.write("func (out *Out%s) GetType() string {\n" % (protoData.id))
    file.write("    return \"Out%s\"\n" % (protoData.id))
    file.write("}\n")
    #Marshal
    file.write("\n")
    file.write("func (out *Out%s) Marshal() ([]byte, error) {\n" % (protoData.id))
    file.write("    stream := %s.NewByteStream()\n" % proto.config.goByteUtilsName)
    file.write("    stream.WriteUInt16(%s)\n" % (protoData.id))
    for _, field in enumerate(protoData.outList):
        file.write("\n")
        WriteField(file,field,"out.","","    ")
    file.write("\n")
    file.write("    return stream.GetBuffer(),nil\n")
    file.write("}\n")
    #Unmarshal
    file.write("\n")
    file.write("func (out *Out%s) Unmarshal(data []byte) error {\n" % (protoData.id))
    file.write("    return nil\n")
    file.write("}\n")


def WriteFieldStructDef(file,struct,space):
    for field in struct.fieldList:
        WriteFieldDef(file,field,space + "    ")
    file.write("%s}\n" % space)

def WriteFieldDef(file,field,space):
    fieldName = string_utils.FirstCharUpper(field.name)
    if field.type == "list":
        if field.defType == proto.define.DefType.inline_struct:
            file.write("%s%s []struct {\n" % (space,fieldName))
            WriteFieldStructDef(file,field.typeStruct,space)
        else:
            file.write("%s%s []%s\n" % (space,fieldName,field.opts["type"]))
    elif field.type == "dict":
        if field.defType == proto.define.DefType.inline_struct:
            file.write("%s%s map[%s]struct {\n" % (space,fieldName,field.opts["key"]))
            WriteFieldStructDef(file,field.typeStruct,space)
        else:
            file.write("%s%s map[%s]%s\n" % (space,fieldName,field.opts["key"],field.opts["value"]))
    else:
        if field.defType == proto.define.DefType.inline_struct:
            file.write("%s%s struct {\n" % (space,fieldName))
            WriteFieldStructDef(file,field.typeStruct,space)
        else:
            typeStr = proto.define.TypeTo(field.type)
            file.write("%s%s %s\n" % (space,fieldName,typeStr))


def GetFieldStructDef(struct,defList,isRoot,space):
    for field in struct.fieldList:
        GetFieldDef(field,defList,space + "    ")

    defList[-1] = defList[-1] + "}"

def GetFieldDef(field,defList,space):
    isRoot = space == ""
    fieldName = string_utils.FirstCharUpper(field.name)

    if field.type == "list":
        if field.defType == proto.define.DefType.inline_struct and isRoot:
            defList.append("%s[]struct {" % (space))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif field.defType == proto.define.DefType.inline_struct and not isRoot:
            defList.append("%s%s []struct {" % (space,fieldName))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif isRoot:
            defList.append("%s[]%s" % (space,field.opts["type"]))
        else:
            defList.append("%s%s []%s" % (space,fieldName,field.opts["type"]))
    elif field.type == "dict":
        if field.defType == proto.define.DefType.inline_struct and isRoot:
            defList.append("%sstruct {" % (space))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif field.defType == proto.define.DefType.inline_struct and not isRoot:
            defList.append("%s%s map[%s]struct {" % (space,fieldName,field.opts["key"]))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif isRoot:
            defList.append("%s%s" % (space,field.opts["value"]))
        else:
            defList.append("%s%s map[%s]%s" % (space,fieldName,field.opts["key"],field.opts["value"]))
    else:
        if field.defType == proto.define.DefType.inline_struct and isRoot:
            defList.append("%sstruct {" % (space))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif field.defType == proto.define.DefType.inline_struct and not isRoot:
            defList.append("%s%s struct {" % (space,fieldName))
            GetFieldStructDef(field.typeStruct,defList,isRoot,space)
        elif isRoot:
            typeStr = proto.define.TypeTo(field.type)
            defList.append("%s%s" % (space,typeStr))
        else:
            typeStr = proto.define.TypeTo(field.type)
            defList.append("%s%s %s" % (space,fieldName,typeStr))

def WriteFieldStruct(file,struct,abbrName,fieldPath,space):
    for field in struct.fieldList:
        WriteField(file,field,abbrName,fieldPath,space)

def WriteField(file,field,abbrName,fieldPath,space):
    fieldName = string_utils.FirstCharUpper(field.name)
    if field.type == "list":
        index = GetIndex()

        file.write("%sstream.WriteUInt16(uint16(len(%s%s%s)))\n" % (space,abbrName,fieldPath,fieldName))
        file.write("%sfor _,v%s := range %s%s%s {\n" % (space,index,abbrName,fieldPath,fieldName))

        if field.defType == proto.define.DefType.inline_struct:
            WriteFieldStruct(file,field.typeStruct,"","v%s." % index,space + "    ")
        elif field.defType == proto.define.DefType.base:
            file.write("%s    stream.%s(v%s)\n" % (space,GetWriteFun(field.opts["type"]),index))
        else:
            file.write("%s    v%s.Write(stream)\n" % (space,index))

        file.write("%s}\n" % space)
    elif field.type == "dict":
        index = GetIndex()
        file.write("%sstream.WriteUInt16(uint16(len(%s%s%s)))\n" % (space,abbrName,fieldPath,fieldName))
        file.write("%sfor k%s,v%s := range %s%s%s {\n" % (space,index,index,abbrName,fieldPath,fieldName))
        file.write("%s    stream.%s(k%s)\n" % (space,GetWriteFun(field.opts["key"]),index))

        if field.defType == proto.define.DefType.inline_struct:
            WriteFieldStruct(file,field.typeStruct,"","v%s." % index,space + "    ")
        elif field.defType == proto.define.DefType.base:
            file.write("%s    stream.%s(v%s)\n" % (space,GetWriteFun(field.opts["value"]),index))
        else:
            file.write("%s    v%s.Write(stream)\n" % (space,index))

        file.write("%s}\n" % space)
    else:
        if field.defType == proto.define.DefType.inline_struct:
            WriteFieldStruct(file,field.typeStruct,abbrName,fieldPath + fieldName + ".",space)
        elif field.defType == proto.define.DefType.base:
            file.write("%sstream.%s(%s%s%s)\n" % (space,GetWriteFun(field.type),abbrName,fieldPath,fieldName ))
        else:
            file.write("%s%s%s%s.Write(stream)\n" % (space,abbrName,fieldPath,fieldName))


def ReadFieldStruct(file,struct,abbrName,fieldPath,space):
    for field in struct.fieldList:
        ReadField(file,field,abbrName,fieldPath,space)

def ReadField(file,field,abbrName,fieldPath,space):
    fieldName = string_utils.FirstCharUpper(field.name)
    if field.type == "list":
        index = GetIndex()
        file.write("%slen%s := int(stream.ReadUInt16())\n" % (space,index))

        if field.defType == proto.define.DefType.inline_struct:
            defList = []
            GetFieldDef(field,defList,"")
            typeStr = defList[0] + ("\n" + space) + ("\n" + space).join(defList[1:])
            file.write("%s%s%s%s = make(%s,len%s,len%s)\n" % (space,abbrName,fieldPath,fieldName,typeStr,index,index))
            file.write("%sfor i%s := 0; i%s < len%s; i%s++ {\n" % (space,index,index,index,index))
            ReadFieldStruct(file,field.typeStruct,abbrName, "%s%s[i%s]." % (fieldPath,fieldName,index),space + "    ")
        else:
            file.write("%s%s%s%s = make([]%s,len%s,len%s)\n" % (space,abbrName,fieldPath,fieldName,field.opts["type"],index,index))
            file.write("%sfor i%s := 0; i%s < len%s; i%s++ {\n" % (space,index,index,index,index))

            if field.defType == proto.define.DefType.base:
                file.write("%s    %s%s%s[i%s] = stream.%s()\n" % (space,abbrName,fieldPath,fieldName,index,GetReadFun(field.opts["type"])))
            elif field.defType == proto.define.DefType.enum:
                file.write("%s    %s%s%s[i%s].Read(stream)\n" % (space,abbrName,fieldPath,fieldName,index))
            else:
                file.write("%s    %s%s%s[i%s].Read(stream)\n" % (space,abbrName,fieldPath,fieldName,index))
            
        file.write("%s}\n" % space)
    elif field.type == "dict":
        index = GetIndex()
        if field.defType == proto.define.DefType.inline_struct:
            defList = []
            GetFieldDef(field,defList,"")
            typeStr = defList[0] + ("\n" + space) + ("\n" + space).join(defList[1:])

            file.write("%s%s%s%s = make(map[%s]%s)\n" % (space,abbrName,fieldPath,fieldName,field.opts["key"],typeStr))
            file.write("%sfor i%s := 0; i%s < int(stream.ReadUInt16()); i%s++ {\n" % (space,index,index,index))
            file.write("%s    k%s := stream.%s()\n" % (space,index,GetReadFun(field.opts["key"])))

            typeStr = defList[0] + ("\n" + space + "    ") + ("\n" + space + "    ").join(defList[1:]) + "{}"
            file.write("%s    v%s := %s\n" % (space,index,typeStr))

            ReadFieldStruct(file,field.typeStruct,"","v%s." % index,space + "    ")
            file.write("%s    %s%s%s[k%s] = v%s\n" % (space,abbrName,fieldPath,fieldName,index,index))
        else:
            file.write("%s%s%s%s = make(map[%s]%s)\n" % (space,abbrName,fieldPath,fieldName,field.opts["key"],field.opts["value"]))
            file.write("%sfor i%s := 0; i%s < int(stream.ReadUInt16()); i%s++ {\n" % (space,index,index,index))
            file.write("%s    key := stream.%s()\n" % (space,GetReadFun(field.opts["key"])))
            
            if field.defType == proto.define.DefType.base:
                file.write("%s    value := stream.%s()\n" % (space,GetReadFun(field.opts["value"])))
            elif field.defType == proto.define.DefType.enum:
                file.write("%s    value := %s\n" % (space,field.opts["value"]))
                file.write("%s    value.Read(stream)\n" % space)
            else:
                file.write("%s    value := %s{}\n" % (space,field.opts["value"]))
                file.write("%s    value.Read(stream)\n" % space)

            file.write("%s    %s%s%s[key] = value\n" % (space,abbrName,fieldPath,fieldName))
        file.write("%s}\n" % space)
    else:
        if field.defType == proto.define.DefType.inline_struct:
            ReadFieldStruct(file,field.typeStruct,abbrName,fieldPath + fieldName + ".",space)
        else:
            if field.defType == proto.define.DefType.base:
                file.write("%s%s%s%s = stream.%s()\n" % (space,abbrName,fieldPath,fieldName,GetReadFun(field.type)))
            elif field.defType == proto.define.DefType.enum:
                file.write("%s%s%s%s.Read(stream)\n" % (space,abbrName,fieldPath,fieldName))
            else:
                file.write("%s%s%s%s = %s{}\n" % (space,abbrName,fieldPath,fieldName,field.type))
                file.write("%s%s%s%s.Read(stream)\n" % (space,abbrName,fieldPath,fieldName))

def GetWriteFun(dataType):
    if dataType == proto.define.FieldType.string:
        return "WriteString"
    elif dataType == proto.define.FieldType.bool:
        return "WriteBool"
    elif dataType == proto.define.FieldType.int8:
        return "WriteInt8"
    elif dataType == proto.define.FieldType.uint8:
        return "WriteUInt8"
    elif dataType == proto.define.FieldType.int16:
        return "WriteInt16"
    elif dataType == proto.define.FieldType.uint16:
        return "WriteUInt16"
    elif dataType == proto.define.FieldType.int32:
        return "WriteInt32"
    elif dataType == proto.define.FieldType.uint32:
        return "WriteUInt32"
    elif dataType == proto.define.FieldType.float:
        return "WriteFloat32"
    elif dataType == proto.define.FieldType.double:
        return "WriteFloat64"
    else:
        return "Write"

def GetReadFun(dataType):
    if dataType == proto.define.FieldType.string:
        return "ReadString"
    elif dataType == proto.define.FieldType.bool:
        return "ReadBool"
    elif dataType == proto.define.FieldType.int8:
        return "ReadInt8"
    elif dataType == proto.define.FieldType.uint8:
        return "ReadUInt8"
    elif dataType == proto.define.FieldType.int16:
        return "ReadInt16"
    elif dataType == proto.define.FieldType.uint16:
        return "ReadUInt16"
    elif dataType == proto.define.FieldType.int32:
        return "ReadInt32"
    elif dataType == proto.define.FieldType.uint32:
        return "ReadUInt32"
    elif dataType == proto.define.FieldType.float:
        return "ReadFloat32"
    elif dataType == proto.define.FieldType.double:
        return "ReadFloat64"
    else:
        return "Read"

def GetIndex():
    global index
    index += 1
    return index

def ResetIndex():
    global index
    index = 0