Abstract
========

Library to implement queryset filtering for django-powered websites without pain.

This library provides a way to declaratively define filter specifications in a
django-forms manner. Such forms can be used as ordinary django forms and they
also provides a method ``filter`` to perform filtering of arbitrary querysets.

This approach is somewhat differs from one in django-admin, but it looks more
intuitive and straightforward for the author.

Main features:

* forms-based declaration and usage;
* simple API;
* easy to implement and reuse abstract filter specs;
* a number of builtin specs for simple cases.

Usage
=====

To perform filtering one must define a subclass of
``datafilters.filterform.FilterForm`` (base class for filter forms).
The typical declaration consists of class attributes declaring filter
specifications, subclasses of ``datafilters.filterspec.FilterSpec``.
This tandem is very much like the ``Form`` and ``Field`` pair.
``FilterSpec`` subclass defines a corresponding form field that will be
used to render and validate a django form and it also defines a method
to get lookup conditions based on user input (``to_lookup``). There is
a bunch of builtin specs so typicaly it is not necessary to implement
your own filter specs for simple filtering.

For example purposes we will use models from django tutorial:
``Choice`` and ``Question``.

The typical filter form looks like that::

    from datafilters.filterform import FilterForm
    from datafilters.specs import GenericSpec, ContainsFilterSpec, \
        SelectBoolFilterSpec

    class ChoicesFilterForm(FilterForm):
        choice_text = ContainsFilterSpec('choice',
                                         label='Choice contains text')
        question_text = ContainsFilterSpec('poll__question',
                                           label='Question contains text')
        has_votes = GreaterThanZeroFilterSpec('votes')

Direct usage of filter form
---------------------------

Defined form can be used directly::

    from django.shortcuts import render_to_response
    from polls.models import Choice

    def choice_list(request):
        choices = Choice.objects.all()
        filterform = ChoicesFilterForm(request.GET)
        if filterform.is_valid():
            choices = filterform.filter(choices)

        return render_to_response('polls/choice_list.html',
            {
                'choices': choices,
                'filterform': filterform,
            })

``filter_powered`` decorator
----------------------------

There is a decorator to remove bottlenecks when using filtering extensively::

    from django.template.response import TemplateResponse
    from datafilters.decorators import filter_powered

    @filter_powered(ChoicesFilterForm, queryset_name='choices')
    def choice_list(request):
        choices = Choice.objects.all()
        return TemplateResponse('polls/choice_list.html',
            {'choices': choices})

View mixin
----------

If you are using django class-based views there is another option to take: a
view mixin ``FilterFormMixin``. Example::

    from django.views.generic import ListView

    class ChoiceListView(FilterFormMixin, ListView):
        model = Choice
        filter_form_cls = ChoicesFilterForm

    choice_list = ChoiceListView.as_view()

Usage in templates
------------------

In our template we can use new context variable ``filterform`` as an ordinary
django form::

    <form class="filter" method="get" action="">
        {{ filterform.as_p }}
        <input type="submit" value="Apply filter" />
    </form>

Requirements
============

* Django >= 1.3;
* `django-forms-extras <http://github.com/freevoid/django-forms-extras>`_ for
  some of builtin specifications (optional).

Copyright
=========
2010-2012, Nikolay Zakharov.
