from django.conf.urls import url
from django.contrib import admin

from .views import register_contest, already_bought, register_contestant, buy_recommened_book, recom_success, submit_manuscript

urlpatterns = [
    url(r'^$', register_contestant, name='register_contestant'),
    url(r'^create/$', register_contest, name='register_contest'),
    url(r'^bought/$', recom_success, name='recom_success'),
    url(r'^thank-you/$', already_bought, name='already_bought'),
    url(r'^buy-recom/(?P<slug>[\w-]+)/$', buy_recommened_book, name='buy_recom'),
    url(r'^submit-manuscript/(?P<random_str>[\w-]+)/$', submit_manuscript, name='submit_manuscript'),
]
