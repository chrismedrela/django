from __future__ import absolute_import, unicode_literals

from django import template
from django.utils import six
from django.utils.unittest import TestCase

from .templatetags import custom


class CustomFilterTests(TestCase):
    def test_filter(self):
        engine = template.TemplateEngineWithBuiltins()
        engine.add_library('custom', custom.get_templatetags(engine))
        t = template._Template(engine, "{% load custom %}{{ string|trim:5 }}")
        context = template.Context({"string": "abcdefghijklmnopqrstuvwxyz"})
        output = t.render(context)
        self.assertEqual(output, "abcde")


class CustomTagTests(TestCase):
    def setUp(self):
        self.engine = template.TemplateEngineWithBuiltins()
        self.engine.add_library('custom', custom.get_templatetags(self.engine))

    def assert_render(self, template_content, expected_output, context=None):
        t = template._Template(self.engine, template_content)
        context = context or template.Context({'value': 42})
        self.assertEqual(t.render(context), expected_output)

    def assert_compilation_failes(self, template_content, error_message_regex):
        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            error_message_regex,
            template._Template, self.engine, template_content)

    def test_simple_tags(self):
        tests = [
            ('{% load custom %}{% no_params %}',
             'no_params - Expected result'),

            ('{% load custom %}{% one_param 37 %}',
             'one_param - Expected result: 37'),

            ('{% load custom %}{% explicit_no_context 37 %}',
             'explicit_no_context - Expected result: 37'),

            ('{% load custom %}{% no_params_with_context %}',
             'no_params_with_context - Expected result (context value: 42)'),

            ('{% load custom %}{% params_and_context 37 %}',
             'params_and_context - Expected result (context value: 42): 37'),

            ('{% load custom %}{% simple_two_params 37 42 %}',
             'simple_two_params - Expected result: 37, 42'),

            ('{% load custom %}{% simple_one_default 37 %}',
             'simple_one_default - Expected result: 37, hi'),

            ('{% load custom %}{% simple_one_default 37 two="hello" %}',
             'simple_one_default - Expected result: 37, hello'),

            ('{% load custom %}{% simple_one_default one=99 two="hello" %}',
             'simple_one_default - Expected result: 99, hello'),

            ('{% load custom %}{% simple_one_default 37 42 %}',
             'simple_one_default - Expected result: 37, 42'),

            ('{% load custom %}{% simple_unlimited_args 37 %}',
             'simple_unlimited_args - Expected result: 37, hi'),

            ('{% load custom %}{% simple_unlimited_args 37 42 56 89 %}',
             'simple_unlimited_args - Expected result: 37, 42, 56, 89'),

            ('{% load custom %}{% simple_only_unlimited_args %}',
             'simple_only_unlimited_args - Expected result: '),

            ('{% load custom %}{% simple_only_unlimited_args 37 42 56 89 %}',
             'simple_only_unlimited_args - Expected result: 37, 42, 56, 89'),

            ('{% load custom %}{% simple_unlimited_args_kwargs '
             '37 40|add:2 56 eggs="scrambled" four=1|add:3 %}',
             'simple_unlimited_args_kwargs - Expected result: '
             '37, 42, 56 / eggs=scrambled, four=4'),
        ]

        for template_content, expected_output in tests:
            self.assert_render(template_content, expected_output)

        tests = [
            ('{% load custom %}{% simple_one_default 99 two="hello" three="foo" %}',
             "'simple_one_default' received unexpected keyword argument 'three'"),

            ('{% load custom %}{% simple_two_params 37 42 56 %}',
             "'simple_two_params' received too many positional arguments"),

            ('{% load custom %}{% simple_one_default 37 42 56 %}',
             "'simple_one_default' received too many positional arguments"),

            ('{% load custom %}{% simple_unlimited_args_kwargs '
             '37 40|add:2 eggs="scrambled" 56 four=1|add:3 %}',
             "'simple_unlimited_args_kwargs' received some positional "
             "argument\(s\) after some keyword argument\(s\)"),

            ('{% load custom %}{% simple_unlimited_args_kwargs '
             '37 eggs="scrambled" eggs="scrambled" %}',
             "'simple_unlimited_args_kwargs' received multiple values "
             "for keyword argument 'eggs'"),
        ]

        for template_content, error_message_regex in tests:
            self.assert_compilation_failes(template_content, error_message_regex)

    def test_simple_tag_registration(self):
        # Test that the decorators preserve the decorated function's docstring, name and attributes.
        self.verify_tag(custom.no_params, 'no_params')
        self.verify_tag(custom.one_param, 'one_param')
        self.verify_tag(custom.explicit_no_context, 'explicit_no_context')
        self.verify_tag(custom.no_params_with_context, 'no_params_with_context')
        self.verify_tag(custom.params_and_context, 'params_and_context')
        self.verify_tag(custom.simple_unlimited_args_kwargs, 'simple_unlimited_args_kwargs')
        self.verify_tag(custom.simple_tag_without_context_parameter, 'simple_tag_without_context_parameter')

    def verify_tag(self, tag, name):
        self.assertEqual(tag.__name__, name)
        self.assertEqual(tag.__doc__, 'Expected %s __doc__' % name)
        self.assertEqual(tag.__dict__['anything'], 'Expected %s __dict__' % name)

    def test_simple_tag_missing_context(self):
        # The 'context' parameter must be present when takes_context is True
        self.assert_compilation_failes(
            '{% load custom %}{% simple_tag_without_context_parameter 123 %}',
            "'simple_tag_without_context_parameter' is decorated "
            "with takes_context=True so it must have a first argument of 'context'")

    def test_inclusion_tags(self):
        tests = [
            ('{% load custom %}{% inclusion_no_params %}',
             'inclusion_no_params - Expected result\n'),

            ('{% load custom %}{% inclusion_one_param 37 %}',
             'inclusion_one_param - Expected result: 37\n'),

            ('{% load custom %}{% inclusion_explicit_no_context 37 %}',
             'inclusion_explicit_no_context - Expected result: 37\n'),

            ('{% load custom %}{% inclusion_no_params_with_context %}',
             'inclusion_no_params_with_context - '
             'Expected result (context value: 42)\n'),

            ('{% load custom %}{% inclusion_params_and_context 37 %}',
             'inclusion_params_and_context - '
             'Expected result (context value: 42): 37\n'),

            ('{% load custom %}{% inclusion_two_params 37 42 %}',
             'inclusion_two_params - Expected result: 37, 42\n'),

            ('{% load custom %}{% inclusion_one_default 37 %}',
             'inclusion_one_default - Expected result: 37, hi\n'),

            ('{% load custom %}{% inclusion_one_default 37 two="hello" %}',
             'inclusion_one_default - Expected result: 37, hello\n'),

            ('{% load custom %}{% inclusion_one_default one=99 two="hello" %}',
             'inclusion_one_default - Expected result: 99, hello\n'),

            ('{% load custom %}{% inclusion_one_default 37 42 %}',
             'inclusion_one_default - Expected result: 37, 42\n'),

            ('{% load custom %}{% inclusion_unlimited_args 37 %}',
             'inclusion_unlimited_args - Expected result: 37, hi\n'),

            ('{% load custom %}{% inclusion_unlimited_args 37 42 56 89 %}',
             'inclusion_unlimited_args - Expected result: 37, 42, 56, 89\n'),

            ('{% load custom %}{% inclusion_only_unlimited_args %}',
             'inclusion_only_unlimited_args - Expected result: \n'),

            ('{% load custom %}{% inclusion_only_unlimited_args 37 42 56 89 %}',
             'inclusion_only_unlimited_args - Expected result: 37, 42, 56, 89\n'),

            ('{% load custom %}{% inclusion_unlimited_args_kwargs '
             '37 40|add:2 56 eggs="scrambled" four=1|add:3 %}',
             'inclusion_unlimited_args_kwargs - Expected result: '
             '37, 42, 56 / eggs=scrambled, four=4\n'),
         ]

        for template_content, expected_output in tests:
            self.assert_render(template_content, expected_output)

        tests = [
            ('{% load custom %}{% inclusion_one_default 99 two="hello" three="foo" %}',
             "'inclusion_one_default' received unexpected keyword argument 'three'"),

            ('{% load custom %}{% inclusion_two_params 37 42 56 %}',
             "'inclusion_two_params' received too many positional arguments"),

            ('{% load custom %}{% inclusion_one_default 37 42 56 %}',
             "'inclusion_one_default' received too many positional arguments"),

            ('{% load custom %}{% inclusion_one_default %}',
             "'inclusion_one_default' did not receive value\(s\) "
             "for the argument\(s\): 'one'"),

            ('{% load custom %}{% inclusion_unlimited_args %}',
             "'inclusion_unlimited_args' did not receive value\(s\) "
             "for the argument\(s\): 'one'"),

            ('{% load custom %}{% inclusion_unlimited_args_kwargs '
             '37 40|add:2 eggs="scrambled" 56 four=1|add:3 %}',
             "'inclusion_unlimited_args_kwargs' received "
             "some positional argument\(s\) after some keyword argument\(s\)"),

            ('{% load custom %}{% inclusion_unlimited_args_kwargs '
             '37 eggs="scrambled" eggs="scrambled" %}',
             "'inclusion_unlimited_args_kwargs' received multiple values "
             "for keyword argument 'eggs'"),
        ]

        for template_content, error_message_regex in tests:
            self.assert_compilation_failes(template_content, error_message_regex)

    def test_include_tag_missing_context(self):
        # The 'context' parameter must be present when takes_context is True
        self.assert_compilation_failes(
            '{% load custom %}{% inclusion_tag_without_context_parameter 123 %}',
            "'inclusion_tag_without_context_parameter' is decorated "
            "with takes_context=True so it must have a first argument of 'context'")

    def test_inclusion_tags_from_template(self):
        tests = [
            ('{% load custom %}{% inclusion_no_params_from_template %}',
             'inclusion_no_params_from_template - '
             'Expected result\n'),

            ('{% load custom %}{% inclusion_one_param_from_template 37 %}',
             'inclusion_one_param_from_template - '
             'Expected result: 37\n'),

            ('{% load custom %}{% inclusion_explicit_no_context_from_template 37 %}',
             'inclusion_explicit_no_context_from_template - '
             'Expected result: 37\n'),

            ('{% load custom %}{% inclusion_no_params_with_context_from_template %}',
             'inclusion_no_params_with_context_from_template - '
             'Expected result (context value: 42)\n'),

            ('{% load custom %}{% inclusion_params_and_context_from_template 37 %}',
             'inclusion_params_and_context_from_template - '
             'Expected result (context value: 42): 37\n'),

            ('{% load custom %}{% inclusion_two_params_from_template 37 42 %}',
             'inclusion_two_params_from_template - '
             'Expected result: 37, 42\n'),

            ('{% load custom %}{% inclusion_one_default_from_template 37 %}',
             'inclusion_one_default_from_template - '
             'Expected result: 37, hi\n'),

            ('{% load custom %}{% inclusion_one_default_from_template 37 42 %}',
             'inclusion_one_default_from_template - '
             'Expected result: 37, 42\n'),

            ('{% load custom %}{% inclusion_unlimited_args_from_template 37 %}',
             'inclusion_unlimited_args_from_template - '
             'Expected result: 37, hi\n'),

            ('{% load custom %}{% inclusion_unlimited_args_from_template 37 42 56 89 %}',
             'inclusion_unlimited_args_from_template - '
             'Expected result: 37, 42, 56, 89\n'),

            ('{% load custom %}{% inclusion_only_unlimited_args_from_template %}',
             'inclusion_only_unlimited_args_from_template - '
             'Expected result: \n'),

            ('{% load custom %}'
             '{% inclusion_only_unlimited_args_from_template 37 42 56 89 %}',
             'inclusion_only_unlimited_args_from_template - '
             'Expected result: 37, 42, 56, 89\n'),
        ]

        for template_content, expected_output in tests:
            self.assert_render(template_content, expected_output)

    def test_inclusion_tag_registration(self):
        # Test that the decorators preserve the decorated function's docstring, name and attributes.
        self.verify_tag(custom.inclusion_no_params, 'inclusion_no_params')
        self.verify_tag(custom.inclusion_one_param, 'inclusion_one_param')
        self.verify_tag(custom.inclusion_explicit_no_context, 'inclusion_explicit_no_context')
        self.verify_tag(custom.inclusion_no_params_with_context, 'inclusion_no_params_with_context')
        self.verify_tag(custom.inclusion_params_and_context, 'inclusion_params_and_context')
        self.verify_tag(custom.inclusion_two_params, 'inclusion_two_params')
        self.verify_tag(custom.inclusion_one_default, 'inclusion_one_default')
        self.verify_tag(custom.inclusion_unlimited_args, 'inclusion_unlimited_args')
        self.verify_tag(custom.inclusion_only_unlimited_args, 'inclusion_only_unlimited_args')
        self.verify_tag(custom.inclusion_tag_without_context_parameter, 'inclusion_tag_without_context_parameter')
        self.verify_tag(custom.inclusion_tag_use_l10n, 'inclusion_tag_use_l10n')
        self.verify_tag(custom.inclusion_tag_current_app, 'inclusion_tag_current_app')
        self.verify_tag(custom.inclusion_unlimited_args_kwargs, 'inclusion_unlimited_args_kwargs')

    def test_15070_current_app(self):
        """ Test that inclusion tag passes down `current_app` of context to
        the Context of the included/rendered template as well. """

        context = template.Context({})
        template_source = '{% load custom %}{% inclusion_tag_current_app %}'
        self.assert_render(template_source, 'None\n', context)

        context.current_app = 'advanced'
        self.assert_render(template_source, 'advanced\n', context)

    def test_15070_use_l10n(self):
        """
        Test that inclusion tag passes down `use_l10n` of context to the
        Context of the included/rendered template as well.
        """
        c = template.Context({})
        t = template.Template('{% load custom %}{% inclusion_tag_use_l10n %}')
        self.assertEqual(t.render(c).strip(), 'None')

        c.use_l10n = True
        self.assertEqual(t.render(c).strip(), 'True')

    def test_assignment_tags(self):
        c = template.Context({'value': 42})

        t = template.Template('{% load custom %}{% assignment_no_params as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_no_params - Expected result')

        t = template.Template('{% load custom %}{% assignment_one_param 37 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_one_param - Expected result: 37')

        t = template.Template('{% load custom %}{% assignment_explicit_no_context 37 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_explicit_no_context - Expected result: 37')

        t = template.Template('{% load custom %}{% assignment_no_params_with_context as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_no_params_with_context - Expected result (context value: 42)')

        t = template.Template('{% load custom %}{% assignment_params_and_context 37 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_params_and_context - Expected result (context value: 42): 37')

        t = template.Template('{% load custom %}{% assignment_two_params 37 42 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_two_params - Expected result: 37, 42')

        t = template.Template('{% load custom %}{% assignment_one_default 37 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_one_default - Expected result: 37, hi')

        t = template.Template('{% load custom %}{% assignment_one_default 37 two="hello" as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_one_default - Expected result: 37, hello')

        t = template.Template('{% load custom %}{% assignment_one_default one=99 two="hello" as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_one_default - Expected result: 99, hello')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_default' received unexpected keyword argument 'three'",
            template.Template, '{% load custom %}{% assignment_one_default 99 two="hello" three="foo" as var %}')

        t = template.Template('{% load custom %}{% assignment_one_default 37 42 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_one_default - Expected result: 37, 42')

        t = template.Template('{% load custom %}{% assignment_unlimited_args 37 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_unlimited_args - Expected result: 37, hi')

        t = template.Template('{% load custom %}{% assignment_unlimited_args 37 42 56 89 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_unlimited_args - Expected result: 37, 42, 56, 89')

        t = template.Template('{% load custom %}{% assignment_only_unlimited_args as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_only_unlimited_args - Expected result: ')

        t = template.Template('{% load custom %}{% assignment_only_unlimited_args 37 42 56 89 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_only_unlimited_args - Expected result: 37, 42, 56, 89')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_param' tag takes at least 2 arguments and the second last argument must be 'as'",
            template.Template, '{% load custom %}{% assignment_one_param 37 %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_param' tag takes at least 2 arguments and the second last argument must be 'as'",
            template.Template, '{% load custom %}{% assignment_one_param 37 as %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_param' tag takes at least 2 arguments and the second last argument must be 'as'",
            template.Template, '{% load custom %}{% assignment_one_param 37 ass var %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_two_params' received too many positional arguments",
            template.Template, '{% load custom %}{% assignment_two_params 37 42 56 as var %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_default' received too many positional arguments",
            template.Template, '{% load custom %}{% assignment_one_default 37 42 56 as var %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_one_default' did not receive value\(s\) for the argument\(s\): 'one'",
            template.Template, '{% load custom %}{% assignment_one_default as var %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_unlimited_args' did not receive value\(s\) for the argument\(s\): 'one'",
            template.Template, '{% load custom %}{% assignment_unlimited_args as var %}The result is: {{ var }}')

        t = template._Template(engine, '{% load custom %}{% assignment_unlimited_args_kwargs 37 40|add:2 56 eggs="scrambled" four=1|add:3 as var %}The result is: {{ var }}')
        self.assertEqual(t.render(c), 'The result is: assignment_unlimited_args_kwargs - Expected result: 37, 42, 56 / eggs=scrambled, four=4')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_unlimited_args_kwargs' received some positional argument\(s\) after some keyword argument\(s\)",
            template.Template, '{% load custom %}{% assignment_unlimited_args_kwargs 37 40|add:2 eggs="scrambled" 56 four=1|add:3 as var %}The result is: {{ var }}')

        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_unlimited_args_kwargs' received multiple values for keyword argument 'eggs'",
            template.Template, '{% load custom %}{% assignment_unlimited_args_kwargs 37 eggs="scrambled" eggs="scrambled" as var %}The result is: {{ var }}')

    def test_assignment_tag_registration(self):
        # Test that the decorators preserve the decorated function's docstring, name and attributes.
        self.verify_tag(custom.assignment_no_params, 'assignment_no_params')
        self.verify_tag(custom.assignment_one_param, 'assignment_one_param')
        self.verify_tag(custom.assignment_explicit_no_context, 'assignment_explicit_no_context')
        self.verify_tag(custom.assignment_no_params_with_context, 'assignment_no_params_with_context')
        self.verify_tag(custom.assignment_params_and_context, 'assignment_params_and_context')
        self.verify_tag(custom.assignment_one_default, 'assignment_one_default')
        self.verify_tag(custom.assignment_two_params, 'assignment_two_params')
        self.verify_tag(custom.assignment_unlimited_args, 'assignment_unlimited_args')
        self.verify_tag(custom.assignment_only_unlimited_args, 'assignment_only_unlimited_args')
        self.verify_tag(custom.assignment_unlimited_args, 'assignment_unlimited_args')
        self.verify_tag(custom.assignment_unlimited_args_kwargs, 'assignment_unlimited_args_kwargs')
        self.verify_tag(custom.assignment_tag_without_context_parameter, 'assignment_tag_without_context_parameter')

    def test_assignment_tag_missing_context(self):
        # The 'context' parameter must be present when takes_context is True
        six.assertRaisesRegex(self, template.TemplateSyntaxError,
            "'assignment_tag_without_context_parameter' is decorated with takes_context=True so it must have a first argument of 'context'",
            template.Template, '{% load custom %}{% assignment_tag_without_context_parameter 123 as var %}')
