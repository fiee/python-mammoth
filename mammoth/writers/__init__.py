from .html import HtmlWriter
from .markdown import MarkdownWriter
from .context import ConTeXtWriter


def writer(output_format=None):
    if output_format is None:
        output_format = "html"

    return _writers[output_format]()


def formats():
    return _writers.keys()


_writers = {
    "html": HtmlWriter,
    "markdown": MarkdownWriter,
    "context": ConTeXtWriter
}
