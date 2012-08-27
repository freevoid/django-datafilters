from django import forms
from django.utils.copycompat import deepcopy
from django.db.models import Q

from datafilters.filterspec import FilterSpec, RuntimeAwareFilterSpecMixin
from datafilters.declarative import declarative_fields
from datafilters.extra_lookup import Extra

__all__ = ('FilterForm', 'ChainingFilterForm', 'FilterFormBase')


def join_dicts(dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result


class FilterFormBase(forms.Form):

    __metaclass__ = declarative_fields(FilterSpec, forms.Form.__metaclass__,
                                       'filter_specs_base')

    default_fields_args = {'required': False}
    fields_per_column = 4
    use_filter_chaining = False

    def __init__(self, data=None, **kwargs):
        self.simple_lookups = []
        self.complex_conditions = []
        self.extra_conditions = Extra()

        use_filter_chaining = kwargs.pop('use_filter_chaining', None)
        if use_filter_chaining is None:
            use_filter_chaining = self.use_filter_chaining

        self.filter = self.filter_chaining \
            if use_filter_chaining else self.filter_bulk

        if hasattr(self, 'filter_specs') and isinstance(self.filter_specs, tuple):
            self.filter_specs = dict(
                    (fs.field_name, fs) for fs in self.filter_specs
                    )
        else:
            self.filter_specs = deepcopy(self.filter_specs_base)

        self.runtime_context = kwargs.pop('runtime_context', {})

        super(FilterFormBase, self).__init__(data=data, **kwargs)

        # Generate form fields
        for name, spec in self.filter_specs.iteritems():
            if isinstance(spec.filter_field, forms.Field):
                self.fields[name] = spec.filter_field
            else:
                field_cls, local_field_kwargs = spec.filter_field
                field_kwargs = self.default_fields_args.copy()
                field_kwargs.update(local_field_kwargs)
                self.fields[name] = field_cls(**field_kwargs)

        self.spec_count = len(self.filter_specs)

    def clean(self):
        '''
        Cleaning phase of `FilterForm` is aimed to collect arguments for
        filtering (lookup parameters).

        As a result we will get three new artefacts:
          * return value: a mapping to use as keyword arguments in `filter`;
          * `complex_conditions`: a `Q` object to use as a positional argument;
          * `extra_conditions`: a mapping to use as keyword arguments in
            `extra`.
        '''
        simple_lookups = []
        complex_conditions = []
        extra_conditions = []
        for name, spec in self.filter_specs.iteritems():
            raw_value = self.cleaned_data.get(name)
            if isinstance(spec, RuntimeAwareFilterSpecMixin):
                lookup_or_condition = spec.to_lookup(raw_value, runtime_context=self.runtime_context)
            else:
                lookup_or_condition = spec.to_lookup(raw_value)

            if isinstance(lookup_or_condition, Q) and lookup_or_condition:
                    complex_conditions.append(lookup_or_condition)
            elif isinstance(lookup_or_condition, Extra):
                extra_conditions.append(lookup_or_condition)
            elif lookup_or_condition:
                simple_lookups.append(lookup_or_condition)

        self.simple_lookups = simple_lookups
        self.complex_conditions = complex_conditions
        self.extra_conditions = extra_conditions

        return {}

    def get_lookup_args(self):
        '''
        Return arguments for filtering.

        :return:
            Pair of objects that can be used as `*args, **kwargs` in call to
            `QuerySet.filter` method.

        NOTE: extra conditions are not handled (so clients should use `filter`)
        '''
        if self.is_valid():
            return self.complex_conditions, join_dicts(self.simple_lookups)
        else:
            return (), {}

    def get_extra_conditions(self):
        if self.is_valid():
            return self.extra_conditions
        else:
            return None

    def is_empty(self):
        '''
        Return `True` if form is valid and contains an empty lookup.
        '''
        return (self.is_valid() and
            not self.simple_lookups and
            not self.complex_conditions and
            not self.extra_conditions)

    def filter_bulk(self, queryset):
        if self.is_valid():
            simple_lookups = self.simple_lookups
            complex_conditions = self.complex_conditions
            extra_conditions = self.get_extra_conditions()
            if extra_conditions:
                queryset = queryset.extra(**extra_conditions.as_kwargs())

            lookup = join_dicts(simple_lookups)
            return queryset.filter(*complex_conditions, **lookup)
        else:
            return queryset

    def filter_chaining(self, queryset):
        if self.is_valid():
            simple_lookups = self.simple_lookups
            complex_conditions = self.complex_conditions
            extra_conditions = self.get_extra_conditions()
            if extra_conditions:
                queryset = queryset.extra(**extra_conditions.as_kwargs())

            for lookup in simple_lookups:
                if lookup:
                    queryset = queryset.filter(**lookup)

            for query in complex_conditions:
                if query:
                    queryset = queryset.filter(query)

        return queryset


class FilterForm(FilterFormBase):

    use_filter_chaining = False


class ChainingFilterForm(FilterFormBase):

    use_filter_chaining = True
