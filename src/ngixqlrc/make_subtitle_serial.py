import imgkit
from lxml import etree
from lxml.html import builder as E
import re
import os
import copy
from .common import lrc_time_to_secs
from .html_commom import generate_html_table, parse_config

__tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')


def sec_to_timestamp(sec:float, timebase:int)->int:
    """
    秒数转时间戳。
    """
    return int(round(sec/(1.0/timebase)))


def generate_line_html(cont_cn, cont_latin, extra_css=None):
    """
    :param: cont_cn  中文歌词，输入文件的一行，不含时间戳。以逐个字符分解到单元格。
    :param: cont_latin  歌词注音，其实不一定只能是拉丁字母。以空格分解到单元格。
    中文歌词中，以竖线|标记换行点，注音中不使用这个规则（不要在注音中加竖线！）。
    换行点同时适用于中文和注音。
    """
    # 首先预处理，搞换行符
    # 中文歌词遍历一遍，确定换行符位置
    br_after = set()
    i = 0
    for ch in cont_cn:
        if ch.isspace():
            continue
        elif ch == '|':
            br_after.add(i)
        else:
            i += 1
    
    cn_lines = cont_cn.split('|')
    lt_lines = []
    i = 0
    cur_line = []
    for word in cont_latin.split():
        cur_line.append(word)
        i += 1
        if i in br_after:
            lt_lines.append(' '.join(cur_line))
            cur_line = []
        
    if cur_line:
        lt_lines.append(' '.join(cur_line))
    while len(lt_lines) < len(cn_lines):
        lt_lines.append('')

    root = etree.Element('p')

    for cn_line, lt_line in zip(cn_lines, lt_lines):
        table = generate_html_table(cn_line,lt_line)
        root.append(table)
        etree.SubElement(root, 'p')

    css = E.STYLE(type='text/css')
    css.text = """
        .LyricPage {
            background: rgba(25,255,255,.0);
        }
        .LyricTable {
            /* border-style: double; */
            background: rgba(255,255,255,0.0);
        }

        .HanhzihCell {
            font-size: 6em;
            font-family: '华文中宋';
            color:rgb(0,0,0);
            text-shadow: 0.05em 0.05em 0.1em #aaa;
        }

        .PhrengqimCell {
            font-size: 4em;
            font-family: 'Times New Roman', Times, serif;
            color: rgb(0,0,0);
            /* -webkit-text-stroke: 1px #000; */
            padding: 10px;
            text-shadow: 0.05em 0.05em 0.1em #aaa;
        }
        """
    body = E.BODY(
        #  E.H1(E.CLASS("heading"), "Top News"),
        #  E.P("World News only on this page", style="font-size: 200%"),
        #  "Ah, and here's some more text, by the way.",
        root,
        css
    )
    if extra_css:
        css_extra = E.STYLE(type='text/css')
        css_extra.text = extra_css
        body.append(css_extra)

    html = E.HTML(
    E.HEAD(
        #  E.LINK(rel="stylesheet", href="great.css", type="text/css"),
        #  E.TITLE("Best Page Ever")
        E.META(charset='utf-8')
    ),
    body,
    )
    
    return html

__global_config = {
    'width':1500,
    'height':500,
    'timebase':30,
}


__imgkit_config = {
    'transparent':None,
    'format':'png',
    'quality':100,
    'width':__global_config['width'],
    'height':__global_config['height']
}


def generate_line_img(cont_cn, cont_latin, out_file, extra_css=None):
    html = generate_line_html(cont_cn, cont_latin, extra_css)
    s = etree.tostring(html, encoding='utf-8')
    s = str(s,'utf-8')
    # print(s)
    with etree.htmlfile(out_file+'_test.html', encoding='utf-8') as fp:
        fp.write_doctype('<!DOCTYPE HTML>')
        fp.write(html)

    imgkit.from_string(s, out_file, options=__imgkit_config)


def __common_item_rate():
    item = etree.Element('rate')
    item.append(etree.fromstring('<ntsc>FALSE</ntsc>'))
    etree.SubElement(item, 'timebase').text = str(__global_config['timebase'])
    return item


