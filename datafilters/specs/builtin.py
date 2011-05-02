'''
Basic filterspecs that can also be used as startpoint for custom ones.
'''
import datetime

from django.utils.translation import ugettext_lazy as _
from django import forms

from datafilters.filterspec import FilterSpec

__all__ = (
        'GenericSpec',
        'DateFieldFilterSpec',
        'DatePickFilterSpec',
        'ContainsFilterSpec',
        'BoolFilterSpec',
        )


class GenericSpec(FilterSpec):
    def __init__(self, field_name, verbose_name, field_cls=forms.CharField, **field_kwargs):
        field_kwargs['label'] = verbose_name
        super(GenericSpec, self).__init__(field_name,
                filter_field=(field_cls, field_kwargs))


class DateFieldFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, is_datetime=True, **kwargs):
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
        self.filter_field = (forms.ChoiceField, {'choices':choices,
            'label':verbose_name,
            'required': False})


class DatePickFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name):
        super(DatePickFilterSpec, self).__init__(field_name)
        self.filter_field = (forms.DateField, {'initial': datetime.date.today,
            'label': verbose_name})
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
    def __init__(self, field_name, verbose_name):
        super(ContainsFilterSpec, self).__init__(field_name)
        self.filter_field = (forms.CharField, {'label': verbose_name, 'required': False})
        self.field_name = field_name

    def to_lookup(self, substring):
        if not substring:
            return {}
        return {'%s__icontains' % self.field_name: substring}


class BoolFilterSpec(FilterSpec):
    def __init__(self, field_name, verbose_name):
        super(BoolFilterSpec, self).__init__(field_name)
        self.filter_field = (forms.BooleanField, {'label': verbose_name, 'required': False})
        self.field_name = field_name
    def to_lookup(self, checked):
        if checked is None:
            return {}
        return {self.field_name: checked}
