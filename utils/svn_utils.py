import os
# import svn.local
# import svn.constants
from utils import io_utils
import pprint

def Update(path):
    client = svn.local.LocalClient(path)

    client.cleanup()
    client.update()

    waitRemovePaths = []
    waitRevertPaths = []
    unversionedPaths = {}

    for s in client.status():
        
        filePath = None
        if io_utils.ExistFolder(s.name):
            filePath = io_utils.GetAbsPath(s.name,True)
        elif io_utils.ExistFile(s.name):
            filePath = io_utils.GetAbsPath(s.name,False)

        if s.type == svn.constants.ST_ADDED :
            waitRemovePaths.append(filePath)
        elif s.type == svn.constants.ST_MISSING:
            waitRemovePaths.append(filePath)
        elif s.type == svn.constants.ST_UNVERSIONED:
            waitRemovePaths.append(filePath)
            unversionedPaths[filePath] = True
        elif s.type == svn.constants.ST_CONFLICTED:
            waitRevertPaths.append(filePath)
        elif s.type == svn.constants.ST_DELETED:
            waitRevertPaths.append(filePath)

        #pprint.pprint(s)

    #print("要移除的路径")
    #pprint.pprint(waitRemovePaths)

    #print("要还原的路径")
    #pprint.pprint(waitRevertPaths)

    rmPaths = ""
    for path in waitRemovePaths:
        io_utils.DeleteFolder(path)
        io_utils.DeleteFile(path)
        exist =  path in unversionedPaths
        if exist == False:
            rmPaths = rmPaths + path + " "

     
    
    if rmPaths != "":
        client.remove(rmPaths)

    revertPaths = ""
    for path in waitRevertPaths:
        if io_utils.ExistPath(path):
            revertPaths = revertPaths + path + " "

    if revertPaths != "":
        client.revert(revertPaths)
        

    
