'''
Basic filterspecs that can also be used as startpoint for custom ones.
'''
import datetime

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

    def __init__(self, field_name, label=None, field_cls=None, **field_kwargs):
        if field_cls is not None:
            self.field_cls = field_cls

        # NOTE: for backward compatibility
        field_kwargs['label'] = label
        super(GenericSpec, self).__init__(field_name, **field_kwargs)


class DateFieldFilterSpec(FilterSpec):

    field_cls = forms.ChoiceField

    def __init__(self, field_name, label=None, is_datetime=True, **field_kwargs):
        field_kwargs['label'] = label
        super(DateFieldFilterSpec, self).__init__(field_name, **field_kwargs)
        self.is_datetime = is_datetime
        self.field_generic = '%s__' % self.field_name

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

        field_name = self.field_name
        today = datetime.date.today()
        one_week_ago = today - datetime.timedelta(days=7)
        today_str = (self.is_datetime and
                        today.strftime('%Y-%m-%d 23:59:59') or
                        today.strftime('%Y-%m-%d'))
        filter_choices = {
                'all': {},
                'today': {'%s__year' % field_name: str(today.year),
                        '%s__month' % field_name: str(today.month),
                        '%s__day' % field_name: str(today.day)},
                'this_week': {'%s__gte' % field_name: one_week_ago.strftime('%Y-%m-%d'),
                                '%s__lte' % field_name: today_str},
                'this_month': {'%s__year' % field_name: str(today.year),
                                '%s__month' % field_name: str(today.month)},
                'this_year': {'%s__year' % field_name: str(today.year)}
            }
        return filter_choices[picked_choice]


class DatePickFilterSpec(FilterSpec):

    field_cls = forms.DateField

    def __init__(self, field_name, label=None, **field_kwargs):
        field_kwargs['label'] = label
        super(DatePickFilterSpec, self).__init__(field_name, **field_kwargs)

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
        kwargs = super(DateFieldFilterSpec, self).get_field_kwargs()
        kwargs['initial'] = datetime.date.today
        return kwargs


class ContainsFilterSpec(FilterSpec):

    def __init__(self, field_name, label=None, **field_kwargs):
        field_kwargs['label'] = label
        super(ContainsFilterSpec, self).__init__(field_name, **field_kwargs)

    def to_lookup(self, substring):
        if not substring:
            return {}
        return {'%s__icontains' % self.field_name: substring}


class BoolFilterSpec(FilterSpec):

    def __init__(self, field_name, label=None, **field_kwargs):
        field_kwargs['label'] = label
        super(BoolFilterSpec, self).__init__(field_name, **field_kwargs)

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
        kwargs = super(DateFieldFilterSpec, self).get_field_kwargs()
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
