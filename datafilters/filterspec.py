from django import forms

__all__ = (
    'FilterSpec',
    'RuntimeAwareFilterSpecMixin',
)


class FilterSpec(object):
    creation_counter = 0
    field_cls = forms.CharField

    def __init__(self, field_name, filter_field=None, **field_kwargs):

        # NOTE: Backward compatibility: previously label was provided with
        # `verbose_name` attribute
        if field_kwargs.get('label') is None:
            old_label = field_kwargs.pop('verbose_name', None)
            if old_label is not None:
                field_kwargs['label'] = old_label

        self.field_name = field_name

        if filter_field is not None:
            self.filter_field = filter_field
        else:
            base_kwargs = self.get_field_kwargs()
            base_kwargs.update(field_kwargs)
            self.filter_field = (self.get_field_cls(), base_kwargs)

        self.creation_counter = FilterSpec.creation_counter + 1
        FilterSpec.creation_counter = self.creation_counter

        super(FilterSpec, self).__init__()

    def get_field_cls(self):
        return self.field_cls

    def get_field_kwargs(self):
        return {'required': False}

    def to_lookup(self, cleaned_value):
        return {self.field_name: cleaned_value} if cleaned_value else {}


class RuntimeAwareFilterSpecMixin(object):
    '''
    Mixin class to recognize filter specs that aware of runtime context
    (accepts runtime_context in to_lookup()).
    '''
    pass
