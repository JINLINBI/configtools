import os
import shutil
import json
import hashlib

def ExistFolder(folderPath):
    return os.path.isdir(folderPath)

def ExistFile(filePath):
    return os.path.isfile(filePath)

def ExistPath(path):
    return os.path.exists(path)

def DeleteFile(file):
    if ExistFile(file):
        os.remove(file)

def DeleteFolder(folder):
    if ExistFolder(folder):
        shutil.rmtree(folder,ignore_errors=True)

def CopyFile(srcFile,destFile):
    CreateFolderByFile(destFile)
    shutil.copyfile(srcFile,destFile)

def CleanFolder(folder):
    if not ExistFolder(folder):
        return

    paths = os.listdir(folder)
    for localPath in paths:
        path = folder + "/" + localPath
        if ExistFolder(path):
            DeleteFolder(path)
        elif ExistFile(path):
            DeleteFile(path)

def GetFileName(file):
    return os.path.basename(file)

def GetFileNameWithoutExtension(file):
    file = os.path.basename(file)
    return os.path.splitext(file)[0]

def RejectPath(srcPath,rejectPath):
    index = srcPath.find(rejectPath)
    if index == -1:return srcPath
    return srcPath.replace(rejectPath,"")

def GetFiles(path,types = "",isRecursive = True,isExclude = False):
    if not ExistFolder(path):
        return []

    if not types:
        types = ""

    if types == "" and isExclude:
        return []
    
    typeLen = len(types)

    if typeLen > 0 and (types[0] == "," or types[typeLen - 1] == "," or types.find(",,") != -1):
        return []

    isAll = False
    typeFiles = {}
    if types != "":
        for typeStr in iter(types.split(",")):
            if typeStr == "*":
                typeFiles[""] = True
            else:
                typeFiles[typeStr] = True
    else:
        isAll = True

    fileList = []
    
    for curPath, _, files in os.walk(path):
        if not isRecursive and curPath != path:
            continue

        for fileName in files:
            ext = GetExt(fileName)

            if not isExclude and (isAll or (ext in typeFiles)):
                filePath = os.path.join(curPath,fileName).replace("\\","/")
                fileList.append(filePath)
            elif isExclude and not (ext in typeFiles):
                filePath = os.path.join(curPath,fileName).replace("\\","/")
                fileList.append(filePath)

    return fileList

def GetPathFiles(path,types = "",isExclude = False,isRecursive = True):
    files = []

    if ExistFile(path):
        files.append(path)
    elif ExistFolder(path):
        files = GetFiles(path,types,isExclude,isRecursive)

    return files

def GetFile():
    pass

def GetAbsPath(path):
    if path == "":
        return path

    absPath = os.path.abspath(path).replace("\\","/").replace("//","/")
    pathLen = len(absPath)
    ext = GetExt(path)

    if ext == "" and absPath[pathLen-1] != "/":
        absPath += "/"
    
    return absPath

def GetExt(file):
    return os.path.splitext(file)[-1][1:]

def GetPathDirectory(path):
    path = os.path.dirname(path)
    return GetAbsPath(path)

def CreateFolderByFile(file):
    folderPath = os.path.dirname(file)
    CreateFolder(folderPath)

def CreateFolder(folderPath):
    if os.path.exists(folderPath) == True:return
    os.makedirs(folderPath)

def WriteAllText(path,contents):
    with open(path, 'w',encoding='utf-8') as fp:
        fp.write(contents)

def ReadAllText(file):
	if not ExistFile(file):
		return ""
	
	with open(file) as file_obj:
		return file_obj.read()

def GetFilePath(file):
    path = os.path.abspath(file)
    return GetAbsPath(path)

def LoadJson(file):
    f = open(file, encoding='utf-8')
    content = f.read()
    f.close()
    return json.loads(content)

def SafeLoadJson(file):
    if not ExistFile(file):
        return None

    try:
        file = open(file, encoding='utf-8')
        content = file.read()
        file.close()
        return json.loads(content)
    except:
        return None

def GetAbsPathByRoot(rootPath,path):
    if path.startswith("./") or path.startswith("../"):
        return GetAbsPath(rootPath + "/" + path)
    else:
        return GetAbsPath(path)

def GetFileMD5(file):
    if not file or file == "" or not ExistFile(file):
        return ""
    
    m = hashlib.md5()
    with open(file,'rb') as fobj:
        while True:
            data = fobj.read(4096)
            if not data:
                break
            m.update(data)

    return m.hexdigest()