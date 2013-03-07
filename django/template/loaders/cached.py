"""
Wrapper class that takes a list of template loaders as an argument and attempts
to load templates from them in order, caching the result.
"""

from __future__ import absolute_import, unicode_literals

import hashlib

from django.template.base import (TemplateDoesNotExist, find_template_loader,
    make_origin, Template)
from django.template.loader import BaseLoader
from django.utils.encoding import force_bytes


class Loader(BaseLoader):
    is_usable = True

    def __init__(self, loaders, *args, **kwargs):
        super(Loader, self).__init__(*args, **kwargs)
        self.template_cache = {}
        self._loaders = [find_template_loader(loader, self.engine) for loader in loaders]

    def find_template(self, name, dirs=None):
        for loader in self._loaders:
            try:
                template, display_name = loader(name, dirs)
                return (template, make_origin(display_name, loader, name, dirs))
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)

    def load_template(self, template_name, template_dirs=None):
        key = template_name
        if template_dirs:
            # If template directories were specified, use a hash to differentiate
            key = '-'.join([template_name, hashlib.sha1(force_bytes('|'.join(template_dirs))).hexdigest()])

        if key not in self.template_cache:
            template, origin = self.find_template(template_name, template_dirs)
            if not hasattr(template, 'render'):
                try:
                    template = Template(template, origin, template_name,
                                        engine=self.engine)
                except TemplateDoesNotExist:
                    # If compiling the template we found raises
                    # TemplateDoesNotExist, back off to returning the source
                    # and display name for the template we were asked to
                    # load. This allows for correct identification (later) of
                    # the actual template that does not exist.
                    return template, origin
            self.template_cache[key] = template
        return self.template_cache[key], None

    def reset(self):
        """ Empty the template cache."""
        self.template_cache.clear()
