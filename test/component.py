def OnCommand():
    return "test","测试代码"

def OnAwake():
    pass

def OnExecute(params):
    testData = {}
    testData["a"] = True
    testData[""] = True

    print("长度",len(testData))


def OnComplete():
    pass

def OnHelp():
    return "\
[test]           测试代码"