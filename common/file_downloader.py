class FileDownloader:
    def __init__(self):
        self.maxDownloadCount = 0
        self.waitRequests = []
        self.requests = {}
        self.failFiles = []

        self.onUpdateProgress = None
        self.onComplete = None
        self.onFileComplete = None
        self.onFileFail = None


    def AddDownloadFile(file,url,maxLen,crc):
        pass

    
