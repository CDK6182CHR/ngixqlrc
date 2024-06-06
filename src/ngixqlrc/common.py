import typing as tp
import re

_tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')

def lrc_time_to_secs(mark:str)->float:
    """
    lrc的时间戳转换为秒数。入参不含方括号。
    """
    sp1 = mark.split(':')
    res = int(sp1[0])*60
    res += float(sp1[1])
    return res


def parse_lrc_line(line:str)->tp.Tuple[tp.Optional[float], str]:
    """Process a line in LRC file, return time mark and content"""
    tmmark_r = re.search(_tmmark_reg, line)
    if tmmark_r:
        tmmark_s = tmmark_r.groups()[0]
        tmmark = lrc_time_to_secs(tmmark_s)
        content = line.lstrip(tmmark_r.group())
        return tmmark, content
    else:
        return None, line
    

def format_lrc_line(tmmark:tp.Optional[float], content:str)->str:
    if tmmark is not None:
        # in principle, the sign should be positive...
        sign = 1
        if tmmark < 0:
            sign = -1
            tmmark = -tmmark
        sub_secs = tmmark % 1.0
        secs = int(round(tmmark-sub_secs))
        tmmark_s = f'{secs//60:02d}:{tmmark%60:05.2f}'
        return f'[{tmmark_s}]{content}'
    else:
        return content
