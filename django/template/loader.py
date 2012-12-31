# Wrapper for loading templates from storage of some sort (e.g. filesystem, database).
#
# This uses the TEMPLATE_LOADERS setting, which is a list of loaders to use.
# Each loader is expected to have this interface:
#
#    callable(name, dirs=[])
#
# name is the template name.
# dirs is an optional list of directories to search instead of TEMPLATE_DIRS.
#
# The loader should return a tuple of (template_source, path). The path returned
# might be shown to the user for debugging purposes, so it should identify where
# the template was loaded from.
#
# A loader may return an already-compiled template instead of the actual
# template source. In that case the path returned should be None, since the
# path information is associated with the template during the compilation,
# which has already been done.
#
# Each loader should have an "is_usable" attribute set. This is a boolean that
# specifies whether the loader can be used in this Python installation. Each
# loader is responsible for setting this when it's initialized.
#
# For example, the eggs loader (which is capable of loading templates from
# Python eggs) sets is_usable to False if the "pkg_resources" module isn't
# installed, because pkg_resources is necessary to read eggs.

from django.core.exceptions import ImproperlyConfigured
from django.template.base import (Origin, Template, Context,
    TemplateDoesNotExist, add_to_builtins, default_engine, make_origin)
from django.utils.importlib import import_module
from django.conf import settings
from django.utils import six

class BaseLoader(object):
    is_usable = False

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, template_name, template_dirs=None):
        return self.load_template(template_name, template_dirs)

    def load_template(self, template_name, template_dirs=None):
        source, display_name = self.load_template_source(template_name, template_dirs)
        origin = make_origin(display_name, self.load_template_source, template_name, template_dirs)
        return source, display_name

    def load_template_source(self, template_name, template_dirs=None):
        """
        Returns a tuple containing the source and origin for the given template
        name.

        """
        raise NotImplementedError

    def reset(self):
        """
        Resets any state maintained by the loader instance (e.g., cached
        templates or cached loader modules).

        """
        pass


def find_template(name, dirs=None):
    return default_engine.find_template(name, dirs)

def get_template(template_name):
    """
    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    """
    template, _ = default_engine.find_template(template_name)
    return template

def get_template_from_string(source, origin=None, name=None):
    """
    Returns a compiled Template object for the given template code,
    handling template inheritance recursively.
    """
    return Template(source, origin, name)

def render_to_string(template_name, dictionary=None, context_instance=None):
    """
    Loads the given template_name and renders it with the given dictionary as
    context. The template_name may be a string to load a single template using
    get_template, or it may be a tuple to use select_template to find one of
    the templates in the list. Returns a string.
    """
    dictionary = dictionary or {}
    if isinstance(template_name, (list, tuple)):
        t = select_template(template_name)
    else:
        t = get_template(template_name)
    if not context_instance:
        return t.render(Context(dictionary))
    # Add the dictionary to the context stack, ensuring it gets removed again
    # to keep the context_instance in the same state it started in.
    context_instance.update(dictionary)
    try:
        return t.render(context_instance)
    finally:
        context_instance.pop()

def select_template(template_name_list):
    return default_engine.select_template(template_name_list)

add_to_builtins('django.template.loader_tags')
