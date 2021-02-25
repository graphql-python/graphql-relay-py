from graphql_relay.utils import base64, unbase64


example_unicode = "Some examples: ❤😀"
example_base64 = "U29tZSBleGFtcGxlczog4p2k8J-YgA=="


def describe_base64_conversion():
    def converts_from_unicode_to_base64():
        assert base64(example_unicode) == example_base64

    def converts_from_base_64_to_unicode():
        assert unbase64(example_base64) == example_unicode
