from __future__ import unicode_literals

from django import template
from django.utils.unittest import TestCase

class CallableVariablesTests(TestCase):

    def setUp(self):
        self.engine = template.TemplateEngineWithBuiltins()

    def assert_render(self, template_content, expected_output, context):
        t = template._Template(self.engine, template_content)
        self.assertEqual(t.render(context), expected_output)

    def get_doodad(self, alters_data=None, do_not_call_in_templates=None):
        class Doodad(object):
            def __init__(self, value):
                self.num_calls = 0
                self.value = value
            def __call__(self):
                self.num_calls += 1
                return {"the_value": self.value}
        if alters_data:
            Doodad.alters_data = True
        if do_not_call_in_templates:
            Doodad.do_not_call_in_templates = True

        return Doodad(42)

    def test_callable(self):
        my_doodad = self.get_doodad()
        context = template.Context({"my_doodad": my_doodad})

        # We can't access ``my_doodad.value`` in the template, because
        # ``my_doodad.__call__`` will be invoked first, yielding a dictionary
        # without a key ``value``.
        self.assert_render('{{ my_doodad.value }}', '', context)

        # We can confirm that the doodad has been called
        self.assertEqual(my_doodad.num_calls, 1)

        # But we can access keys on the dict that's returned
        # by ``__call__``, instead.
        self.assert_render('{{ my_doodad.the_value }}', '42', context)
        self.assertEqual(my_doodad.num_calls, 2)

    def test_alters_data(self):
        my_doodad = self.get_doodad(alters_data=True)
        context = template.Context({"my_doodad": my_doodad})

        # Since ``my_doodad.alters_data`` is True, the template system will not
        # try to call our doodad but will use TEMPLATE_STRING_IF_INVALID
        self.assert_render('{{ my_doodad.value }}', '', context)
        self.assert_render('{{ my_doodad.the_value }}', '', context)

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)

    def test_do_not_call(self):
        my_doodad = self.get_doodad(do_not_call_in_templates=True)
        context = template.Context({"my_doodad": my_doodad})

        # Since ``my_doodad.do_not_call_in_templates`` is True, the template
        # system will not try to call our doodad.  We can access its attributes
        # as normal, and we don't have access to the dict that it returns when
        # called.
        self.assert_render('{{ my_doodad.value }}', '42', context)
        self.assert_render('{{ my_doodad.the_value }}', '', context)

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)

    def test_do_not_call_and_alters_data(self):
        # If we combine ``alters_data`` and ``do_not_call_in_templates``, the
        # ``alters_data`` attribute will not make any difference in the
        # template system's behavior.

        my_doodad = self.get_doodad(alters_data=True,
                                    do_not_call_in_templates=True)
        context = template.Context({"my_doodad": my_doodad})

        self.assert_render('{{ my_doodad.value }}', '42', context)
        self.assert_render('{{ my_doodad.the_value }}', '', context)

        # Double-check that the object was really never called during the
        # template rendering.
        self.assertEqual(my_doodad.num_calls, 0)
