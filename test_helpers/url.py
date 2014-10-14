try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def assert_url_equal(expected, returned):
    parsed_expected = urlparse.urlparse(expected)
    parsed_returned = urlparse.urlparse(returned)

    error = '{0}: "{1}" did not match expected {0}: "{2}"'
    for attr in ['scheme', 'netloc', 'path', 'params', 'fragment']:
        parsed = getattr(parsed_expected, attr)
        expect = getattr(parsed_returned, attr)
        assert parsed == expect, error.format(attr, expect, parsed)

    parsed_query = urlparse.parse_qs(parsed_expected.query)
    expected_query = urlparse.parse_qs(parsed_returned.query)

    assert expected_query == parsed_query, error.format(
        'query', expected_query, parsed_query)
