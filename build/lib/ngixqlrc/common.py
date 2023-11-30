

def lrc_time_to_secs(mark:str)->float:
    """
    lrc的时间戳转换为秒数。入参不含方括号。
    """
    sp1 = mark.split(':')
    res = int(sp1[0])*60
    res += float(sp1[1])
    return res

