'''
Some additional filterspecs that depends on forms_extras package (and thus
optional).
'''
import datetime

from datafilters.filterspec import FilterSpec
from forms_extras.fields import (DatePeriodSelectField, NoneBooleanField,
         DatePeriodField)

__all__ = (
        'DatePeriodFilterSpec',
        'DatePeriodSelectFilterSpec',
        'IsNullFilterSpec'
        )

class DatePeriodFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, **field_kwargs):
        super(DatePeriodFilterSpec, self).__init__(field_name)
        field_kwargs['label'] = verbose_name
        self.filter_field = (DatePeriodField, field_kwargs)

    def to_lookup(self, picked_dates):
        if not isinstance(picked_dates, dict):
            return {}

        retval = {}
        from_date = picked_dates.get('from')
        if from_date:
            retval['%s__gte' % self.field_name] = from_date

        to_date = picked_dates.get('to')
        if to_date:
            retval['%s__lt' % self.field_name] = to_date + datetime.timedelta(1)

        return retval


class DatePeriodSelectFilterSpec(FilterSpec):

    def __init__(self, field_name, verbose_name, **field_kwargs):
        super(DatePeriodSelectFilterSpec, self).__init__(field_name)
        field_kwargs['label'] = verbose_name
        self.filter_field = (DatePeriodSelectField, field_kwargs)
        self.field_name = field_name

    def to_lookup(self, picked_dates):
        if not isinstance(picked_dates, tuple):
            return {}

        retval = {}
        from_date, to_date = picked_dates
        if from_date:
            retval['%s__gte' % self.field_name] = from_date

        if to_date:
            retval['%s__lte' % self.field_name] = to_date
            #+ datetime.timedelta(1)

        return retval


class IsNullFilterSpec(FilterSpec):
    def __init__(self, field_name, verbose_name, revert=True):
        super(IsNullFilterSpec, self).__init__(field_name)
        self.filter_field = (NoneBooleanField, {'label': verbose_name, 'required': False})
        self.revert = revert
        self.lookup = '%s__isnull' % field_name

    def to_lookup(self, checked):
        if checked is None:
            return {}
        if self.revert:
            return {self.lookup: not checked}
        else:
            return {self.lookup: checked}
