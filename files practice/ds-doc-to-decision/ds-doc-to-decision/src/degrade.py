"""Text-domain degradation (D3): simulates OCR-style corruption at a given intensity.
Deterministic per (set text, level, seed) so runs are reproducible."""
import random, re

SUBS = {"0": "O", "O": "0", "1": "l", "l": "1", "5": "S", "8": "B", ".": ",", "I": "1"}

def degrade(text, level, seed=42):
    if level <= 0:
        return text
    import zlib as _z; rng = random.Random((_z.crc32(text[:80].encode()) & 0xffff) * 1000 + int(level * 1000) + seed)
    out = []
    for ch in text:
        r = rng.random()
        if r < level * 0.30 and ch in SUBS:
            out.append(SUBS[ch])                      # OCR confusion
        elif r < level * 0.38 and ch == " ":
            out.append("")                            # collapsed space
        elif r < level * 0.42 and ch.isalnum():
            out.append("")                            # dropped char
        else:
            out.append(ch)
    return "".join(out)
