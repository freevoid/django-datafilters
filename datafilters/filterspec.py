class DummyFilterChoices:

    def __init__(self, field_name):
        self.field_name = field_name

    def get(self, x, *args, **kwargs):
        return {self.field_name: x} if x else {}


class FilterSpec(object):

    filter_choices = {}

    def __init__(self, field_name, filter_field=None):
        self.field_name = field_name

        if not self.filter_choices:
            self.filter_choices = DummyFilterChoices(field_name=field_name)

        if filter_field is not None:
            self.filter_field = filter_field

        super(FilterSpec, self).__init__()

    def to_lookup(self, cleaned_value):
        return self.filter_choices.get(cleaned_value, {})
