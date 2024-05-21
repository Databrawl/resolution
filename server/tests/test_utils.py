from vdb.utils import _clean


def test_clean():
    assert _clean("• Hello, World!") == "Hello, World!"
    assert _clean("Hello - World!") == "Hello World!"
    assert _clean("Hello,    World!") == "Hello, World!"
    assert _clean("Hello, Wörld!") == "Hello, Wrld!"
    assert _clean("1. Hello, World!") == "Hello, World!"
    assert _clean("Hello, World!....") == "Hello, World!"
    assert _clean("Hello, \nWorld!") == "Hello, World!"
    assert _clean("Hello, ЯЯЯ“World!”") == 'Hello, World!'
    assert _clean("") == ""  # Test case for empty string
