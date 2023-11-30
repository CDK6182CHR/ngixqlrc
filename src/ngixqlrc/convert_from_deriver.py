"""
2023.11.28  convert from qieyun-autoderiver  https://nk2028.shn.hk/qieyun-autoderiver/
simply regex operation with some extra processing.
"""
import re 

_regex_symbols = re.compile(r'\((.*?)\)')

def convert_from_deriver(src:str, dst:str):
    fout = open(dst, 'w', encoding='utf-8', errors='ignore')
    fin = open(src, encoding='utf-8', errors='ignore')

    for line in fin:
        symbols = re.findall(_regex_symbols, line)
        fout.write(f"{' '.join(symbols)}\n")

    fin.close()
    fout.close()


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('src')
    parser.add_argument('dst')

    p = parser.parse_args()
    convert_from_deriver(p.src, p.dst)