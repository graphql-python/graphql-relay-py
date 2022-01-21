from typing import Iterator, List

__all__ = ["base64", "unbase64"]

Base64String = str


def base64(s: str) -> Base64String:
    """Encode the string s using Base64."""
    if isinstance(s, (bytearray, bytes)):
        s = s.decode("unicode")  # handle encoded string gracefully

    unicode_list = list(str_to_unicode_seq(s))
    length = len(unicode_list)
    rest = length % 3
    result: List[str] = []
    extend = result.extend

    for i in range(0, length - rest, 3):
        a, b, c = unicode_list[i : i + 3]
        result.extend(
            (
                first_6_bits(a),
                last_2_bits_and_first_4_bits(a, b),
                last_4_bits_and_first_2_bits(b, c),
                last_6_bits(c),
            )
        )

    if rest == 1:
        a = unicode_list[-1]
        extend((first_6_bits(a), last_2_bits_and_first_4_bits(a, 0), "=="))
    elif rest == 2:
        a, b = unicode_list[-2:]
        extend(
            (
                first_6_bits(a),
                last_2_bits_and_first_4_bits(a, b),
                last_4_bits_and_first_2_bits(b, 0),
                "=",
            )
        )

    return "".join(result)


def first_6_bits(a: int) -> str:
    return to_base_64_char(a >> 2 & 0x3F)


def last_2_bits_and_first_4_bits(a: int, b: int) -> str:
    return to_base_64_char((a << 4 | b >> 4) & 0x3F)


def last_4_bits_and_first_2_bits(b: int, c: int) -> str:
    return to_base_64_char((b << 2 | c >> 6) & 0x3F)


def last_6_bits(c: int) -> str:
    return to_base_64_char(c & 0x3F)


def unbase64(s: str) -> str:
    """Decode the string s using Base64."""
    if isinstance(s, (bytearray, bytes)):
        s = s.decode("ascii")  # handle encoded string gracefully

    unicode_list: List[int] = []
    extend = unicode_list.extend
    length = len(s)

    for i in range(0, length, 4):
        try:
            a, b, c, d = [from_base_64_char(char) for char in s[i : i + 4]]
        except (KeyError, ValueError):
            return ""  # for compatibility
        bitmap_24 = a << 18 | b << 12 | c << 6 | d
        extend((bitmap_24 >> 16 & 0xFF, bitmap_24 >> 8 & 0xFF, bitmap_24 & 0xFF))

    i = length - 1
    while i > 0 and s[i] == "=":
        i -= 1
        unicode_list.pop()

    return "".join(unicode_list_to_str(unicode_list))


b64_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

b64_character_map = {c: i for i, c in enumerate(b64_characters)}


def to_base_64_char(bit_map_6: int) -> str:
    return b64_characters[bit_map_6]


def from_base_64_char(base_64_char: str) -> int:
    return 0 if base_64_char == "=" else b64_character_map[base_64_char]


def str_to_unicode_seq(s: str) -> Iterator[int]:
    for utf_char in s:
        code = ord(utf_char)
        if code < 0x80:
            yield code
        elif code < 0x800:
            yield 0xC0 | code >> 6
            yield 0x80 | code & 0x3F
        elif code < 0x10000:
            yield 0xE0 | code >> 12
            yield 0x80 | code >> 6 & 0x3F
            yield 0x80 | code & 0x3F
        else:
            yield 0xF0 | code >> 18
            yield 0x80 | code >> 12 & 0x3F
            yield 0x80 | code >> 6 & 0x3F
            yield 0x80 | code & 0x3F


def unicode_list_to_str(s: List[int]) -> Iterator[str]:
    s.reverse()
    next_code = s.pop
    while s:
        a = next_code()
        if a & 0x80 == 0:
            yield chr(a)
            continue
        b = next_code()
        if a & 0xE0 == 0xC0:
            yield chr((a & 0x1F) << 6 | b & 0x3F)
            continue
        c = next_code()
        if a & 0xF0 == 0xE0:
            yield chr((a & 0x0F) << 12 | (b & 0x3F) << 6 | c & 0x3F)
            continue
        d = next_code()
        yield chr((a & 0x07) << 18 | (b & 0x3F) << 12 | (c & 0x3F) << 6 | d & 0x3F)
