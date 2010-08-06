from django import forms
from django.db.models import Q
from misc.forms import Form, CalendarField, DatePeriodField,\
        DatePeriodSelectField
from django.utils.translation import ugettext_lazy as _
from django.utils.copycompat import deepcopy

from misc.snippets import declarative_fields
from misc.forms import NoneBooleanField

import datetime

def filter_at_day(queryset, fieldname, time):
    one_day = datetime.timedelta(days=1)
    # Use date() to reset h/m/s
    from_day = time.date()
    to_day = (time + one_day).date()
    params = {
            fieldname + '__gte': from_day,
            fieldname + '__lt': to_day
            }
    return queryset.filter(**params)

def filter_today(queryset, fieldname):
    return filter_at_day(queryset, fieldname, time=datetime.datetime.now())

def split_by_now(queryset, fieldname, now=None):
    now = now or datetime.datetime.now()
    passed_side = queryset.filter(**{fieldname + '__lt': now})
    ongoing_side = queryset.filter(**{fieldname + '__gte': now})
    return passed_side, ongoing_side

class DummyFilterChoices:
    def __init__(self, field_name):
        self.field_name = field_name
    def get(self, x, *args, **kwargs):
        return {self.field_name: x} if x else {}

######################## BASE CLASSES #########################################

class FilterSpec(object):
    filter_choices = {}

    creation_counter = 0

    def __init__(self, field_name, filter_field=None):

        self.creation_counter = FilterSpec.creation_counter
        FilterSpec.creation_counter += 1

        self.field_name = field_name
        self.filter_choices = self.filter_choices or DummyFilterChoices(field_name=field_name)
        if filter_field is not None:
            self.filter_field = filter_field

        super(FilterSpec, self).__init__()

    def to_lookup(self, cleaned_value):
        return self.filter_choices.get(cleaned_value, {})

class FilterForm(Form):
    __metaclass__ = declarative_fields(FilterSpec, Form.__metaclass__, 'filter_specs_base')
    default_fields_args = {'required': False}

    def __init__(self, data=None, **kwargs):
        self.complex_conditions = []
        if hasattr(self, 'filter_specs') and isinstance(self.filter_specs, tuple):
            self.filter_specs = dict((fs.field_name, fs) for fs in self.filter_specs)
        else:
            self.filter_specs = deepcopy(self.filter_specs_base)

        view_kwargs = kwargs.pop('view_kwargs', {})
        super(FilterForm, self).__init__(data=data, **kwargs)
        # Generate form fields
        for name, spec in self.filter_specs.iteritems():
            field_cls, local_field_kwargs = spec.filter_field
            field_kwargs = self.default_fields_args.copy()
            field_kwargs.update(local_field_kwargs)
            if field_kwargs.has_key('view_kwargs'):
                field_kwargs['view_kwargs'] = view_kwargs
            self.fields[name] = field_cls(**field_kwargs)

        self.spec_count = len(self.filter_specs)

    def clean(self):
        data = {}
        complex_conditions = []
        for name, spec in self.filter_specs.iteritems():
            lookup_or_condition = spec.to_lookup(self.cleaned_data.get(name))
            if isinstance(lookup_or_condition, Q):
                complex_conditions.append(lookup_or_condition)
            else:
                data.update(lookup_or_condition)
        self.complex_conditions = complex_conditions
        return data

    def filter(self, queryset):
        if self.is_valid():
            return queryset.filter(*self.complex_conditions, **self.cleaned_data)
        else:
            return queryset

    def is_empty(self):
        return self.is_valid() and not self.cleaned_data and not self.complex_conditions

######################## BASIC FILTER SPECIFICATIONS ##########################

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
        self.filter_field = (CalendarField, {'initial': datetime.date.today,
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

from functools import wraps
def filter_powered(filterform_cls, queryset_name='object_list', pass_params=False,
        add_count=False, aggregate_args={}, values_spec=None, deferred=None):
    def decorator(view):
        @wraps(view)
        def filter_powered_view(request, *args, **kwargs):
            output = view(request, *args, **kwargs)
            # Work only with views that returns dict context
            if isinstance(output, dict):
                context = output
                queryset = output.get(queryset_name)
            elif isinstance(output, tuple):
                context = output[1]
                queryset = context.get(queryset_name)
            else:
                return output

            # XXX Maybe this should be eliminated (if there is no result, we want to have filterform in context?)
            #if not queryset:
            #    return output
            
            if not pass_params:
                filterform = filterform_cls(request.GET)
            else:
                filterform = filterform_cls(request.GET, view_kwargs=kwargs)

            # PERFORM SOME FILTERING.
            queryset = filterform.filter(queryset)

            if add_count:
                context[queryset_name + '_count'] = queryset.count()
            if aggregate_args:
                aggregated = queryset.aggregate(**aggregate_args)
                context.update(aggregated)
            if values_spec:
                queryset = queryset.values(*values_spec)
            if deferred is not None:
                queryset, context = deferred(queryset, context)

            context[queryset_name] = queryset
            context['filterform'] = filterform
            if isinstance(output, dict):
                output = context
            elif isinstance(output, tuple):
                output = (output[0], context)
            return output
        return filter_powered_view
    return decorator

