import base64

from .. import utils


def test_base64_encode_unicode_strings_correctly():
    my_unicode = u'\xfb\xf1\xf6'
    my_base64 = utils.base64(my_unicode)
    assert my_base64 == base64.b64encode(my_unicode.encode('utf-8')).decode('utf-8')

    my_unicode = u'\u06ED'
    my_base64 = utils.base64(my_unicode)
    assert my_base64 == base64.b64encode(my_unicode.encode('utf-8')).decode('utf-8')


def test_base64_encode_strings_correctly():
    my_string = 'abc'
    my_base64 = utils.base64(my_string)
    assert my_base64 == base64.b64encode(my_string.encode('utf-8')).decode('utf-8')


def test_unbase64_decodes_unicode_strings_correctly():
    my_unicode = u'\xfb\xf1\xf6'
    my_converted_unicode = utils.unbase64(utils.base64(my_unicode))
    assert my_unicode == my_converted_unicode


def test_unbase64_decodes_strings_correctly():
    my_string = 'abc'
    my_converted_string = utils.unbase64(utils.base64(my_string))
    assert my_string == my_converted_string
