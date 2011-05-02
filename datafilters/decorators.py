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

            # XXX Maybe this should be eliminated (if there is no result,
            # do we want to have filterform in context?)
            #if not queryset:
            #    return output

            if not pass_params:
                filterform = filterform_cls(request.GET)
            else:
                filterform = filterform_cls(request.GET, view_kwargs=kwargs)

            # Perform actual filtering
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
