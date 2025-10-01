"""
edstem_to_pdf.py

Main script to convert Edstem XML to PDF using WeasyPrint.
"""
import sys
import os
from weasyprint import HTML, CSS
from edstem_xml_to_html import convert_edstem_xml_to_html


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert Edstem XML to Edstem-style PDF.')
    parser.add_argument('input', help='Input Edstem XML file')
    parser.add_argument('output', help='Output PDF file')
    parser.add_argument('--css', default='edstem_style.css', help='CSS file for Edstem styling (default: edstem_style.css)')
    args = parser.parse_args()

    # Read XML content
    with open(args.input, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    # Convert XML to HTML
    html_content = convert_edstem_xml_to_html(xml_content)

    # Read CSS
    if os.path.exists(args.css):
        css = CSS(filename=args.css)
    else:
        print(f"Warning: CSS file '{args.css}' not found. Using default styling.")
        css = None

    # Render PDF
    html = HTML(string=html_content)
    if css:
        html.write_pdf(args.output, stylesheets=[css])
    else:
        html.write_pdf(args.output)
    print(f"PDF generated: {args.output}")

if __name__ == '__main__':
    main()

