import random
import requests

class HttpRequest:
    uniqueId = 0

    def __init__(self):
        self.id = 0
        self.url = None
        self.param = None
        self.crc = 0
        self.timeout = 0
        self.lastProgress = 0.0
        self.retryCount = 1

        self.onUpdateProgress = None
        self.onFail = None

        self.lastSize = 0
        self.maxSize = 0

        self.useRandom = False

        self.data = bytearray()

    def GetId():
        uniqueId = uniqueId + 1
        return uniqueId


    def Request(self):
        httpPath = self.url

        if self.useRandom:
            httpPath += "?random=" + str(random.randint(0,1000))

        count = 0
        r = requests.get(httpPath)

        for chunk in r.iter_content(chunk_size = 102400):
            if chunk:
                #f.write(chunk)
                count += len(chunk)
                #self.data.append(chunk)
                print("count",len(chunk))
                #configValue.opts["valueList"].append(dictKey.value)
                #print("增加count",count)

        print("总长度",len(r.content))
        a = r.content[0:4]
        print("a",len(a))