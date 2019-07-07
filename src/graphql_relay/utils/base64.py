from base64 import b64encode, b64decode

__all__ = ['base64', 'unbase64']


def base64(s: str) -> str:
    """"Encode the string s using Base64."""
    return b64encode(s.encode('utf-8')).decode('utf-8')


def unbase64(s: str) -> str:
    """"Decode the string s using Base64."""
    return b64decode(s).decode('utf-8')
