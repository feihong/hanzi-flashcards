import os.path as op
import sys
import gzip
import re
from collections import namedtuple, Counter
from pathlib import Path


DICTIONARY_URL = 'http://www.mdbg.net/chindict/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz'

FLASHCARD_HANZI_MAX = 3500

IGNORED_CHARACTERS = ['：', '”', '“', '\u3000', '一', '。', '，', '！', '、', '…']

DictItem = namedtuple('DictItem', ['traditional', 'simplified', 'pinyin', 'gloss'])



def download_dict():
    import requests
    if not op.exists('dict.txt.gz'):
        response = requests.get(DICTIONARY_URL)
        with open('dict.txt.gz', 'wb') as fp:
            fp.write(response.content)


def get_dict_items(filter_by):
    """
    Return a sequence of single-hanzi dictionary items.

    """
    with gzip.open('dict.txt.gz', mode='rt', encoding='utf-8') as fp:
        for line in fp:
            if not '[' in line:
                continue
            hanzi = line.split(' [', 1)[0]
            if len(hanzi) == 3:
                match = re.match(r'(\w) (\w) \[(.*)\] \/(.*)\/', line)
                if match:
                    item = DictItem(*match.groups())
                    if filter_by(item):
                        yield item


def write_flashcards(items):
    with open('flashcards.txt', 'w') as fp:
        fp.write('\ufeff')      # Write BOM
        # fp.write('//Hanzi Preload\n')
        for i, item in enumerate(items):
            line = '%s, %s\t' % (
                decode_pinyin(item.pinyin), item.gloss)
            if item.simplified == item.traditional:
                line += '%s' % item.simplified
            else:
                line += '%s, %s' % (item.traditional, item.simplified)
            print(i, repr(line))
            fp.write(line + '\n')

    print('\nWrote %d entries to flashcards.txt' % i)


def get_corpus_chars():
    corpus = Path('corpus')
    for txtfile in corpus.glob('*.txt'):
        print('Opening', txtfile)
        with txtfile.open() as fp:
            while True:
                c = fp.read(1)
                if c == '':
                    break
                if ord(c) > 256 and c not in IGNORED_CHARACTERS:
                    yield c


def write_hanzi_frequency():
    counter = Counter()
    for c in get_corpus_chars():
        counter[c] += 1

    items = counter.most_common()
    with open('hanzi_frequency.txt', 'w') as fp:
        for i, item in enumerate(items, 1):
            hanzi, count = item
            fp.write('%d. %s %s\n' % (i, hanzi, count))

    print('\nWrote %d lines to hanzi_frequency.txt' % i)


def get_most_frequent_hanzi():
    counter = Counter()
    for c in get_corpus_chars():
        counter[c] += 1

    return dict(counter.most_common(FLASHCARD_HANZI_MAX))


# Source: http://stackoverflow.com/questions/8200349/convert-numbered-pinyin-to-pinyin-with-tone-marks/8200388#8200388
PinyinToneMark = {
    0: "aoeiuv\u00fc",
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
}

def decode_pinyin(s):
    s = s.lower()
    r = ""
    t = ""
    for c in s:
        if c >= 'a' and c <= 'z':
            t += c
        elif c == ':':
            assert t[-1] == 'u'
            t = t[:-1] + "\u00fc"
        else:
            if c >= '0' and c <= '5':
                tone = int(c) % 5
                if tone != 0:
                    m = re.search("[aoeiuv\u00fc]+", t)
                    if m is None:
                        t += c
                    elif len(m.group(0)) == 1:
                        t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                    else:
                        if 'a' in t:
                            t = t.replace("a", PinyinToneMark[tone][0])
                        elif 'o' in t:
                            t = t.replace("o", PinyinToneMark[tone][1])
                        elif 'e' in t:
                            t = t.replace("e", PinyinToneMark[tone][2])
                        elif t.endswith("ui"):
                            t = t.replace("i", PinyinToneMark[tone][3])
                        elif t.endswith("iu"):
                            t = t.replace("u", PinyinToneMark[tone][4])
                        else:
                            t += "!"
            r += t
            t = ""
    r += t
    return r


if __name__ == '__main__':
    download_dict()

    # write_hanzi_frequency()

    hanzi_dict = get_most_frequent_hanzi()
    dict_items = get_dict_items(lambda x: x.simplified in hanzi_dict)
    dict_items = list(dict_items)
    dict_items.sort(key=lambda x: -hanzi_dict[x.simplified])
    write_flashcards(dict_items)
