"""
edstem_xml_to_html.py

Converts Edstem XML content to HTML for PDF rendering.
"""
import xml.etree.ElementTree as ET
from html import escape

def convert_edstem_xml_to_html(xml_content: str) -> str:
    """
    Convert Edstem XML content to HTML string.
    Handles bold, italics, code, pre, lists, headings, images, etc.
    """
    def xml_to_html(elem):
        tag = elem.tag.lower()
        # Map Edstem XML tags to HTML tags
        tag_map = {
            'b': 'strong',
            'i': 'em',
            'u': 'u',
            'code': 'code',
            'pre': 'pre',
            'ul': 'ul',
            'ol': 'ol',
            'li': 'li',
            'h1': 'h1',
            'h2': 'h2',
            'h3': 'h3',
            'h4': 'h4',
            'h5': 'h5',
            'h6': 'h6',
            'img': 'img',
            'a': 'a',
            'math': 'span',  # Placeholder for math, can be improved
        }
        html_tag = tag_map.get(tag, tag)
        # Handle images
        if tag == 'img':
            src = elem.attrib.get('src', '')
            alt = elem.attrib.get('alt', '')
            return f'<img src="{escape(src)}" alt="{escape(alt)}" />'
        # Handle links
        if tag == 'a':
            href = elem.attrib.get('href', '#')
            inner = ''.join(xml_to_html(child) for child in elem)
            return f'<a href="{escape(href)}">{inner}</a>'
        # Handle math (placeholder)
        if tag == 'math':
            return f'<span class="math">{escape(elem.text or "")}</span>'
        # Handle lists and other tags
        inner_html = ''
        if elem.text:
            inner_html += escape(elem.text)
        for child in elem:
            inner_html += xml_to_html(child)
            if child.tail:
                inner_html += escape(child.tail)
        return f'<{html_tag}>{inner_html}</{html_tag}>'

    # Parse XML
    root = ET.fromstring(xml_content)
    # If the root is not a content wrapper, wrap in <div>
    html = xml_to_html(root)
    if not html.startswith('<div'):
        html = f'<div>{html}</div>'
    return html

