from __future__ import absolute_import, unicode_literals

from django.template import (VariableNode, Context, Template,
    TemplateEngineWithBuiltins)
from django.template.loader import get_template_from_string
from django.utils.unittest import TestCase
from django.test.utils import override_settings

class NodelistTest(TestCase):

    def setUp(self):
        self.engine = TemplateEngineWithBuiltins()

    def assert_one_variable_node(self, template_content):
        template = Template(template_content, engine=self.engine)
        variables = template.nodelist.get_nodes_by_type(VariableNode)
        self.assertEqual(len(variables), 1)

    def test_for(self):
        self.assert_one_variable_node('{% for i in 1 %}{{ a }}{% endfor %}')

    def test_if(self):
        self.assert_one_variable_node('{% if x %}{{ a }}{% endif %}')

    def test_ifequal(self):
        self.assert_one_variable_node('{% ifequal x y %}{{ a }}{% endifequal %}')

    def test_ifchanged(self):
        self.assert_one_variable_node('{% ifchanged x %}{{ a }}{% endifchanged %}')


class ErrorIndexTest(TestCase):
    """ Checks whether index of error is calculated correctly in template
    debugger in for loops. Refs ticket #5831."""

    @override_settings(DEBUG=True, TEMPLATE_DEBUG = True)
    def test_correct_exception_index(self):
        tests = [
            ('{% load bad_tag %}'
             '{% for i in range %}'
             '{% badsimpletag %}'
             '{% endfor %}',
             (38, 56)),

            ('{% load bad_tag %}'
             '{% for i in range %}{% for j in range %}'
             '{% badsimpletag %}'
             '{% endfor %}{% endfor %}',
             (58, 76)),

            ('{% load bad_tag %}'
             '{% for i in range %}'
             '{% badsimpletag %}'
             '{% for j in range %}Hello{% endfor %}'
             '{% endfor %}',
             (38, 56)),

            ('{% load bad_tag %}'
             '{% for i in range %}{% for j in five %}'
             '{% badsimpletag %}'
             '{% endfor %}{% endfor %}',
             (38, 57)),

            ('{% load bad_tag %}'
             '{% for j in five %}'
             '{% badsimpletag %}'
             '{% endfor %}',
             (18, 37)),
        ]
        context = Context({
            'range': range(5),
            'five': 5,
        })
        engine = TemplateEngineWithBuiltins()
        for source, expected_error_source_index in tests:
            template = Template(source, engine=engine)
            try:
                template.render(context)
            except (RuntimeError, TypeError) as e:
                error_source_index = e.django_template_source[1]
                self.assertEqual(error_source_index,
                                 expected_error_source_index)
