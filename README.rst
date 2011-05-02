Abstract
========

Library for django-powered websites to implement data filtering without gore.

This library provides decorator for django views (``filter_powered``) and
small framework to create so-called FilterForm classes that declaratively
define filter specifications.

This approach is somewhat differs from one in django-admin, but it looks much
more intuitive and straightforward imho.

Main limitation of ``filter_powered``
=====================================

Views that "powered" with filter expected to return either SimpleTemplateResponse
subclass (that was introduced in Django 1.3) or *bare context dictionaries*
(to get the context and data to filter) so decorator returns the same type that
was passed into it.

Other types (``HttpResponse`` it common case) are silently ignored and
bypassed by decorator.

As mentioned above, if one want to use ``filter_powered`` decorator with older
django, he have to implement some decorator to put above that will actually
render context. It should be something like that::

    @render_to("foo/bar.html")
    def bar(request):
        some_result = do_smth(request)
        return {'result': some_result}

``render_to`` decorator implementation is trivial and therefore omitted. In such
way we can hook anything between ``render_to`` and template context and thus
isolate common context processing tasks (like filtering) and reuse them.

Requirements
============

* Django (1.3 to use SimpleTemplateResponse, but 1.2 will be also just fine,
  see above);
* `django-forms-extras <http://github.com/freevoid/django-forms-extras>`_ for
  some of builtin specifications.

TODO: Examples, more info about ``FilterForm``, ``FilterSpec`` and
``filter_powered``.


Copyright
=========
2010, Nikolay Zakharov.
