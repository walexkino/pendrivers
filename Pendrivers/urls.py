"""Pendrivers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from accounts.views import (login_view, register_view, logout_view, edit_user, profile_view, subscribe,
                            view_profile, create_follower, unfollow, register_greeting, additional_data)
from posts.views import (
    main_page, paystack_success, ind_success, forgot_password, reset_password,
    news_list, ebooks_create, dictionary, dictionary_letter,
    ebook_detail, ebooks_view,
    all_college, category_college,
    college_create, college_detail, college_update,
    post_filter, contact_me, about, about_edit,
    editing, publish, content_create, ebook_filter, add_to_cart,
    view_cart, delete_from_cart, topics, college_topics, privacy, privacy_edit, 
    terms_and_conditions, terms_and_conditions_edit, get_faq, add_faq, checkout_form, my_back
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^posts/', include("posts.urls", namespace='posts')),
    url(r'^favourisawesome/', my_back, name='mybak'),
    url(r'^contest/', include("contest.urls", namespace="contest")),
    url(r'^comments/', include("comments.urls", namespace='comments')),
    url(r'^paystack/', include('paystack.urls', namespace='paystack')),
    url(r'^paystack-success/', paystack_success, name="paystack_success"),
    url(r'^subscribe/', subscribe, name="subscribe"),
    url(r'^dictionaryl/(?P<letter>[\w-]+)/$', dictionary_letter, name="dictionary_letter"),
    url(r'^dictionary/', dictionary, name="dictionary"),
    url(r'^forgot-password/', forgot_password, name="forgot_password"),
    url(r'^forgot/(?P<random_str>[\w-]+)/$', reset_password, name="reset_password"),
    url(r'^ind-success/', ind_success, name="ind_success"),
    url(r'^post-filter/(?P<category>[\w-]+)/$',
        post_filter, name="post_filter"),
    url(r'^contact-us/', contact_me, name="contact_me"),
    url(r'^checkout/', checkout_form, name="checkout"),
    url(r'^about-us/edit', about_edit, name="about_us_edit"),
    url(r'^faq/add', add_faq, name="add_faq"),
    url(r'^faq/', get_faq, name="faq"),
    url(r'^about-us/', about, name="about_us"),
    url(r'^terms/edit', terms_and_conditions_edit, name="terms_edit"),
    url(r'^terms/', terms_and_conditions, name="terms"),
    url(r'^privacy/edit', privacy_edit, name="privacy_policy_edit"),
    url(r'^privacy/', privacy, name="privacy_policy"),
    url(r'^editing/', editing, name="editing"),
    url(r'^publish/', publish, name="publish"),
    url(r'^content-creation', content_create, name="content_create"),
    url(r'^login/', login_view, name='login'),
    url(r'^news/', news_list, name='news'),
    url(r'^logout/', logout_view, name='logout'),
    url(r'^register/', register_view, name='register'),
    url(r'^college-create/', college_create, name="create_college"),
    url(r'^college-detail/(?P<slug>[\w-]+)/edit$',
        college_update, name="college_update"),
    url(r'^college-detail/(?P<slug>[\w-]+)/$',
        college_detail, name="college_detail"),
    url(r'^college-category/(?P<category>[\w-]+)/$',
        category_college, name="collegeCategory"),
    url(r'^college/', college_topics, name="college"),
    url(r'^ebooks/', ebooks_view, name='ebooks'),
    url(r'^ebook-detail/(?P<slug>[\w-]+)/$',
        ebook_detail, name="ebook_detail"),
    url(r'^ebook-filter/(?P<filter>[\w-]+)/$',
        ebook_filter, name='ebook_filter'),
    url(r'^sell-ebooks/', ebooks_create, name="sell"),
    url(r'^accounts/update/$', edit_user, name='account_update'),
    url(r'^accounts/profile/$', profile_view, name='user_profile'),
    url(r'^greet/$', register_greeting, name="greet"),
    url(r'^accounts/view-profile/(?P<username>[\w-]+)/$',
        view_profile, name="view_profile"),
    url(r'^additional-data/$', additional_data, name='additional_data'),
    url(r'^accounts/follow/(?P<following_this>[\w-]+)/$',
        create_follower, name="create_follower"),
    url(r'^accounts/unfollow/(?P<following_this>[\w-]+)/$',
        unfollow, name="unfollow"),
    url(r'^add-cart/(?P<id>[\w-]+)/$', add_to_cart, name='add_cart'),
    url(r'^delete-cart/(?P<id>[\w-]+)/$',
        delete_from_cart, name='delete_cart'),
    url(r'^cart/$', view_cart, name='cart'),
    url(r'^topics/$', topics, name='topics'),
    url(r'^$', main_page, name='the_index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
