"""
2024.06.02  Simple CUI program that shift the given LRC file by specified seconds.
"""
from .common import parse_lrc_line, format_lrc_line


def lrc_shift(input_file, output_file, seconds, is_advance):
    dt = -seconds if is_advance else seconds

    fpout = open(output_file, 'w', encoding='utf-8', errors='ignore')
    fpin = open(input_file, encoding='utf-8', errors='ignore')

    for line in fpin:
        tmmark, content = parse_lrc_line(line)
        if tmmark is not None:
            line_shift = format_lrc_line(tmmark + dt, content)
        else:
            line_shift = content
        fpout.write(line_shift)
    fpin.close()
    fpout.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str)
    parser.add_argument('--output-file', '-o', default=None, type=str)
    parser.add_argument('--seconds', type=float, default=0.0)
    parser.add_argument('--advance', '-a', action='store_true')
    parser.add_argument('--delay', '-d', action='store_const', dest='advance', const=False)

    p = parser.parse_args()
    print(p)

    out_file = p.output_file
    if out_file is None:
        out_file = f'{p.input_file}_shift.lrc'
    lrc_shift(p.input_file, out_file, p.seconds, p.advance)
    

