from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/decorated/$', 'polls.views.decorated_poll_list', name='decorated'),
    url(r'^polls/classbased/$', 'polls.views.class_based_poll_list', name='class_based'),
    url(r'^polls/classbased_chaining/$', 'polls.views.class_based_chaining_poll_list', name='class_based_chaining'),
    url(r'^admin/', include(admin.site.urls)),
)
