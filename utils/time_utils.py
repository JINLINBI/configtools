import time
import datetime

def GetTimeInterval(beginTime):
    return datetime.datetime.now() - beginTime


def GetFormat_h_m_s(time):
    m, s = divmod(time.seconds, 60)
    h, m = divmod(m, 60)
    return h,m,s