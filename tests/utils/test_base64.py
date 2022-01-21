from graphql_relay.utils import base64, unbase64


example_unicode = "Some examples:  ͢❤😀"
example_base64 = "U29tZSBleGFtcGxlczogIM2i4p2k8J+YgA=="


def describe_base64_conversion():
    def converts_from_unicode_to_base64():
        assert base64(example_unicode) == example_base64

    def converts_from_base64_to_unicode():
        assert unbase64(example_base64) == example_unicode

    def converts_invalid_base64_to_empty_string():
        assert unbase64("") == ""
        assert unbase64("invalid") == ""
        assert unbase64(example_base64[-1:]) == ""
        assert unbase64(example_base64[1:]) == ""
        assert unbase64("!" + example_base64[1:]) == ""
        assert unbase64("Ü" + example_base64[1:]) == ""

    def converts_from_unicode_as_bytes_to_base64():
        bytes_example_code = example_unicode.encode("utf-8")
        assert base64(bytes_example_code) == example_base64  # type: ignore
        bytearray_example_code = bytearray(bytes_example_code)
        assert base64(bytearray_example_code) == example_base64  # type: ignore

    def converts_from_base64_as_bytes_to_unicode():
        bytes_example_code = example_base64.encode("ascii")
        assert unbase64(bytes_example_code) == example_unicode  # type: ignore
        bytearray_example_code = bytearray(bytes_example_code)
        assert unbase64(bytearray_example_code) == example_unicode  # type: ignore
