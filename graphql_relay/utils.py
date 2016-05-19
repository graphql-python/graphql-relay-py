from base64 import b64encode as _base64, b64decode as _unbase64

try:
    str_type = basestring
    base64 = _base64
    unbase64 = _unbase64

    def is_str(s):
        return isinstance(s, basestring)

except NameError:
    def base64(s):
        return _base64(bytes(s, 'utf-8')).decode('utf-8')

    def unbase64(s):
        return _unbase64(s).decode('utf-8')

    def is_str(s):
        return isinstance(s, str)


def resolve_maybe_thunk(f):
    if callable(f):
        return f()
    return f
