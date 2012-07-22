from django.utils.datastructures import SortedDict

__all__ = ('get_declared_fields', 'declarative_fields')


def get_declared_fields(bases, attrs, cls_filter,
        with_base_fields=True,
        extra_attr_name='base_fields'):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions
    """
    fields = [(field_name, attrs.pop(field_name))\
            for field_name, obj in attrs.items()\
                if isinstance(obj, cls_filter)]

    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in reversed(bases):
            if hasattr(base, extra_attr_name):
                fields = getattr(base, extra_attr_name).items() + fields
    else:
        for base in reversed(bases):
            if hasattr(base, 'declared_fields'):
                fields = base.declared_fields.items() + fields

    return SortedDict(fields)


def declarative_fields(cls_filter, meta_base=type, extra_attr_name='base_fields'):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs[extra_attr_name] = fields = get_declared_fields(bases, attrs, cls_filter,
                extra_attr_name=extra_attr_name)
        attrs[extra_attr_name + '_names'] = set(fields.keys())
        new_class = meta_base.__new__(cls, name, bases, attrs)
        return new_class

    return type('', (meta_base,), {'__new__': __new__})
