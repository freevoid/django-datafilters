from functools import wraps

__all__ = ('filter_powered',)


def filter_powered(filterform_cls, queryset_name='object_list', pass_params=False,
        add_count=False, aggregate_args={}, values_spec=None, deferred=None):

    def decorator(view):

        @wraps(view)
        def filter_powered_view(request, *args, **kwargs):
            output = view(request, *args, **kwargs)
            # SimpleTemplateResponse objects have context in `context_data`
            if hasattr(output, 'context_data'):
                context = output.context_data
            # Otherwise, work only with views that returns dict context
            elif isinstance(output, dict):
                context = output
            elif isinstance(output, tuple):
                context = output[1]
            else:
                return output

            queryset = context.get(queryset_name)

            filterform = filterform_cls(request.GET,
                                        runtime_context=kwargs)

            # Perform actual filtering
            queryset = filterform.filter(queryset).distinct()

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
            elif hasattr(output, 'context'):
                output.context = context
            return output

        return filter_powered_view

    return decorator
