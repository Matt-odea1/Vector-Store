import re
from typing import List


def split_by_markdown_heading(text: str) -> List[str]:
    heading_iter = list(re.finditer(r"(?m)^###\s+.+$", text))
    if not heading_iter:
        return [text.strip()] if text.strip() else []

    sections: List[str] = []
    for i, m in enumerate(heading_iter):
        start = m.start()
        end = heading_iter[i + 1].start() if i + 1 < len(heading_iter) else len(text)
        chunk = text[start:end].strip()
        if chunk:
            sections.append(chunk)
    return sections