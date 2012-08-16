from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls1/$', 'polls.views.poll_list', name='poll_list1'),
    url(r'^polls2/$', 'polls.views.class_based_poll_list', name='poll_list2'),
    url(r'^admin/', include(admin.site.urls)),
)
