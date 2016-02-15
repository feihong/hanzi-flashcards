import os.path as op
import sys
import gzip
import re
from collections import namedtuple


DICTIONARY_URL = 'http://www.mdbg.net/chindict/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz'

DictItem = namedtuple('DictItem', ['traditional', 'simplified', 'pinyin', 'gloss'])


def download_dict():
    import requests
    if not op.exists('dict.txt.gz'):
        response = requests.get(DICTIONARY_URL)
        with open('dict.txt.gz', 'wb') as fp:
            fp.write(response.content)


def get_dict_items():
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
                    yield DictItem(*match.groups())


def write_flashcards(items):
    with open('flashcards.txt', 'w') as fp:
        for count, item in enumerate(get_dict_items()):
            line = '%s, %s\t%s\t' % (item.pinyin, item.gloss, item.pinyin)
            if item.simplified == item.traditional:
                line += '%s, %s' % (item.simplified, item.traditional)
            else:
                line += '%s' % item.simplified
            print(line)
            fp.write(line + '\n')

    print('\nWrote %d entries to flashcards.txt' % count)

if __name__ == '__main__':
    download_dict()
    write_flashcards(get_dict_items())
