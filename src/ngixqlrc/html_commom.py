from lxml import etree
from lxml.html import builder as E
import re 
import markdown
from mdx_superscript import SuperscriptExtension


html_config = {
    'capital_red': True,
    'use_md': False,
    'center': False,
}

def parse_config(p):
    html_config['capital_red'] = bool(p.capital_red)
    html_config['use_md'] = bool(p.use_md)
    html_config['center'] = p.center


cap_reg = re.compile(r'[A-Z]{1,}')


def generate_html_table(line_cn, line_latin):
    """
    本函数处理单行的。
    合并生成html页面和字幕的两种处理环境。
    """
    table = etree.Element('table',E.CLASS('LyricTable'))
    if html_config['center']:
        table.attrib['align'] = 'center'

    trp = etree.SubElement(table, 'tr')
    trc = etree.SubElement(table, 'tr')
    prengqim = line_latin.split()
    # for t in prengqim:
    #     if html_config['capital_red']:
    #         if caps:=re.findall(cap_reg, t):
    #             for i in caps:
    #                 t=t.replace(i, f'<font color="red">{i.lower()}</font>')
    #     if html_config['use_md']:
    #         t = markdown.markdown(t, extensions=[SuperscriptExtension()])
    #     # td = etree.SubElement(tr, 'td', E.CLASS('PhrengqimCell'), align='center')
    #     td = etree.fromstring(f'<td class="PhrengqimCell">{t}</td>')
    #     td.attrib['align'] = 'center'
    #     tr.append(td)
    
    # # 汉字行：逐字，但忽略空格
    # trc = etree.SubElement(table, 'tr')
    # for t in line_cn:
    #     t:str
    #     # 2023.11.30: 仅考虑文本字符，忽略标点
    #     if not t.isspace() and t!='|':
    #         td = etree.SubElement(tr, 'td', E.CLASS('HanhzihCell'), align='center')
    #         td.text = t

    # 2023.11.30: 共同循环，保留汉字行中的非文字成分
    num = max(len(prengqim), len(line_cn))
    # print(prengqim, line_cn)
    ic = 0
    ip = 0
    break_later = False
    while ip < len(prengqim) or ic < len(line_cn):
        tp = prengqim[ip] if ip < len(prengqim) else ''
        tc = line_cn[ic] if ic < len(line_cn) else ''

        # first, check the Chinese char
        if not tc.isspace() and tc!='|':
            tdc = etree.SubElement(trc, 'td', E.CLASS('HanhzihCell'), align='center')
            tdc.text = tc

            # 2023.11.30  experimental: 对标点符号，直接跳过注音行
            if not tc.isalnum():
                ip -= 1
                tp = ''
                # 2024.06.12: 对行尾标点，结束本字处理后直接break，避免死循环
                if ic == len(line_cn) - 1:
                    break_later = True
        else:
            ic += 1
            continue

        # now, for Latin word
        if html_config['capital_red']:
            if caps:=re.findall(cap_reg, tp):
                for i in caps:
                    tp=tp.replace(i, f'<font color="red">{i.lower()}</font>')
        if html_config['use_md']:
            tp = markdown.markdown(tp, extensions=[SuperscriptExtension()])
        # td = etree.SubElement(tr, 'td', E.CLASS('PhrengqimCell'), align='center')
        tdp = etree.fromstring(f'<td class="PhrengqimCell">{tp}</td>')
        tdp.attrib['align'] = 'center'
        trp.append(tdp)
        ic += 1
        ip += 1
        if break_later:
            break


    return table



