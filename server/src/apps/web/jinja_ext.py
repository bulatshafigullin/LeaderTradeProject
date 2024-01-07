import logging
import pprint

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils.encoding import force_str
from jinja2.nodes import ContextReference
from jinja2 import TemplateSyntaxError

from jinja2 import nodes
from jinja2.ext import Extension
from markupsafe import Markup

class CacheExtension(Extension):
    """
    Exactly like Django's own tag, but supports full Jinja2
    expressiveness for all arguments.

        {% cache gettimeout()*2 "foo"+options.cachename  %}
            ...
        {% endcache %}

    General Syntax:

        {% cache [expire_time] [fragment_name] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcache %}

    Available by default (does not need to be loaded).

    Partly based on the ``FragmentCacheExtension`` from the Jinja2 docs.
    """

    tags = {'cache'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        expire_time = parser.parse_expression()
        fragment_name = parser.parse_expression()
        vary_on = []

        while not parser.stream.current.test('block_end'):
            vary_on.append(parser.parse_expression())

        body = parser.parse_statements(['name:endcache'], drop_needle=True)

        return nodes.CallBlock(
            self.call_method('_cache_support',
                             [expire_time, fragment_name,
                              nodes.List(vary_on), nodes.Const(lineno)]),
            [], [], body).set_lineno(lineno)

    def _cache_support(self, expire_time, fragm_name, vary_on, lineno, caller):
        try:
            if expire_time is not None:
                expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError(
                f'"{list(self.tags)[0]}" tag got a non-integer timeout value: {expire_time!r}',
                lineno,
            )

        cache_key = make_template_fragment_key(fragm_name, vary_on)

        value = cache.get(cache_key)
        if value is None:
            value = caller()
            cache.set(cache_key, force_str(value), expire_time)
        else:
            value = force_str(value)

        return value
