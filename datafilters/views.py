from django.views.generic.list import MultipleObjectMixin

__all__ = ('FilterFormMixin',)


class FilterFormMixin(MultipleObjectMixin):
    """
    Mixin that adds filtering behaviour for Class Based Views.
    Changed in a way that can play nicely with other CBV simply by overriding the get_queryset(self) and
    get_context_data(self, **kwargs) method.
    """
    filter_form_cls = None
    use_filter_chaining = False
    context_filterform_name = 'filterform'

    def get_filter(self):
        return self.filter_form_cls(self.request.GET,
                                    runtime_context=self.get_runtime_context(),
                                    use_filter_chaining=self.use_filter_chaining)

    def get_queryset(self):
        qs = super(FilterFormMixin, self).get_queryset()
        qs = self.get_filter().filter(qs).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(FilterFormMixin, self).get_context_data(**kwargs)
        context[self.context_filterform_name] = self.get_filter()
        return context

    def get_runtime_context(self):
        return {'user': self.request.user}
