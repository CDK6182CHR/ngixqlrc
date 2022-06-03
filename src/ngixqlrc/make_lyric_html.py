"""
2022年3月6日
此程序依据汉语拼音和中古音一一对应的歌词文件，生成HTML文档。
可用LRC作为输入，前面的时间戳直接丢掉。
"""
import lxml
from lxml import etree
from lxml.html import builder as E
import re



def lyric_html(triungkox, ghenhdaih, outfile, outlower):
    """
    2022.06.03修订：中文歌词中把竖线抹了
    """

    root = etree.Element('p')

    fp1 = open(triungkox, 'r', encoding='utf-8', errors='ignore')
    fp2 = open(ghenhdaih, 'r', encoding='utf-8', errors='ignore')

    tmmark_reg = re.compile(r'^\[([0-9:.]{1,})\]')
    cap_reg = re.compile(r'[A-Z]{1,}')

    # while fp1 and fp2:
    #     line1 = fp1.readline().strip()
    #     line2 = fp2.readline().strip()
    for (line1,line2) in zip(fp1,fp2):
        line1 = line1.strip()
        line2 = line2.strip()
        if tmmark_r:=re.search(tmmark_reg, line1):
            line1 = line1.lstrip(tmmark_r.group())
        if tmmark_r:=re.search(tmmark_reg, line2):
            line2 = line2.lstrip(tmmark_r.group())
        if not line1 or not line2:
            continue
        print(line1, line2)
        # 中古拼音行：按空格分划
        table = etree.SubElement(root, 'table', E.CLASS('LyricTable'))
        tr = etree.SubElement(table, 'tr')
        prengqim = line1.split()
        for t in prengqim:
            if caps:=re.findall(cap_reg, t):
                for i in caps:
                    t=t.replace(i, f'<font color="red">{i.lower()}</font>')
            # td = etree.SubElement(tr, 'td', E.CLASS('PhrengqimCell'), align='center')
            td = etree.fromstring(f'<td class="PhrengqimCell">{t}</td>')
            td.attrib['align'] = 'center'
            tr.append(td)
        # 汉字行：逐字，但忽略空格
        tr = etree.SubElement(table, 'tr')
        for t in line2:
            t:str
            if not t.isspace() and t != '|':
                td = etree.SubElement(tr, 'td', E.CLASS('HanhzihCell'), align='center')
                td.text = t
        etree.SubElement(root, 'p')
    fp1.close()
    fp2.close()

    css = E.STYLE(type='text/css')
    css.text = """
        .LyricTable{
            border-style: double;
        }
        .HanhzihCell{
            font-size: 1.5em;
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

    with etree.htmlfile(outfile, encoding='utf-8') as xf:
        xf.write_doctype('<!DOCTYPE HTML>')

        xf.write(html)


    # 2022.05.31: also add lower-case version
    if outlower:
        with open(triungkox, encoding='utf-8', errors='ignore') as fp:
            with open(outlower, 'w', encoding='utf-8', errors='ignore') as fout:
                fout.write(fp.read().lower())


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='将拼音注音和汉字歌词转换为html的一一对应格式')
    parser.add_argument('triungkox', nargs=1, help='注音文件，lrc或txt')
    parser.add_argument('ghenhdaih', nargs=1, help='汉字歌词文件，lrc或txt')
    parser.add_argument('outfile', nargs=1, help='输出的html文件')
    parser.add_argument('lower', nargs='?', default=None, 
        help='（可选）输出的纯小写注音文件，如不指定则不生成')

    p = parser.parse_args(sys.argv[1:])

    triungkox = p.triungkox[0]
    ghenhdaih = p.ghenhdaih[0]
    outfile = p.outfile[0]
    outlower = p.lower[0] if p.lower is not None else None

    lyric_html(triungkox, ghenhdaih, outfile, outlower)    


