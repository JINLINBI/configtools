class BuildType:
    asset = "asset"
    app = "app"

class PlatformType:
    win     = "win"
    android = "android"
    ios     = "ios"

def IsPlatformType(platform):
    if platform == PlatformType.win:
        return True
    elif platform == PlatformType.android:
        return True
    elif platform == PlatformType.ios:
        return True
    else:
        return False

#executeCmd = "%s -projectPath %s -quit%s -executeMethod BuilderAsset.CmdBuildAsset %s %s %s %s" %(debugCmd,buildPlatform,buildVersion,buildId,buildAssetType)
platform = None
buildInfo = None
outPath = None


cuttinglLine = "--------------------------------------------------------"


runMode = ""

buildId = ""

localLogFile = "temp/log.json"
logFile = ""

unityLockfile = "Temp/UnityLockfile"

localLuaWarpPath = "Assets/XLua/Gen/"

buildFilePath = "Framework/Editor/Build/setting.json"
baseSettingFile = "Assets/Resources/base_setting.json"



luaWarpPath = ""

lock = None



