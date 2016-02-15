import os.path as op
import sys
import gzip
import re
from collections import namedtuple, Counter
from pathlib import Path


DICTIONARY_URL = 'http://www.mdbg.net/chindict/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz'

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
        for count, item in enumerate(items):
            line = '%s, %s\t%s\t' % (item.pinyin, item.gloss, item.pinyin)
            if item.simplified == item.traditional:
                line += '%s, %s' % (item.simplified, item.traditional)
            else:
                line += '%s' % item.simplified
            print(line)
            fp.write(line + '\n')

    print('\nWrote %d entries to flashcards.txt' % count)


def get_corpus_chars():
    corpus = Path('corpus')
    for txtfile in corpus.glob('*.txt'):
        print(txtfile)
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
            fp.write('%d. %s %s\n' % (i, item[0], item[1]))


if __name__ == '__main__':
    download_dict()
    # write_flashcards(get_dict_items(lambda x: True))

    write_hanzi_frequency()
