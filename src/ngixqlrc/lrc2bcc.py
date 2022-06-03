from distutils import errors
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



def lrc_to_bcc(src:str,dst:str,translate:int=0):
    """
    将LRC格式的歌词文件转换成B站字幕bcc格式。
    """
    res = {
    "font_size": 0.4,
    "font_color": "#FFFFFF",
    "background_alpha": 0.5,
    "background_color": "#9C27B0",
    "Stroke": "none",
    "body": [
        # {
        #     "from": 31.924998,
        #     "to": 36.924998,
        #     "location": 2,
        #     "content": "若有人兮山之阿"
        # }
    ]}
    fp = open(src,encoding='utf-8',errors='ignore')
    content_last=None
    tmmark_last:float = None
    tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')
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
                res['body'].append({
                    "from":tmmark_last,
                    "to":tmmark,
                    "location":2,
                    "content":content_last
                })

            content_last = content
            tmmark_last = tmmark
            
        else:
            # 暂定没有事件标记就忽略本行
            pass
    if tmmark_last:
         res['body'].append({
                    "from":tmmark_last,
                    "to":tmmark_last+5,
                    "location":2,
                    "content":content_last
                })
    
    fp.close()
    with open(dst, 'w', encoding='utf-8', errors='ignore') as fout:
        json.dump(res, fout, ensure_ascii=False)


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Convert LRC file to bilibili barrage file (*.bcc)')
    parser.add_argument('src', nargs=1, type=str, help='source *.lrc file')
    parser.add_argument('dst', nargs='?', default=None,
         type=str, help='output *.bcc file, default as <src>.bcc')
    parser.add_argument('-t', '--translate', dest='translate', nargs=1, default=0,
        type=int, required=False, 
        help='translate the timeline by given value (in seconds)')
    
    p = parser.parse_args(sys.argv[1:])
    src = p.src[0]
    dst = p.dst
    if dst is None:
        dst = src+'.bcc'
    else:
        dst = dst[0]
    translate = p.translate

    lrc_to_bcc(src, dst, translate)


