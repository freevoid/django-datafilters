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
        'GreaterThanZeroFilterSpec',
        'SelectBoolFilterSpec',
        )


class GenericSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, field_cls=forms.CharField, **field_kwargs):
        field_kwargs['label'] = verbose_name
        super(GenericSpec, self).__init__(field_name,
                filter_field=(field_cls, field_kwargs))


class DateFieldFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, is_datetime=True, **field_kwargs):
        super(DateFieldFilterSpec, self).__init__(field_name)

        self.field_generic = '%s__' % self.field_name
        self.filter_choices = type('',(),{})

        def get(picked_choice, default):
            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(days=7)
            today_str = is_datetime and today.strftime('%Y-%m-%d 23:59:59') or today.strftime('%Y-%m-%d')
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
            return filter_choices.get(picked_choice, default)
        self.filter_choices.get = staticmethod(get)

        choices = (
            ('all', _('Any date')),
            ('today', _('Today')),
            ('this_week', _('Past 7 days')),
            ('this_month', _('This month')),
            ('this_year', _('This year')),
                )

        field_kwargs.update({'choices':choices,
            'label':verbose_name,
            'required': False})
        self.filter_field = (forms.ChoiceField, field_kwargs)


class DatePickFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, **field_kwargs):
        super(DatePickFilterSpec, self).__init__(field_name)
        _field_kwargs = {
            'initial': datetime.date.today,
            'label': verbose_name
        }
        _field_kwargs.update(field_kwargs)
        self.filter_field = (forms.DateField, field_kwargs)
        self.filter_choices = type('',(),{})

        def get(picked_date, default):
            if not isinstance(picked_date, datetime.date):
                return default
            return {
                        '%s__year' % field_name: str(picked_date.year),
                        '%s__month' % field_name: str(picked_date.month),
                        '%s__day' % field_name: str(picked_date.day)
                        }
        self.filter_choices.get = staticmethod(get)


class ContainsFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, **field_kwargs):
        super(ContainsFilterSpec, self).__init__(field_name)
        _field_kwargs = {'label': verbose_name, 'required': False}
        _field_kwargs.update(field_kwargs)
        self.filter_field = (forms.CharField, _field_kwargs)
        self.field_name = field_name

    def to_lookup(self, substring):
        if not substring:
            return {}
        return {'%s__icontains' % self.field_name: substring}


class BoolFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, **field_kwargs):
        super(BoolFilterSpec, self).__init__(field_name)
        _field_kwargs = {'label': verbose_name, 'required': False}
        _field_kwargs.update(field_kwargs)
        self.filter_field = (forms.BooleanField, _field_kwargs)
        self.field_name = field_name

    def to_lookup(self, checked):
        if checked is None:
            return {}
        return {self.field_name: checked}


class SelectBoolFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, revert=False, **field_kwargs):
        super(SelectBoolFilterSpec, self).__init__(field_name)
        _field_kwargs = {
            'label': verbose_name,
            'choices': (('all', _('All')),
                ('true', _('Yes')),
                ('false', _('No')))
        }
        _field_kwargs.update(field_kwargs)
        self.filter_field = (forms.ChoiceField, _field_kwargs)
        self.field_name = field_name
        self.revert = revert

    def to_lookup(self, choice):
        if choice is None or choice == 'all' or choice == '':
            return {}
        checked = True if choice == 'true' else False
        if not self.revert:
            return {self.field_name: checked}
        else:
            return {self.field_name: not checked}


class GreaterThanZeroFilterSpec(SelectBoolFilterSpec):

    def to_lookup(self, choice):
        if choice == 'true':
            checked = True
        elif choice == 'false':
            checked = False
        else:
            checked = None

        if checked is None:
            return {}
        elif checked:
            return {'%s__gt' % self.field_name: 0}
        else:
            return {self.field_name: 0}
