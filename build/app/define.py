import build.define

#1.unity.exe路径 2.工程路径 3.命令行模式运行 4.uuid 5.平台类型 6.客户端输出名 7.内置资源大小(mb单位) 8.渠道 9.游戏名
buildCmd = "%s -projectPath %s%s -executeMethod Build.MakeApp -args:\
uuid=%s,\
platform=%s,\
outName=%s,\
assetsLen=%s,\
channel=%s,\
gameName=%s,\
channelSubPrefix=%s,\
baseSettingFile=%s,\
isSyncUpdate=%s"

executeCmd = ""