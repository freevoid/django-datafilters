import itertools

from django import forms
from django.utils.copycompat import deepcopy
from django.db.models import Q

from datafilters.filterspec import FilterSpec
from datafilters.declarative import declarative_fields


class FilterForm(forms.Form):

    __metaclass__ = declarative_fields(FilterSpec, forms.Form.__metaclass__,
            'filter_specs_base')

    default_fields_args = {'required': False}

    fields_per_column = 4 # for default get_columns() implementation

    def __init__(self, data=None, **kwargs):
        self.complex_conditions = []
        if hasattr(self, 'filter_specs') and isinstance(self.filter_specs, tuple):
            self.filter_specs = dict(
                    (fs.field_name, fs) for fs in self.filter_specs
                    )
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
            return queryset.filter(*self.complex_conditions,
                    **self.cleaned_data)
        else:
            return queryset

    def is_empty(self):
        return self.is_valid() and not self.cleaned_data\
                and not self.complex_conditions

    def get_columns(self):
        '''
        Returns iterator that yields a column (iterator too).
        By default, flat field list is divided in columns with
        fields_per_column elements in each (fields_per_column is a
        class attribute).

        This function can be ignored/overrided without a doubt.
        '''
        nfields = len(self.fields)
        fields_per_column = self.fields_per_column

        ncolumns, tail = divmod(nfields, fields_per_column)
        for i in range(ncolumns):
            yield itertools.islice(self, i*fields_per_column,
                    (i + 1)*fields_per_column)
        if tail:
            yield itertools.islice(self, ncolumns*fields_per_column,
                    ncolumns*fields_per_column + tail)
