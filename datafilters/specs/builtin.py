'''
Basic filterspecs that can also be used as startpoint for custom ones.
'''
import datetime
import warnings

from django.utils.translation import ugettext_lazy as _
from django import forms

from datafilters.filterspec import FilterSpec

__all__ = (
    'BoolFilterSpec',
    'ContainsFilterSpec',
    'DateFieldFilterSpec',
    'DatePickFilterSpec',
    'GenericSpec',
    'GreaterThanFilterSpec',
    'GreaterThanZeroFilterSpec',
    'SelectBoolFilterSpec',
)


class GenericSpec(FilterSpec):

    def __init__(self, *args, **kwargs):
        warnings.warn(
            'GenericSpec is deprecated. Use datafilters.filterspec.FilterSpec',
            DeprecationWarning)
        super(GenericSpec, self).__init__(*args, **kwargs)


class DateFieldFilterSpec(FilterSpec):

    field_cls = forms.ChoiceField

    def __init__(self, field_name, label=None, is_datetime=True,
            base_date_fun=datetime.date.today, **field_kwargs):

        field_kwargs['label'] = label
        super(DateFieldFilterSpec, self).__init__(field_name, **field_kwargs)
        self.is_datetime = is_datetime
        self.base_date_fun = base_date_fun
        self.lookup_kwarg_since = '%s__gte' % self.field_name
        self.lookup_kwarg_until = '%s__lt' % self.field_name

        self.filter_choices = {
            'all': lambda today, tomorrow: {},
            'today': lambda today, tomorrow: {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(tomorrow),
            },
            'this_week': lambda today, tomorrow: {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=7)),
                self.lookup_kwarg_until: str(tomorrow),
            },
            'this_month': lambda today, tomorrow: {
                self.lookup_kwarg_since: str(today.replace(day=1)),
                self.lookup_kwarg_until: str(tomorrow),
            },
            'this_year': lambda today, tomorrow: {
                self.lookup_kwarg_since: str(today.replace(month=1, day=1)),
                self.lookup_kwarg_until: str(tomorrow),
            },
        }

    def get_field_kwargs(self):
        kwargs = super(DateFieldFilterSpec, self).get_field_kwargs()
        kwargs['choices'] = (
            ('all', _('Any date')),
            ('today', _('Today')),
            ('this_week', _('Past 7 days')),
            ('this_month', _('This month')),
            ('this_year', _('This year')),
        )
        return kwargs

    def to_lookup(self, picked_choice):
        if not picked_choice:
            return {}

        today = self.base_date_fun()
        tomorrow = today + datetime.timedelta(days=1)

        return self.filter_choices[picked_choice](today, tomorrow)


class DatePickFilterSpec(FilterSpec):

    field_cls = forms.DateField

    def to_lookup(self, picked_date):
        if not isinstance(picked_date, datetime.date):
            return {}

        field_name = self.field_name
        return {
            '%s__year' % field_name: str(picked_date.year),
            '%s__month' % field_name: str(picked_date.month),
            '%s__day' % field_name: str(picked_date.day)
        }

    def get_field_kwargs(self):
        kwargs = super(DatePickFilterSpec, self).get_field_kwargs()
        kwargs['initial'] = datetime.date.today
        return kwargs


class ContainsFilterSpec(FilterSpec):

    def to_lookup(self, substring):
        if not substring:
            return {}
        return {'%s__icontains' % self.field_name: substring}


class BoolFilterSpec(FilterSpec):

    def to_lookup(self, checked):
        if checked is None:
            return {}
        return {self.field_name: checked}


class SelectBoolFilterSpec(FilterSpec):

    field_cls = forms.ChoiceField

    def __init__(self, field_name, label=None, revert=False, **field_kwargs):
        field_kwargs['label'] = label
        super(SelectBoolFilterSpec, self).__init__(field_name, **field_kwargs)
        self.revert = revert

    def get_field_kwargs(self):
        kwargs = super(SelectBoolFilterSpec, self).get_field_kwargs()
        kwargs['choices'] = (
            ('all', _('All')),
            ('true', _('Yes')),
            ('false', _('No')),
        )
        return kwargs

    def to_lookup(self, choice):
        if choice is None or choice == 'all' or choice == '':
            return {}
        checked = True if choice == 'true' else False
        if not self.revert:
            return {self.field_name: checked}
        else:
            return {self.field_name: not checked}


class GreaterThanFilterSpec(SelectBoolFilterSpec):

    value = 0

    def __init__(self, *args, **kwargs):
        value = kwargs.pop('value', None)
        if value is not None:
            self.value = value
        super(GreaterThanFilterSpec, self).__init__(*args, **kwargs)

    def to_lookup(self, choice):
        if choice == 'true':
            checked = True
        elif choice == 'false':
            checked = False
        else:
            return {}

        if checked:
            return {'%s__gt' % self.field_name: self.value}
        else:
            return {'%s__lte' % self.field_name: self.value}


# For backward compatibility
GreaterThanZeroFilterSpec = GreaterThanFilterSpec
