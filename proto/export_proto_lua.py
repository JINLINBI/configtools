
import proto.define
import proto.config
from utils import io_utils

def ExportFile(fileParse):
    fileName = io_utils.GetFileNameWithoutExtension(fileParse.filePath)
    outFile = proto.config.luaOutPath + ("proto_%s.lua" % fileName)
    io_utils.CreateFolderByFile(outFile)

    file = open(outFile,encoding="utf-8", mode="w")

    num = 0
    for data in fileParse.dataList:
        if data.type == proto.define.DefType.proto:
            num += 1
            if num > 1:file.write("\n\n")
            WritePorot(file,data)
            
    file.flush()
    file.close()


def WritePorot(file,proto):
    file.write("protos[%s] =\n" % (proto.id))
    file.write("{\n")

    #In
    file.write("    In =\n")
    file.write("    {\n")
    for _, field in enumerate(proto.inList):
        WriteField(file,field,"        ")
    file.write("    },\n")

    #Out
    file.write("    Out =\n")
    file.write("    {\n")
    for _, field in enumerate(proto.outList):
        WriteField(file,field,"        ")
    file.write("    }\n")

    file.write("}")

def WriteField(file,field,space):
    if field.type == "list":
        if field.defType == proto.define.DefType.base:
            file.write("%s{name = \"%s\", type = \"list\", fields = { type = \"%s\" }},\n" % (space,field.name,field.opts["type"]))
        elif field.defType == proto.define.DefType.enum:
            enum = proto.define.allTypes[field.opts["type"]]
            file.write("%s{name = \"%s\", type = \"list\", fields = { type = \"%s\" }},\n" % (space,field.name,enum.valueType))
        elif field.defType == proto.define.DefType.struct:
            file.write("%s{name = \"%s\", type = \"list\", fields = {\n" % (space,field.name))
            struct = proto.define.allTypes[field.opts["type"]]
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))
        elif field.defType == proto.define.DefType.inline_struct:
            file.write("%s{name = \"%s\", type = \"list\", fields = {\n" % (space,field.name))
            struct = field.typeStruct
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))
    elif field.type == "dict":
        if field.defType == proto.define.DefType.base:
            file.write("%s{name = \"%s\", type = \"dict\",key = \"%s\",fields = { type = \"%s\" }},\n" % (space,field.name,field.opts["key"],field.opts["value"]))
        elif field.defType == proto.define.DefType.enum:
            enum = proto.define.allTypes[field.opts["value"]]
            file.write("%s{name = \"%s\", type = \"dict\",key = \"%s\",fields = { type = \"%s\" }},\n" % (space,field.name,field.opts["key"],enum.valueType))
        elif field.defType == proto.define.DefType.struct:
            file.write("%s{name = \"%s\", type = \"dict\",key = \"%s\",fields = {\n" % (space,field.name,field.opts["key"]))
            struct = proto.define.allTypes[field.opts["value"]]
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))
        elif field.defType == proto.define.DefType.inline_struct:
            file.write("%s{name = \"%s\", type = \"dict\",key = \"%s\",fields = {\n" % (space,field.name,field.opts["key"]))
            struct = field.typeStruct
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))
    else:
        if field.defType == proto.define.DefType.base:
            file.write("%s{name = \"%s\", type = \"%s\"},\n" % (space,field.name,field.type))
        elif field.defType == proto.define.DefType.enum:
            enum = proto.define.allTypes[field.type]
            file.write("%s{name = \"%s\", type = \"%s\"},\n" % (space,field.name,enum.valueType))
        elif field.defType == proto.define.DefType.struct:
            file.write("%s{name = \"%s\", type = \"struct\", fields = {\n" % (space,field.name))
            struct = proto.define.allTypes[field.type]
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))
        elif field.defType == proto.define.DefType.inline_struct:
            file.write("%s{name = \"%s\", type = \"struct\", fields = {\n" % (space,field.name))
            struct = field.typeStruct
            for _, structField in enumerate(struct.fieldList):
                WriteField(file,structField,space + "    ")
            file.write("%s}},\n" % (space))