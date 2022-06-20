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

    tr = etree.SubElement(table, 'tr')
    prengqim = line_latin.split()
    for t in prengqim:
        if html_config['capital_red']:
            if caps:=re.findall(cap_reg, t):
                for i in caps:
                    t=t.replace(i, f'<font color="red">{i.lower()}</font>')
        if html_config['use_md']:
            t = markdown.markdown(t, extensions=[SuperscriptExtension()])
        # td = etree.SubElement(tr, 'td', E.CLASS('PhrengqimCell'), align='center')
        td = etree.fromstring(f'<td class="PhrengqimCell">{t}</td>')
        td.attrib['align'] = 'center'
        tr.append(td)
    
    # 汉字行：逐字，但忽略空格
    tr = etree.SubElement(table, 'tr')
    for t in line_cn:
        t:str
        if not t.isspace() and t!='|':
            td = etree.SubElement(tr, 'td', E.CLASS('HanhzihCell'), align='center')
            td.text = t
    return table



