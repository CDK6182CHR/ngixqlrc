import json
import re


def lrc_time_to_secs(mark:str)->float:
    """
    lrc的时间戳转换为秒数。入参不含方括号。
    """
    sp1 = mark.split(':')
    res = int(sp1[0])*60
    res += float(sp1[1])
    return res


def tm_to_str(secs:float)->str:
    """
    将秒数转换为下列格式：
    00:00:05,505
    """
    h = int(secs // 3600)
    m = int((secs%3600)//60)
    s = secs-3600*h-60*m
    si = int(s)
    ms = int(round((s-si)*1000))
    return f'{h:02d}:{m:02d}:{si:02d},{ms:03d}'



def write_srt_item(fout, num, tm_start:float, tm_to:float, txt):
    fout.write(f'{num}\n')
    fout.write(f'{tm_to_str(tm_start)} --> {tm_to_str(tm_to)} \n')
    fout.write(f'{txt}\n\n')



def lrc_to_srt(src:str,dst:str,translate:int=0):
    """
    将LRC格式的歌词文件转换成SRT字幕格式 用于导入PR
    """
    fp = open(src,encoding='utf-8',errors='ignore')
    fout = open(dst, 'w', encoding='utf-8-sig', errors='ignore')
    content_last=None
    tmmark_last:float = None
    tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')
    n = 0
    for line in fp:
        line = line.strip()
        if not line:
            continue
        tmmark_r = re.search(tmmark_reg, line)
        if tmmark_r:
            tmmark_s = tmmark_r.groups()[0]
            tmmark = lrc_time_to_secs(tmmark_s)+translate
            content = line.lstrip(tmmark_r.group())
            if content_last:
                n+=1
                write_srt_item(fout, n, tmmark_last, tmmark, content_last)

            content_last = content
            tmmark_last = tmmark
            
        else:
            # 暂定没有时间标记就忽略本行
            pass
    if tmmark_last:
        n+=1
        write_srt_item(fout, n, tmmark_last, tmmark_last+5, content_last)
    
    fp.close()
    fout.close()


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Convert LRC file to subtitle file (*.srt)')
    parser.add_argument('src', nargs=1, type=str, help='source *.lrc file')
    parser.add_argument('dst', nargs='?', default=None,
         type=str, help='output *.srt file, default as <src>.srt')
    parser.add_argument('-t', '--translate', dest='translate', nargs=1, default=0,
        type=int, required=False, 
        help='translate the timeline by given value (in seconds)')
    
    p = parser.parse_args(sys.argv[1:])
    src = p.src[0]
    dst = p.dst
    if dst is None:
        dst = src+'.srt'
    else:
        dst = dst[0]
    translate = p.translate
    
    lrc_to_srt(src, dst, translate)