def __common_item_format():
    fmt = etree.Element('format')
    scc = etree.SubElement(fmt, 'samplecharacteristics')
    scc.append(__common_item_rate())
    etree.SubElement(scc, 'width').text = str(__global_config['width'])
    etree.SubElement(scc, 'height').text = str(__global_config['height'])
    scc.append(etree.fromstring('<pixelaspectratio>Square</pixelaspectratio>'))
    scc.append(etree.fromstring('<anamorphic>FALSE</anamorphic>'))
    return fmt


def generate_clip_item(imgname,cont_cn, imgfullname, timebase, 
    tm_start, tm_end):
    item = etree.Element('clipitem', {'id': imgname})
    item.append(etree.Comment(cont_cn.replace('-','_')))
    etree.SubElement(item, 'name').text = imgname
    etree.SubElement(item, 'duration').text = '3251'
    rate = etree.SubElement(item,'rate')
    etree.SubElement(rate, 'ntsc').text='FALSE'
    etree.SubElement(rate,'timebase').text=str(timebase)

    etree.SubElement(item,'in').text=str(sec_to_timestamp(tm_start, timebase))
    etree.SubElement(item,'out').text=str(sec_to_timestamp(tm_end, timebase))
    etree.SubElement(item,'start').text=str(sec_to_timestamp(tm_start, timebase))
    etree.SubElement(item,'end').text=str(sec_to_timestamp(tm_end, timebase))
    
    item.append(etree.fromstring('<pixelaspectratio>Square</pixelaspectratio>'))
    item.append(etree.fromstring('<stillframe>TRUE</stillframe>'))
    item.append(etree.fromstring('<anamorphic>FALSE</anamorphic>'))
    item.append(etree.fromstring('<alphatype>straight</alphatype>'))

    etree.SubElement(item, 'masterclipid').text = imgname+'1'
    efile = etree.SubElement(item,'file',{'id':imgname})
    etree.SubElement(efile, 'name').text = imgname
    etree.SubElement(efile, 'pathurl').text = imgfullname
    efile.append(copy.deepcopy(rate))
    etree.SubElement(efile,'duration').text = '2'  # 不知道这是啥
    etree.SubElement(efile, 'width').text = str(__global_config['width'])
    etree.SubElement(efile, 'height').text = str(__global_config['height'])
    med = etree.SubElement(efile, 'media')

    ved = etree.SubElement(med, 'video')
    etree.SubElement(ved, 'duration').text = '2'
    ved.append(etree.fromstring('<stillframe>TRUE</stillframe>'))
    ved.append(__common_item_format())

    item.append(etree.fromstring('<sourcetrack><mediatype>video</mediatype></sourcetrack>'))
    item.append(etree.fromstring('<fielddominance>none</fielddominance>'))
    return item


def proc_item(cont_cn, cont_latin, tm_start, tm_end, n, output_root, trk, extra_css):
    print(n, cont_cn, cont_latin)

    img_name = f'img{n:03d}.png'
    img_fullname = f'{os.path.abspath(output_root)}/{img_name}'
    generate_line_img(cont_cn,cont_latin.lower(),img_fullname,extra_css)

    item = generate_clip_item(img_name, cont_cn, img_fullname,
        __global_config['timebase'],tm_start, tm_end)
    trk.append(item)


