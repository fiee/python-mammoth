# coding=utf-8
"""
ConTeXt format writer
2015-2018 by fiëé visuëlle, www.fiee.net
ConTeXt is a TeX format, see www.contextgarden.net
"""
from __future__ import unicode_literals
from .abc import Writer
import re
import base64
import logging
logger = logging.getLogger()

# mapping of HTML tags to ConTeXt
CTXMAP = {
    'p' : ('\\startparagraph\n', '\n\\stopparagraph\n\n'),
    'pre' : ('\\startlines\n', '\n\\stoplines\n\n'),
    'b' : ('{\\bf ', '}'),
    'i' : ('\\emph{', '}'),
    'strong' : ('{\\bf ', '}'),
    'em' : ('\\emph{', '}'),
    'u' : ('\\underbar{', '}'),
    'sup' : ('\\high{', '}'),
    'sub' : ('\\low{', '}'),
    'table' : ('\\bTABLE ', '\\eTABLE\n'),
    'tr' : ('\\bTR', '\\eTR\n'),
    'td' : ('\\bTD', '\\eTD'),
    'ol' : ('\\startitemize[1]\n', '\\stopitemize\n'),
    'ul' : ('\\startitemize[n]\n', '\\stopitemize\n'),
    'li' : ('\\startitem\n', '\n\\stopitem\n'),
    'a' : ('\\goto{', '}'),
    'footnote' : ('\\footnote{','}'),
    'br' : ('\\crlf ',''),
    'h1' : ('\\startchapter[]\n', '\n\\stopchapter\n\n'),
    'h2' : ('\\startsection[]\n', '\n\\stopsection\n\n'),
    'h3' : ('\\startsubsection[]\n', '\n\\stopsubsection\n\n'),
    'h4' : ('\\startsubsubsection[]\n', '\n\\stopsubsubsection\n\n'),
    'img': ('%% \\imgdata', ''),
    'span': ('{', '}'),
}

LANG = 'en'

QUOTEMAP = {
    'en' : '“”‘’',
    'de' : '„“̦‘',
}
QUOTES = QUOTEMAP[LANG]
reDOUBLEQUOTE = re.compile(QUOTES[0] + '([\w\s]+)' + QUOTES[1], re.I|re.U)
reSINGLEQUOTE = re.compile(QUOTES[2] + '([\w\s]+)' + QUOTES[3], re.I|re.U)


class ConTeXtWriter(Writer):
    image_counter = 0

    def __init__(self):
        self._fragments = []

    def text(self, text):
        self._fragments.append(_escape_context(text))

    def start(self, name, attributes=None):
        attribute_string = _generate_attribute_string(attributes)
        if (name == 'a') and ('id' in attributes) and (('footnote-ref' in attributes['id']) or ('endnote-ref' in attributes['id'])):
            name = 'footnote'
        if name in CTXMAP:
            name = CTXMAP[name][0]
        else:
            logger.warn('<%s is not in CTXMAP!' % name)
        if name.endswith('{') and attribute_string:
            name = name[0:len(name)-1]
            attribute_string += '{'
        self._fragments.append("{0}{1}".format(name, attribute_string))

    def end(self, name):
        if name in CTXMAP:
            name = CTXMAP[name][1]
        else:
            logger.warn('%s> is not in CTXMAP!' % name)
        self._fragments.append(name)

    def self_closing(self, name, attributes=None):
        attribute_string = _generate_attribute_string(attributes)
        if name in CTXMAP:
            self._fragments.append("{0}{1}{2}".format(CTXMAP[name][0], attribute_string, CTXMAP[name][1]))
        else:
            logger.warn('<%s> is not in CTXMAP!' % name)
            self._fragments.append("\\%s{%s}" % (name, attribute_string))

    def append(self, html):
        self._fragments.append(html)

    def as_string(self):
        return "".join(self._fragments)

def _escape_context(text):
    for c in '\\{}$&%|':
        text = text.replace(c, '\\'+c)
    text = text.replace(' ', ' ')
    text = text.replace('--', '–') # always?
    for m in reSINGLEQUOTE.finditer(text):
        text = text.replace(m.group(0), r'\quote{' + m.group(1) + '}')
    for m in reDOUBLEQUOTE.finditer(text):
        text = text.replace(m.group(0), r'\quotation{' + m.group(1) + '}')
    for m in re.finditer(r'\s+"(.*?)"\s+', text, re.U|re.M):
        text = text.replace(m.group(0), r' \quotation{' + m.group(1) + '} ')
    for m in re.finditer(r'‘(.*?)’', text, re.U|re.M):
        text = text.replace(m.group(0), r'\quote{' + m.group(1) + '}')
    return text


def _generate_attribute_string(attributes):
    if not attributes:
        return ""
    else:
        return "[" + ",".join(
            '{0}={1}'.format(key, _escape_context(attributes[key]))
            for key in sorted(attributes)
        ) + "]"
