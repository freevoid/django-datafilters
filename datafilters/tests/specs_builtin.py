import datetime

from django.test import TestCase
from django import forms

from datafilters.filterspec import FilterSpec
from datafilters.filterform import FilterForm
from datafilters.specs import builtin


class FilterSpecTestMixin(object):

    field_name = 'foo'
    spec_cls = None

    def get_spec_args(self):
        return (self.field_name,), {}

    def get_test_patterns(self):
        return self.test_patterns

    def get_spec(self):
        args, kwargs = self.get_spec_args()
        return self.spec_cls(*args, **kwargs)

    def test_to_lookup(self):
        spec = self.get_spec()
        for value, expected_lookup in self.test_patterns:
            self.assertItemsEqual(spec.to_lookup(value), expected_lookup)

    def test_field_args_passing(self):
        '''
        Specific formfield's attributes must be passed to the underlying field.
        '''
        args, kwargs = self.get_spec_args()
        kwargs['label'] = 'Custom label'
        kwargs['widget'] = forms.Textarea
        spec = self.spec_cls(*args, **kwargs)

        class Form(FilterForm):
            my_field = spec

        f = Form()
        self.assertEqual(f['my_field'].label, 'Custom label')
        self.assertIsInstance(f['my_field'].field.widget, forms.Textarea)

    def test_verbose_name_passing(self):
        args, kwargs = self.get_spec_args()
        kwargs['label'] = 'Proper label'
        kwargs['verbose_name'] = 'Old style label'
        spec = self.spec_cls(*args, **kwargs)

        del kwargs['label']
        old_style_spec = self.spec_cls(*args, **kwargs)

        del kwargs['verbose_name']
        if len(args) == 1:
            args = args + ('Positional verbose name',)
        oldest_style_spec = self.spec_cls(*args, **kwargs)

        class Form(FilterForm):
            my_field = spec
            old_style_field = old_style_spec
            oldest_style_field = oldest_style_spec

        f = Form()
        self.assertEqual(f['my_field'].label, 'Proper label')
        self.assertEqual(f['old_style_field'].label, 'Old style label')
        self.assertEqual(f['oldest_style_field'].label, 'Positional verbose name')

    def test_empty(self):
        '''
        If field value is not provided there should be an empty lookup.
        '''
        spec = self.get_spec()
        self.assertItemsEqual(spec.to_lookup(None), {})
        self.assertItemsEqual(spec.to_lookup(''), {})

        class Form(FilterForm):
            my_field = spec

        f = Form({})
        self.assertTrue(f.is_empty())


class BoolTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.BoolFilterSpec

    test_patterns = [
        (True, {'foo': True}),
        (False, {'foo': False}),
        (None, {}),
    ]

    # skip test_empty
    test_empty = None


class ContainsTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.ContainsFilterSpec

    test_patterns = [
        ('hello', {'foo__icontains': 'hello'}),
    ]


class DateFieldTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.DateFieldFilterSpec

    def get_spec_args(self):
        return (
            (self.field_name,),
            dict(is_datetime=True,
                 base_date_fun=lambda: datetime.date(2012, 5, 14))
        )

    test_patterns = [
        ('all', {}),
        ('today', {
            'foo__gte': '2012-05-14',
            'foo__lt': '2012-05-15',
        }),
        ('this_week', {
            'foo__gte': '2012-05-07',
            'foo__lt': '2012-05-15',
        }),
        ('this_month', {
            'foo__gte': '2012-05-01',
            'foo__lt': '2012-05-15',
        }),
        ('this_year', {
            'foo__gte': '2012-01-01',
            'foo__lt': '2012-05-15',
        }),
    ]


class DatePickTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.DatePickFilterSpec

    test_patterns = [
        (datetime.date(2012, 1, 1), {
            'foo__year': 2012,
            'foo__month': 1,
            'foo__day': 1,
        }),
        (datetime.date(2012, 5, 20), {
            'foo__year': 2012,
            'foo__month': 5,
            'foo__day': 20,
        }),
    ]


class BaseFilterSpecTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = FilterSpec

    test_patterns = [
        ('', {}),
        ('x', {'foo': 'x'}),
        (100, {'foo': 100}),
        (datetime.date(2012, 1, 1), {'foo': datetime.date(2012, 1, 1)}),
    ]


class GenericTestCase(BaseFilterSpecTestCase):

    spec_cls = builtin.GenericSpec


class SelectBoolTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.SelectBoolFilterSpec

    test_patterns = [
        ('true', {'foo': True}),
        ('false', {'foo': False}),
        ('all', {}),
        ('_wrong_value', {'foo': False}),
    ]


class GreaterThanTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.GreaterThanFilterSpec

    def get_spec_args(self):
        return (self.field_name,), {'value': 10}

    test_patterns = [
        ('true', {'foo__gt': 10}),
        ('false', {'foo__lte': 10}),
        ('all', {}),
    ]


class GreaterThanZeroTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.GreaterThanZeroFilterSpec

    test_patterns = [
        ('true', {'foo__gt': 0}),
        ('false', {'foo__lte': 0}),
        ('all', {}),
    ]
