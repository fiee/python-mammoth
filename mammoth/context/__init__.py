# coding=utf-8
"""
ConTeXt format tools
2015-2018 by fiëé visuëlle, www.fiee.net
ConTeXt is a TeX format, see www.contextgarden.net
"""
from __future__ import unicode_literals
from __future__ import absolute_import
import re
from .footnotes import fix_footnotes

__all__ = ['remove_empty_links', 'fix_footnotes', 'fix_quotes', 'fix_spaces', 'remove_empty_elements']


reSpacerun = re.compile(r'[ \t]+')
reEmptyElement = re.compile(r'\\emph\{\}')
reEmptyLink = re.compile('\\\goto\[id=.*?\]\{\}', flags=re.U|re.I)


def fix_spaces(context):
    """
    Replace multiple spaces by one (just for the beauty)
    """
    for m in reSpacerun.finditer(context):
        context = context.replace(m.group(0), ' ')
    context = context.replace(' }', '} ')
    context = context.replace('\n\n\n', '\n\n')
    return context


def remove_empty_links(context):
    """
    remove empty links like
    \goto[id=_Hlk502424747]{}

    Some come from DDE or Fieldmarks
    """
    for m in reEmptyLink.finditer(context):
        context = context.replace(m.group(0), '')
    return context


def remove_empty_elements(context):
    """
    Remove obsolete \emph{}
    """
    context = fix_spaces(context)
    context = remove_empty_links(context)
    for m in reEmptyElement.finditer(context):
        context = context.replace(m.group(0), ' ')
    return context


QUOTEMAP = {
    'en' : '“”‘’',
    'de' : '„“‚‘',
    'de_fr': '»«›‹',
    'fr': '«»‹›'
}


def fix_quotes(context, lang='en'):
    """
    Convert quote signs into logical quotations.
    Also helps to find missing quotation marks.
    """
    Quotes = QUOTEMAP[lang]
    reDoubleQuote = re.compile(Quotes[0] + '(.*?)' + Quotes[1], re.I|re.U)
    reSingleQuote = re.compile(Quotes[2] + '(.*?)' + Quotes[3], re.I|re.U)
    for m in reDoubleQuote.finditer(context):
        context = context.replace(m.group(0), '\\quotation{%s}' % m.group(1))
    for m in reSingleQuote.finditer(context):
        context = context.replace(m.group(0), '\\quote{%s}' % m.group(1))
    return context
