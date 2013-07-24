from django.views.generic.list import MultipleObjectMixin

__all__ = ('FilterFormMixin',)


class FilterFormMixin(MultipleObjectMixin):
    """
    Mixin that adds filtering behaviour for Class Based Views.
    """
    filter_form_cls = None
    use_filter_chaining = False
    context_filterform_name = 'filterform'

    def get_filter(self):
        """
        Get FilterForm instance.
        """
        return self.filter_form_cls(self.request.GET,
                                    runtime_context=self.get_runtime_context(),
                                    use_filter_chaining=self.use_filter_chaining)

    def get_queryset(self):
        """
        Return queryset with filtering applied (if filter form passes
        validation).
        """
        qs = super(FilterFormMixin, self).get_queryset()
        filter_form = self.get_filter()
        if filter_form.is_valid():
            qs = filter_form.filter(qs).distinct()
        return qs

    def get_context_data(self, **kwargs):
        """
        Add filter form to the context.

        TODO: Currently we construct the filter form object twice - in
        get_queryset and here, in get_context_data. Will need to figure out a
        good way to eliminate extra initialization.
        """
        context = super(FilterFormMixin, self).get_context_data(**kwargs)
        context[self.context_filterform_name] = self.get_filter()
        return context

    def get_runtime_context(self):
        """
        Get context for filter form to allow passing runtime information,
        such as user, cookies, etc.

        Method might be overriden by implementation and context returned by
        this method will be accessible in to_lookup() method implementation
        of FilterSpec.
        """
        return {'user': self.request.user}
