import lzma
import base64

html_string = f"""
  <body>
    <div> {"text"*10000000000}
  </body>
"""


def shorten_text_lzma(long_text):
    """Compresses a string using LZMA and returns a short base64-encoded string."""
    text_bytes = long_text.encode("utf-8")
    compressed_bytes = lzma.compress(text_bytes)
    short_string = base64.b64encode(compressed_bytes).decode("ascii")
    return short_string


def lengthen_text_lzma(short_string):
    """Decompresses an LZMA compressed string."""
    compressed_bytes = base64.b64decode(short_string.encode("ascii"))
    decompressed_bytes = lzma.decompress(compressed_bytes)
    original_text = decompressed_bytes.decode("utf-8")
    return original_text


short = shorten_text_lzma(html_string)
print(len(short))
# long = lengthen_text_lzma(short)
# with open("test.html", "w", encoding="utf-8") as f:
#     f.write(long)
