import itertools
from django import template

register = template.Library()


@register.filter
def split_in_columns(filterform, fields_per_column=None):
    '''
    Return iterator that yields a column (iterator too).

    By default, flat field list is divided in columns with
    fields_per_column elements in each (fields_per_column is a
    class attribute).
    '''
    nfields = len(filterform.fields)
    if fields_per_column is None:
        fields_per_column = filterform.fields_per_column

    ncolumns, tail = divmod(nfields, fields_per_column)
    if tail > 0:
        ncolumns += 1

    itr = iter(filterform)

    for _i in range(ncolumns):
        yield itertools.islice(itr, fields_per_column)
