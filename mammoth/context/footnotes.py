# coding=utf-8
"""
ConTeXt format tools: Footnotes and Comments
2015-2018 by fiëé visuëlle, www.fiee.net
ConTeXt is a TeX format, see www.contextgarden.net
"""
from __future__ import unicode_literals
import re
import logging
logger = logging.getLogger()

reFNref = re.compile(r'(?:\[class=fnr\]\{)?\\high\{\\(?:foot|end)note\[href=#((?P<docid1>.*?)-)?(?:foot|end)note-(?P<href>\d+),\s?id=((?P<docid2>.*?)-)?(?:foot|end)note-ref-(?P<ref>\d+)\]\{.*?\}\}\}?', flags=re.I|re.U|re.M)

reFN = re.compile(r'\\startitem\s*\[id=((?P<docid>.*?)-)?(?:foot|end)note-(?P<id>\d+)\]\\startparagraph\s+(?P<text>.*?)\s*\\goto\[.*?\]\{.*?\}\s+\\stopparagraph\s+\\stopitem', flags=re.I|re.U|re.M|re.S)

reFN2 = re.compile(r'\\startitem\s*\[id=((?P<docid>.*?)-)?(?:foot|end)note-(?P<id>\d+)\]\\(?:foot|end)note\{\s*(?P<text>.*?)\}\\startparagraph\s+\\goto\[.*?\]\{.*?\}\s+\\stopparagraph\s+\\stopitem', flags=re.I|re.U|re.M|re.S)

reCMref = re.compile(r'\[class=comment\]\{\\goto\[href=#((?P<docid1>.*?)-)?comment-(?P<href>.*?),\s?id=((?P<docid2>.*?)-)?comment-ref-(?P<ref>.*?)\]\{(?P<mark>.*?)\}\}', flags=re.I|re.U|re.M)

reCM = re.compile(r'(?:dldt)?\[id=((?P<docid>.*?)-)?comment-(?P<id>\d+)\]Comment \[(?P<mark>.*?)\](?:dtdd)?\\startparagraph\s+(?P<text>.*?)\s*\\goto\[.*?\]\{.*?\}\s+\\stopparagraph\s+(?:dddl)?', flags=re.I|re.U|re.M|re.S)


def fix_footnotes(context):
    """
    Combine footnote markers and contents into \footnote[ref]{content}
    as well as comments into \startcomment[] ... \stopcomment
    """
    # collect footnotes
    footnotes = {}
    for m in reFN.finditer(context):
        footnotes[m.group('id')] = m.group('text')
        context = context.replace(m.group(0), '')
    for m in reFN2.finditer(context):
        footnotes[m.group('id')] = m.group('text')
        context = context.replace(m.group(0), '')
    logger.info('%d footnotes found.', len(footnotes.keys()))
    logger.debug(footnotes)

    # collect comments
    comments = {}
    for m in reCM.finditer(context):
        comments[m.group('id')] = m.group('text')
        context = context.replace(m.group(0), '')
    logger.info('%d comments found.', len(comments.keys()))
    logger.debug(comments)

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

    # replace comment references by comment
    for m in reCMref.finditer(context):
        href = m.group('href')
        ref = m.group('ref')
        logger.debug(m.groups())
        try:
            cmtext = '\\startcomment[cm%s]\n%s\n\\stopcomment' % (m.group('ref'), comments[m.group('ref')])
        except KeyError as e:
            logger.error('Wrong comment reference "%s"' % m.group('ref'))
            fntext = '\\startcomment[cm%s]\nWRONG REFERENCE\n\\stopcomment' % m.group('ref')
        context = context.replace(m.group(0), cmtext)

    return context
