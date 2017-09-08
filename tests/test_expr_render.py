import re
import sys

import pytest

from devtools import Debug, debug


def foobar(a, b, c):
    return a + b + c


def test_simple():
    a = [1, 2, 3]
    v = debug.format(len(a))
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    # print(s)
    assert (
        'tests/test_expr_render.py:<line no> test_simple: len(a) = 3 (int)'
    ) == s


def test_exotic_types():
    aa = [1, 2, 3]
    v = debug.format(
        sum(aa),
        1 == 2,
        1 < 2,
        1 << 2,
        't' if True else 'f',
        1 or 2,
        [a for a in aa],
        {a for a in aa},
        {a: a + 1 for a in aa},
        (a for a in aa),
    )
    s = re.sub(r':\d{2,}', ':<line no>', str(v))
    s = re.sub(r'(at 0x)\w+', r'\1<hash>', s)
    print(s)
    # list and generator comprehensions are wrong because ast is wrong, see https://bugs.python.org/issue31241
    assert (
        'tests/test_expr_render.py:<line no> test_exotic_types\n'
        '  sum(aa) = 6 (int)\n'
        '  1 == 2 = False (bool)\n'
        '  1 < 2 = True (bool)\n'
        '  1 << 2 = 4 (int)\n'
        '  \'t\' if True else \'f\' = "t" (str) len=1\n'
        '  1 or 2 = 1 (int)\n'
        '  [a for a in aa] = [1, 2, 3] (list)\n'
        '  {a for a in aa} = {1, 2, 3} (set)\n'
        '  {a: a + 1 for a in aa} = {1: 2, 2: 3, 3: 4} (dict)\n'
        '  (a for a in aa) = <generator object test_exotic_types.<locals>.<genexpr> at 0x<hash>> (generator)'
    ) == s


def test_newline():
    v = debug.format(
        foobar(1, 2, 3))
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    # print(s)
    assert (
        'tests/test_expr_render.py:<line no> test_newline: foobar(1, 2, 3) = 6 (int)'
    ) == s


def test_trailing_bracket():
    v = debug.format(
        foobar(1, 2, 3)
    )
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    # print(s)
    assert (
        'tests/test_expr_render.py:<line no> test_trailing_bracket: foobar(1, 2, 3) = 6 (int)'
    ) == s


def test_multiline():
    v = debug.format(
        foobar(1,
               2,
               3)
    )
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    # print(s)
    assert (
        'tests/test_expr_render.py:<line no> test_multiline: foobar(1, 2, 3) = 6 (int)'
    ) == s


def test_multiline_trailing_bracket():
    v = debug.format(
        foobar(1, 2, 3
               ))
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    # print(s)
    assert (
        'tests/test_expr_render.py:<line no> test_multiline_trailing_bracket: foobar(1, 2, 3 ) = 6 (int)'
    ) == s


@pytest.mark.skipif(sys.version_info < (3, 6), reason='kwarg order is not guaranteed for 3.5')
def test_kwargs():
    v = debug.format(
        foobar(1, 2, 3),
        a=6,
        b=7
    )
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    assert (
        'tests/test_expr_render.py:<line no> test_kwargs\n'
        '  foobar(1, 2, 3) = 6 (int)\n'
        '  a = 6 (int)\n'
        '  b = 7 (int)'
    ) == s


@pytest.mark.skipif(sys.version_info < (3, 6), reason='kwarg order is not guaranteed for 3.5')
def test_kwargs_multiline():
    v = debug.format(
        foobar(1, 2,
               3),
        a=6,
        b=7
    )
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    assert (
        'tests/test_expr_render.py:<line no> test_kwargs_multiline\n'
        '  foobar(1, 2, 3) = 6 (int)\n'
        '  a = 6 (int)\n'
        '  b = 7 (int)'
    ) == s


def test_multiple_trailing_lines():
    v = debug.format(
        foobar(
            1, 2, 3
        ),
    )
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    assert (
        'tests/test_expr_render.py:<line no> test_multiple_trailing_lines: foobar( 1, 2, 3 ) = 6 (int)'
    ) == s


def test_syntax_warning():
    # exceed the 4 extra lines which are normally checked
    with pytest.warns(SyntaxWarning) as warning_checker:
        v = debug.format(
            abs(
                abs(
                    abs(
                        abs(
                            -1
                        )
                    )
                )
            )
        )
    assert len(warning_checker) == 1
    warning = warning_checker.list[0]
    print(warning.message)
    assert 'Error: unexpected EOF while parsing (test_expr_render.py' in str(warning.message)
    # check only the original code is included in the warning
    assert '-1\n"' in str(warning.message)
    s = re.sub(':\d{2,}', ':<line no>', str(v))
    assert (
        'tests/test_expr_render.py:<line no> test_syntax_warning: 1 (int)'
    ) == s


def test_no_syntax_warning():
    # exceed the 4 extra lines which are normally checked
    debug_ = Debug(warnings=False)
    with pytest.warns(None) as warning_checker:
        v = debug_.format(
            abs(
                abs(
                    abs(
                        abs(
                            -1
                        )
                    )
                )
            )
        )
        assert 'test_no_syntax_warning: 1 (int)' in str(v)
    assert len(warning_checker) == 0