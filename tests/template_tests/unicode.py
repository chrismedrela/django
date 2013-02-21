# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import (Template, TemplateEncodingError, Context,
    TemplateEngineWithBuiltins)
from django.utils.safestring import SafeData
from django.utils import six
from django.utils.unittest import TestCase


class UnicodeTests(TestCase):
    def test_template(self):
        engine = TemplateEngineWithBuiltins()

        # Templates can be created from unicode strings.
        first_template = Template('ŠĐĆŽćžšđ {{ var }}', engine=engine)

        # Templates can also be created from bytestrings. These are assumed to
        # be encoded using UTF-8.
        source = (b'\xc5\xa0\xc4\x90\xc4\x86\xc5\xbd\xc4\x87\xc5\xbe'
                  b'\xc5\xa1\xc4\x91 {{ var }}')
        second_template = Template(source, engine=engine)

        source = b'\x80\xc5\xc0'
        self.assertRaises(TemplateEncodingError, Template, source, engine=engine)

        # Contexts can be constructed from unicode or UTF-8 bytestrings.
        c1 = Context({b"var": b"foo"})
        c2 = Context({"var": b"foo"})
        c3 = Context({b"var": "Đđ"})
        c4 = Context({"var": b"\xc4\x90\xc4\x91"})

        # Since both templates and all four contexts represent the same thing,
        # they all render the same (and are returned as unicode objects and
        # "safe" objects as well, for auto-escaping purposes).
        self.assertEqual(first_template.render(c3), second_template.render(c3))
        self.assertIsInstance(first_template.render(c3), six.text_type)
        self.assertIsInstance(first_template.render(c3), SafeData)