def main(cn_file, latin_file, output_root, extra_css_file):
    if not os.path.exists(output_root):
        os.mkdir(output_root)

    etree.Comment('本序列文件由ngixqlrc生成')
    etree.Comment('https://github.com/CDK6182CHR/ngixqlrc')

    # prepare xml header ...
    xeml = etree.Element('xmeml',{'version':'5'})
    seq = etree.SubElement(xeml, 'sequence', {'id':'XML字幕序列'})
    seq.append(etree.fromstring('<updatebehavior>add</updatebehavior>'))
    seq.append(etree.fromstring('<name>XML字幕序列</name>'))
    rate = etree.SubElement(seq, 'rate')
    etree.SubElement(rate, 'ntsc').text = 'FALSE'
    etree.SubElement(rate, 'timebase').text = str(__global_config['timebase'])

    tc = etree.SubElement(seq, 'timecode')
    tc.append(copy.deepcopy(rate))
    tc.append(etree.fromstring('<string>00:00:00:00</string>'))
    tc.append(etree.fromstring('<frame>0</frame>'))
    tc.append(etree.fromstring('<source>source</source>'))
    tc.append(etree.fromstring('<displayformat>NDF</displayformat>'))
    etree.SubElement(seq, 'width').text = str(__global_config['width'])
    etree.SubElement(seq, 'height').text = str(__global_config['height'])
    # in, out, duration, 最后来填
    med = etree.SubElement(seq,'media')
    vid = etree.SubElement(med, 'video')
    vid.append(__common_item_format())
    vid.append(etree.fromstring("""
    <track>
          <enabled>TRUE</enabled>
          <locked>FALSE</locked>
        </track>
    """
    ))
    trk = etree.SubElement(vid,'track')
    
    fp1 = open(latin_file, 'r', encoding='utf-8', errors='ignore')
    fp2 = open(cn_file, 'r', encoding='utf-8', errors='ignore')

    if extra_css_file:
        with open(extra_css_file, encoding='utf-8', errors='ignore') as fp:
            extra_css = fp.read()
    else:
        extra_css = None


    fp1_last, fp2_last = '',''
    tmmark_last = ''
    n = 0
    for (line1,line2) in zip(fp1,fp2):
        line1 = line1.strip()
        line2 = line2.strip()
        if tmmark_r:=re.search(__tmmark_reg, line1):
            line1 = line1.lstrip(tmmark_r.group())
        if tmmark_r:=re.search(__tmmark_reg, line2):
            tmmark = tmmark_r.groups()[0]
            line2 = line2.lstrip(tmmark_r.group())
        if not line1 or not line2:
            pass    # 2024.05.28: just process empty line as normal one?
            # fp1_last, fp2_last = line1, line2
            # tmmark_last = tmmark
            # continue
        if tmmark_last:
            proc_item(fp2_last, fp1_last, lrc_time_to_secs(tmmark_last), 
            lrc_time_to_secs(tmmark), n, output_root, trk, extra_css)
            n += 1

        fp1_last, fp2_last = line1, line2
        tmmark_last = tmmark
    if fp1_last:
        proc_item(fp2_last, fp1_last, lrc_time_to_secs(tmmark_last), 
            lrc_time_to_secs(tmmark_last)+10, n, output_root, trk, extra_css)
    secs_max = lrc_time_to_secs(tmmark_last)+10
        
    fp1.close()
    fp2.close()

    # finialize ..
    etree.SubElement(seq,'duration').text=str(
        sec_to_timestamp(secs_max, __global_config['timebase'])+1)
    etree.SubElement(seq, 'in').text = '0'
    etree.SubElement(seq,'out').text=str(
        sec_to_timestamp(secs_max, __global_config['timebase'])+1)
    seq.append(etree.fromstring('<ismasterclip>FALSE</ismasterclip>'))

    with etree.xmlfile(f'{output_root}/subtitle.xml',encoding='utf-8') as fp:
        fp.write_declaration()
        fp.write_doctype('<!DOCTYPE xmeml>')
        fp.write(xeml, pretty_print=True)


if __name__ == '__main__':
    ...
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='根据歌词文件生成标音的Premiere序列')
    parser.add_argument('triungkox', help='注音文件，lrc或txt')
    parser.add_argument('ghenhdaih', help='汉字歌词文件，lrc或txt')
    parser.add_argument('output_root', help='输出的文件夹名')
    parser.add_argument('--width', dest='width', type=int, 
            default=1500, required=False, help='输出图幅宽度')
    parser.add_argument('--height',  dest='height', type=int, 
            default=500, required=False, help='输出图幅高度')
    parser.add_argument('--timebase', dest='timebase', type=int, 
            default=30, required=False, help='输出序列的帧速率 fps')
    parser.add_argument('--use-md', '-m', action='store_true', dest='use_md', help='是否使用markdown解析注音文本')
    parser.add_argument('--capital-red', '-r',  action='store_true', dest='capital_red', 
            help='是否将注音中的大写字母转换为红色文本')
    parser.add_argument('--center', '-c', action='store_true', help='表格是否居中')
    parser.add_argument('--extra-css-file', '-e', type=str, default=None,
                        help="额外引入的css样式表文件，插入到每一页面的最后")

    p = parser.parse_args(sys.argv[1:])

    __global_config['height'] = __imgkit_config['height'] = p.height
    __global_config['width'] = __imgkit_config['width'] = p.width
    __global_config['timebase'] = p.timebase

    print(__global_config)

    parse_config(p)

    main(p.ghenhdaih, p.triungkox, p.output_root, p.extra_css_file)
