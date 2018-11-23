from django.conf.urls import url
from django.contrib import admin

from .views import (
    post_list,
    post_create,
    post_detail,
    post_filter,
    post_update,
    post_delete,
    get_tag,
    sub_categories,
    like,
    total_cat
)

urlpatterns = [
    url(r'^$', post_list, name='list'),
    url(r'^create/$', post_create),
    url(r'^like/(?P<post_id>[\w-]+)/$', like, name='like'),
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
    url(r'^sub-category/(?P<category>[\w-]+)/$', sub_categories, name='sub_categories'),
    url(r'^tag/(?P<tag>[\w-]+)/$', get_tag, name='get_tag'),
    url(r'^(?P<slug>[\w-]+)/edit/$', post_update, name='update'),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete),
]
