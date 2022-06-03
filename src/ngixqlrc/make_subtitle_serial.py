import imgkit
from lxml import etree
from lxml.html import builder as E
import re
import os
import copy


__tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')


def lrc_time_to_secs(mark:str)->float:
    """
    lrc的时间戳转换为秒数。入参不含方括号。
    """
    sp1 = mark.split(':')
    res = int(sp1[0])*60
    res += float(sp1[1])
    return res


def sec_to_timestamp(sec:float, timebase:int)->int:
    """
    秒数转时间戳。
    """
    return int(round(sec/(1.0/timebase)))


def generate_line_elements(line_cn, line_latin):
    """
    returns the table element
    """
    table = etree.Element('table',E.CLASS('LyricTable'))

    tr = etree.SubElement(table, 'tr')
    prengqim = line_latin.split()
    for t in prengqim:
        # td = etree.SubElement(tr, 'td', E.CLASS('PhrengqimCell'), align='center')
        td = etree.fromstring(f'<td class="PhrengqimCell">{t}</td>')
        td.attrib['align'] = 'center'
        tr.append(td)
    
    # 汉字行：逐字，但忽略空格
    tr = etree.SubElement(table, 'tr')
    for t in line_cn:
        t:str
        if not t.isspace():
            td = etree.SubElement(tr, 'td', E.CLASS('HanhzihCell'), align='center')
            td.text = t
    return table


def generate_line_html(cont_cn, cont_latin):
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
        table = generate_line_elements(cn_line,lt_line)
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
            font-size: 4em;
            font-family: '华文中宋';
            color:rgb(0,0,0);
            /* -webkit-text-stroke: 2px #000; */
        }

        .PhrengqimCell {
            font-size: 2.5em;
            font-family: 'Times New Roman', Times, serif;
            color: rgb(0,0,0);
            /* -webkit-text-stroke: 1px #000; */
            padding: 5px;
        }
        """

    html = E.HTML(
    E.HEAD(
        #  E.LINK(rel="stylesheet", href="great.css", type="text/css"),
        #  E.TITLE("Best Page Ever")
        E.META(charset='utf-8')
    ),
    E.BODY(
        #  E.H1(E.CLASS("heading"), "Top News"),
        #  E.P("World News only on this page", style="font-size: 200%"),
        #  "Ah, and here's some more text, by the way.",
        root,
        css
    )
    )
    
    return html


__imgkit_config = {
    'transparent':None,
    'format':'png',
    'quality':100,
    'width':1500,
    'height':500
}

__global_config = {
    'width':1500,
    'height':1000,
    'timebase':30,
}


def generate_line_img(cont_cn, cont_latin, out_file):
    html = generate_line_html(cont_cn, cont_latin)
    s = etree.tostring(html, encoding='utf-8')
    s = str(s,'utf-8')
    # print(s)
    # with etree.htmlfile(out_file+'_test.html', encoding='utf-8') as fp:
    #     fp.write_doctype('<!DOCTYPE HTML>')
    #     fp.write(html)

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
    item.append(etree.Comment(cont_cn))
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


"""

"""


def proc_item(cont_cn, cont_latin, tm_start, tm_end, n, output_root, trk):
    print(n, cont_cn, cont_latin)

    img_name = f'img{n:03d}.png'
    img_fullname = f'{os.path.abspath(output_root)}/{img_name}'
    generate_line_img(cont_cn,cont_latin.lower(),img_fullname)

    item = generate_clip_item(img_name, cont_cn, img_fullname,
        __global_config['timebase'],tm_start, tm_end)
    trk.append(item)


def main(cn_file, latin_file, output_root):

    # prepare xml header ...
    xeml = etree.Element('xmeml',{'version':'5'})
    seq = etree.SubElement(xeml, 'sequence', {'id':'XML字幕序列'})
    seq.append(etree.fromstring('<updatebehavior>add</updatebehavior>'))
    seq.append(etree.fromstring('<name>XML字幕序列_25.0p_Subtitle</name>'))
    rate = etree.SubElement(seq, 'rate')
    etree.SubElement(rate, 'ntsc').text = 'FALSE'
    etree.SubElement(rate, 'timebase').text = str(__global_config['timebase'])

    tc = etree.SubElement(seq, 'timecode')
    tc.append(copy.deepcopy(rate))
    tc.append(etree.fromstring('<string>01:00:00:00</string>'))
    tc.append(etree.fromstring('  <frame>90000</frame>'))
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
            fp1_last, fp2_last = line1, line2
            tmmark_last = tmmark
            continue
        if tmmark_last:
            proc_item(fp2_last, fp1_last, lrc_time_to_secs(tmmark_last), 
            lrc_time_to_secs(tmmark), n, output_root, trk)
            n += 1

        fp1_last, fp2_last = line1, line2
        tmmark_last = tmmark
    if fp1_last:
        proc_item(fp2_last, fp1_last, lrc_time_to_secs(tmmark_last), 
            lrc_time_to_secs(tmmark_last)+10, n, output_root, trk)
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
    # generate_line_img(
    #     '又一三月|浓愁共清风盈袖',
    #     'iuh qjit sam ngyat nryung zriu gyungh chieng piung jeng zsiuh',
    #     'img/1.png'
    # )
    # generate_line_img(
    #     '未觉经身处腐草生芳华瘦',
    #     'myoih kruk keng sjin chjoh Byox chaux srang phyang ghrua sriuh'.lower(),
    #     'img/2.png'
    # )
    main('汉字-对照版.lrc','中古-对照版.txt','serial_out')
