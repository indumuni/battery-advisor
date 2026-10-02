import re
from dataclasses import dataclass

MAX_CHARS = 1200

@dataclass
class Chunk:
    text: str
    heading: str

def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    pieces, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        if cur and len(cur) + len(para) + 2 > max_chars:
            pieces.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        pieces.append(cur)
    return pieces

def split_markdown(md: str, max_chars: int = MAX_CHARS) -> list[Chunk]:
    """Split by heading (levels 1-3). Each chunk is prefixed with its heading path."""
    chunks: list[Chunk] = []
    path: list[tuple[int, str]] = []
    buf: list[str] = []

    def flush():
        body = "\n".join(buf).strip()
        buf.clear()
        if not body:
            return
        heading = " > ".join(h for _, h in path)
        for piece in _split_long(body, max_chars):
            chunks.append(Chunk(text=f"{heading}\n\n{piece}" if heading else piece, heading=heading))

    for line in md.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            flush()
            level = len(m.group(1))
            path[:] = [p for p in path if p[0] < level]
            path.append((level, m.group(2).strip()))
        else:
            buf.append(line)
    flush()
    return chunks