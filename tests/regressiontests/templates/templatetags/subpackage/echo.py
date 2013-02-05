from __future__ import absolute_import, unicode_literals

from django import template

register = template.Library()

@register.simple_tag
def echo2(arg):
    return arg
