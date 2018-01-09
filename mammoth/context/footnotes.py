# coding=utf-8
"""
ConTeXt format tools: Footnotes
2015-2018 by fiëé visuëlle, www.fiee.net
ConTeXt is a TeX format, see www.contextgarden.net
"""
from __future__ import unicode_literals
import re
import logging
logger = logging.getLogger()


# [class=fnr]{\high{\footnote[href=#footnote-5,id=footnote-ref-5]{[4]}}}
reFNref = re.compile(r'\[class=fnr\]\{\\high\{\\(?:foot|end)note\[href=#((?P<docid1>.*?)-)?(?:foot|end)note-(?P<href>.*?),\s?id=((?P<docid2>.*?)-)?footnote-ref-(?P<ref>.*?)\]\{(?P<mark>.*?)\}}\}', flags=re.I|re.U|re.M)

#re.compile('\\\\high\{\\\\footnote\[href=#((?P<docid1>.*?)-)?(?:foot|end)note-(?P<href>.*?),\s?id=((?P<docid2>.*?)-)?footnote-ref-(?P<ref>.*?)\]\{(?P<mark>.*?)\}\}', flags=re.I|re.U|re.M)

# \startitem
#[id=footnote-3]\startparagraph
# Tellkamp 2008, 490. \goto[href=#footnote-ref-3]{↑}
#\stopparagraph
#
#\stopitem
reFN = re.compile(r'\\startitem\s*\[id=((?P<docid>.*?)-)?(?:foot|end)note-(?P<id>\d+)\]\\startparagraph\s+(?P<text>.*?)\s*\\goto\[.*?\]\{.*?\}\s+\\stopparagraph\s+\\stopitem', flags=re.I|re.U|re.M|re.S)


def fix_footnotes(context):
    """
    Combine footnote markers and contents into \footnote[ref]{content}
    """
    # collect footnotes
    footnotes = {}
    for m in reFN.finditer(context):
        footnotes[m.group('id')] = m.group('text')
        context = context.replace(m.group(0), '')
    logger.info('%d footnotes found.', len(footnotes.keys()))
    logger.debug(footnotes)

    # replace footnote references by footnote
    for m in reFNref.finditer(context):
        href = m.group('href')
        ref = m.group('ref')
        logger.debug(m.groups())
        try:
            fntext = '\\footnote[fn%s]{%s}' % (m.group('ref'), footnotes[m.group('ref')])
        except KeyError as e:
            logger.error('Wrong footnote reference "%s"' % m.group('ref'))
            fntext = '\\footnote[fn%s]{WRONG REFERENCE}' % m.group('ref')
        context = context.replace(m.group(0), fntext)

    return context
