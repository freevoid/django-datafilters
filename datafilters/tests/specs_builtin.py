from django.test import TestCase

from datafilters.specs import builtin


class FilterSpecTestMixin(object):

    field_name = 'foo'

    def setUp(self):
        self.spec = self.spec_cls(self.field_name)

    def test_spec(self):
        for value, expected_lookup in self.test_patterns:
            self.assertItemsEqual(self.spec.to_lookup(value), expected_lookup)


class BoolTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.BoolFilterSpec

    test_patterns = [
        (True, {'foo': True}),
        (False, {'foo': False}),
        (None, {}),
    ]


class SelectBoolTestCase(FilterSpecTestMixin, TestCase):

    spec_cls = builtin.SelectBoolFilterSpec

    test_patterns = [
        ('true', {'foo': True}),
        ('false', {'foo': False}),
        ('all', {}),
        ('', {}),
        (None, {}),
        ('_wrong_value', {'foo': False}),
    ]
