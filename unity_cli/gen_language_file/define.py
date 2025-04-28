
localLogFile = "Logs/gen_language_file_log.json"


#1.unity.exe路径 2.工程路径 3.命令行模式运行 4.uuid 5.语言列表
buildCmd = "%s -projectPath %s%s -executeMethod GenLanguageFile.Generate -args:\
uuid=%s,\
language=%s"