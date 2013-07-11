# coding=UTF-8
import unicodedata

def unicode_to_sane_ascii(txt):
    return unicodedata.normalize('NFD', unicode(txt)).encode('ascii', 'ignore')

