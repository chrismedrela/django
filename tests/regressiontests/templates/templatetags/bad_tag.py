from __future__ import absolute_import, unicode_literals

from django import template


register = template.Library()

@register.tag
def badtag(parser, token):
    raise RuntimeError("I am a bad tag")

@register.simple_tag
def badsimpletag():
    raise RuntimeError("I am a bad simpletag")
