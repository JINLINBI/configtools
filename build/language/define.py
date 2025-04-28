

#1.unity.exe路径 2.工程路径 3.命令行模式运行 4.uuid 5.平台类型
#unity一共收到5个参数
buildCmd = "%s -projectPath %s%s -executeMethod Build.MakeLanguagePack -args:\
uuid=%s,\
platform=%s,\
channelSubPrefix=%s,\
channel=%s,\
language=%s,\
noticeError=%s"