try:
    from urllib import quote_plus  # python 2
except:
    pass

try:
    from urllib.parse import quote_plus  # python 3
except:
    pass

import cloudinary
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from itertools import chain
from operator import attrgetter
from decouple import config
import requests
import json

from comments.forms import CommentForm
from comments.models import Comment
from .forms import (
    PostForm, CollegeForm, 
    EbooksForm, ContactForm, 
    PrivacyPolicyForm, AboutUsForm, 
    TermsAndConditionsForm, FaqForm,
    CheckoutForm, ForgotPasswordForm, ResetPassword
)
from accounts.models import UserProfile
from django.contrib.auth.models import User
import string
import random
from .models import Post, College, Ebooks, Cart, Bought, Like, AboutUs, TermsAndConditions, PrivacyPolicy, Faq



def paystack_success(request):
    cart_obj = Cart.objects.filter(user=request.user)
    for obj in cart_obj:
        Bought.objects.create(user=request.user, book=obj.book)
        obj.book.sold += 1
        obj.book.owner.user.money += obj.book.price
        obj.book.owner.user.save()
        obj.book.save()
        obj.delete()
    return render(request, 'font-temp/thanks.html', {"footer": True})

def reset_password(request, random_str):
    form = ResetPassword(request.POST or None, initial={'code': random_str})
    if form.is_valid():
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        user_profile = UserProfile.objects.filter(password_code=code)
        if user_profile.exists():
            user = user_profile.first().user
            user.set_password(new_password)
            user.save()
            context = {
                "msg": "Passoword changed successfully"
            }
            return render(request, "font-temp/forgot_password.html", context)
        else:
            context = {
                "msg": "An error occurred"
            }
            return render(request, "font-temp/forgot_password.html", context)
    else:
        context = {
            "form": form,
            "title": "Submit",
            "footer": True
        }
        return render(request, "font-temp/form.html", context)



def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    if form.is_valid():
        username = request.POST.get('username')
        user_qs = User.objects.filter(username=username)
        if user_qs.exists() and user_qs.count() == 1:
            user = user_qs.first()
            random_str = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(10))
            user.user.password_code = random_str
            receiver = user.email
            user.user.save()
            subject = "Forgot password"
            message = "We have been notified that you forgot your password.\n"
            message += "The retrieve it at https://thependrivers.com/forgot/{}".format(
                random_str)
            from_user = 'timpendrivers@gmail.com'
            to = [receiver]
            send_mail(subject, message, from_user, to, fail_silently=False)
            context = {
                "msg": "The link to change your password has been sent to the email address of the user."
            }
            return render(request, "font-temp/forgot_password.html", context)
        else:
            context = {
                "msg": "A user with the username doesnt exist"
            }
            return render(request, 'font-temp/forgot_password.html', context)
    context = {
        "form": form,
        "title": "Submit",
        "footer": True
    }
    return render(request, "font-temp/form.html", context)



def ind_success(request):
    slug = request.GET.get("slug")
    book = Ebooks.objects.get(slug=slug)
    Bought.objects.create(user=request.user, book=book)
    book.sold += 1
    book.save()
    book.owner.user.money += book.price
    book.owner.user.save()
    cart_obj = Cart.objects.filter(user=request.user, book=book)
    if cart_obj.exists() and cart_obj.count() == 1:
        obj = cart_obj.first()
        obj.delete()
    return render(request, 'font-temp/thanks.html', {"footer": True})

@login_required()
def checkout_form(request):
    form = CheckoutForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data) #{'account_name': 'Favour Okedele', 'account_number': '0228668522', 'bank': '058'}
        data = {
            "type": "nuban",
            "name": form.cleaned_data.get('account_name'),
            "description": "User checking out",
            "account_number": form.cleaned_data.get('account_number'),
            "bank_code": form.cleaned_data.get('bank'),
            "currency": "NGN"
        }
        headers = {
            "Authorization": "Bearer " + config('TEST_PAYSTACK_SECRET_KEY'),
            "Content-Type": "application/json"
        }
        r = requests.post('https://api.paystack.co/transferrecipient', headers=headers, data=json.dumps(data))
        returned_data = r.json()
        send_data = {
            "source": "balance",
            "reason": "Checkout",
            "amount": request.user.user.money,
            "recipient": returned_data.get('recipient_code')
        }
        transfer = requests.post('https://api.paystack.co/transfer', headers=headers, data=json.dumps(send_data))
        # print('\n')
        # print('\n')
        # print(transfer.json())
        # header = {"Authorization": "Bearer " + config('PAYSTACK_SECRET_KEY')}
        # r = requests.post('https://api.paystack.co/transfer/disable_otp', headers=header)
        # print(r.json())
        return redirect('/')
    else:
        context = {
            "form": form,
            "footer": True,
            "title": "Checkout"
        }
        return render(request, "font-temp/form.html", context)
   


def about(request):
    about_obj = AboutUs.objects.first()
    context = {
        "obj": about_obj,
        "footer": True,
        "title": "About Us"
    }
    return render(request, 'font-temp/about.html', context)

def get_faq(request):
    faqs = Faq.objects.all()
    context = {
        "faqs": faqs,
        "footer": True
    }
    return render(request, 'font-temp/faq.html', context)

def add_faq(request):
    form = FaqForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('faq')
    context = {
        "title": "FAQ",
        "form": form,
        "footer": True
    }
    return render(request, "font-temp/form.html", context)

def about_edit(request):
    instance = AboutUs.objects.first()
    form = AboutUsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('about_us')
    else:
        context = {
            "title": "Update About Us",
            "form": form,
            "footer": True
        }
        return render(request, "font-temp/post_form.html", context)


def editing(request):
    return render(request, 'font-temp/editing.html', {"footer": True})


def privacy(request):
    privacy_obj = PrivacyPolicy.objects.first()
    context = {
        "obj": privacy_obj,
        "footer": True,
        "title": "Privacy Policy"
    }
    return render(request, 'font-temp/about.html', context)

def privacy_edit(request):
    instance = PrivacyPolicy.objects.first()
    form = PrivacyPolicyForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('privacy_policy')
    else:
        context = {
            "title": "Privacy Form",
            "instance": instance,
            "form": form,
            "footer": True
        }
        return render(request, "font-temp/post_form.html", context)


def terms_and_conditions(request):
    terms_obj = TermsAndConditions.objects.first()
    context = {
        "obj": terms_obj,
        "footer": True,
        "title": "Terms and Conditions"
    }
    return render(request, "font-temp/about.html", context)

def terms_and_conditions_edit(request):
    instance = TermsAndConditions.objects.first()
    form = TermsAndConditionsForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('terms')
    else:
        context = {
            "title": "Terms and Conditions Form",
            "instance": instance,
            "form": form,
            "footer": True
        }
        return render(request, "font-temp/post_form.html", context)


def publish(request):
    return render(request, 'font-temp/publish.html', {"footer": True})


def content_create(request):
    return render(request, 'font-temp/content.html', {"footer": True})


def contact_me(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        user_sender = form.cleaned_data['sender']
        sender = 'timpendrivers@gmail.com'

        recipients = ['thependrivershome@gmail.com']

        real_message = "Sender: " + user_sender + '\n' + \
            "Subject: " + subject + "\nMessage: " + message
        send_mail(subject, real_message, sender, recipients)
        return HttpResponseRedirect('/')
    context = {
        "form": form,
        "title": "Contact Us",
        "footer": True
    }
    return render(request, 'font-temp/form.html', context)

@login_required()
def post_create(request):
    articles = ['Business', 'Education', 'Family', 'Finance', 'Food', 'Health', 'Relationship', 'Spirituality',
                'Technology', 'History', 'Politics', 'Others']
    poetry = ['humour', 'tragedy', 'romance', 'nature', 'motivation', 'love']
    fiction = ['Adventure', 'Epistle', 'Humanity', 'Humour', 'Horror', 'Love', 'Mystery', 'Romance', 'Satire', 'Sci-Fi',
               'Tragedy']
    creative = ['Art', 'music', 'Photography']
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        tags = request.POST.get('tags')
        tag_list = tags.split(' ')
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        # message success
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
        "footer": True
    }
    return render(request, "font-temp/post_form.html", context)


def main_page(request):
    posts = Post.objects.all().order_by('-timestamp')[:3]
    college = College.objects.exclude(category='Dictionary').order_by('-timestamp')[:3]
    ebooks = Ebooks.objects.all().order_by('-timestamp')[:4]
    combined = sorted(chain(posts, college), key=attrgetter('timestamp'), reverse=True)[:3]
    count = range(len(ebooks))
    the_array = []
    for i in ebooks:
        the_array.append(i) 
    context = {
        "posts": combined,
        "ebooks": ebooks,
        "name": "home",
        "footer": True
    }
    return render(request, 'font-temp/index-4.html', context)

def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data,
            parent=parent_obj,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    # Comment.objects.filter_by_instance(instance)
    comments = instance.comments

    news = Post.objects.filter(category='News').order_by('-timestamp')[:3]

    if request.user.is_authenticated():
        user_likes_this = instance.liked.filter(
            user=request.user) and True or False
    else:
        user_likes_this = False

    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_string,
        "comments": comments,
        "comment_form": form,
        "news": news,
        "liked": user_likes_this,
        "footer": True
    }
    # return render(request, "single.html", context)
    return render(request, "font-temp/blog-details.html", context)


def post_filter(request, category):
    today = timezone.now().date()
    queryset_list = Post.objects.filter(
        category=category).order_by('-timestamp')

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:3]

    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
        "pages": x,
        "news": news,
        "griot": True,
        "footer": True
    }
    return render(request, "font-temp/blog.html", context)


def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.filter(
        category='Griots')  # .order_by("-timestamp")

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]
    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
        "pages": x,
        "news": news,
        "footer": True,
        "griot": True
    }
    # return render(request, "Pindex.html", context)
    return render(request, "font-temp/blog.html", context)


def news_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.filter(
        category='News')  # .order_by("-timestamp")

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:3]
    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
        "pages": x,
        "news": news,
    }
    return render(request, "font-temp/blog.html", context)


@login_required()
def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None,
                    request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved",
                         extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "font-temp/post_form.html", context)


@login_required()
def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")


@login_required()
def college_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = CollegeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        # message success
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "font-temp/post_form.html", context)

@login_required()
def college_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(College, slug=slug)
    form = CollegeForm(request.POST or None,
                    request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved",
                         extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "font-temp/post_form.html", context)


def my_back(request):
    user = request.user
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return redirect('/')

def college_detail(request, slug=None):
    instance = get_object_or_404(College, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data,
            parent=parent_obj,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    # Comment.objects.filter_by_instance(instance)
    comments = instance.comments
    news = Post.objects.filter(category='News').order_by('-timestamp')[:3]

    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_string,
        "comments": comments,
        "comment_form": form,
        "news": news,
    }
    return render(request, "font-temp/blog-details.html", context)


def all_college(request):
    queryset_list = College.objects.all()

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]

    context = {
        "object_list": queryset,
        "page_request_var": page_request_var,
        "pages": x,
        "college": "College",
        "news": news,
    }
    return render(request, "font-temp/blog.html", context)

def dictionary(request):
    print('inside dict')
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]
    queryset_list = College.objects.filter(category="Dictionary").order_by('title')
    alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page = request.GET.get("page")
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    context = {
        "object_list": queryset,
        "title": "College",
        "page_request_var": "page",
        "pages": x,
        "footer": True,
        "news": news,
        "alphabets": alphabets
    }
    return render(request, "font-temp/dictionary.html", context)

def dictionary_letter(request, letter):
    print('inside letter')
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]
    queryset_list = College.objects.filter(category="Dictionary").filter(Q(title__startswith=letter) | Q(title__startswith=letter.lower())).order_by('title')
    alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page = request.GET.get("page")
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    context = {
        "object_list": queryset,
        "title": "College",
        "page_request_var": "page",
        "pages": x,
        "footer": True,
        "news": news,
        "alphabets": alphabets
    }
    return render(request, "font-temp/dictionary.html", context)


def category_college(request, category):
    if category == "Dictionary":
        return redirect('/dictionary')
    queryset_list = College.objects.filter(category=category)
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page = request.GET.get("page")
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]

    context = {
        "object_list": queryset,
        "title": "College",
        "page_request_var": "page",
        "pages": x,
        "footer": True,
        "news": news
    }
    return render(request, "font-temp/blog.html", context)


def handle_uploaded_file(f):
    fs = FileSystemStorage()
    filename = fs.save(f.name, f)
    file_url = fs.url(filename)
    return file_url
    # with open('media/ebooks'+f.name, 'wb+') as destination:
    #     for chunks in f.chunks():
    #         destination.write(chunks)

@login_required()
def ebooks_create(request):
    form = EbooksForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        # image = cloudinary.uploader.upload(request.FILES['ebook_file'])
        # print('Ebook file', image)
        book_link = handle_uploaded_file(request.FILES['ebook_file'])
        instance = form.save(commit=False)
        instance.owner = request.user
        instance.ebook_link = book_link
        # instance.the_pdf = image['url']
        instance.save()
        # message success
        messages.success(request, "Successfully Created")
        return redirect('ebooks')
    context = {
        "form": form,
        "title": "Submit",
        "footer": True
    }
    return render(request, "font-temp/form.html", context)


def ebooks_view(request):
    ebooks = Ebooks.objects.all().order_by('-timestamp')
    query = request.GET.get("book")
    if query:
        ebooks = ebooks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query)
        ).distinct()
    context = {"ebooks": ebooks, "footer": True}
    return render(request, 'font-temp/category-grid-right.html', context)


def ebook_filter(request, filter):
    if filter == 'seller':
        ebook = Ebooks.objects.all().order_by('-sold')
    elif filter == 'featured':
        ebook = Ebooks.objects.filter(featured=True)
    elif filter == 'new':
        ebook = Ebooks.objects.all().order_by('-timestamp')
    else:
        return redirect('/ebooks')
    query = request.GET.get("book")
    if query:
        ebook = ebook.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__first_name__icontains=query) |
            Q(owner__last_name__icontains=query)
        ).distinct()
    context = {"ebooks": ebook, "footer": True}
    return render(request, 'font-temp/category-grid-right.html', context)


def ebook_detail(request, slug=None):
    instance = get_object_or_404(Ebooks, slug=slug)
    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }
    form = CommentForm(request.POST or None, initial=initial_data)
    
    if form.is_valid() and request.user.is_authenticated():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
            new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data,
            parent=parent_obj,
            )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    elif request.user.is_authenticated():
        # Comment.objects.filter_by_instance(instance)
        comments = instance.comments
        in_cart = Cart.objects.filter(book=instance, user=request.user)
        the_url = '/ind-success/?slug='+instance.slug
        if request.user.is_authenticated():
            bought_obj = Bought.objects.filter(user=request.user, book=instance)
            if bought_obj.count() > 0:
                isBought = True
            else:
                isBought = False
        else:
            isBought = False

        context = {
            "title": instance.title,
            "book": instance,
            "comments": comments,
            "comment_form": form,
            "isBought": isBought,
            "favour_url": the_url
        }
        if in_cart.count() > 0:
            context['added'] = True
        else:
            context['added'] = False
        return render(request, "font-temp/book-detail.html", context)

    else:
        return  HttpResponseRedirect('/login/')
    
    
@login_required()
def add_to_cart(request, id):
    book = Ebooks.objects.get(id=id)
    user = request.user
    obj, created = Cart.objects.get_or_create(user=user, book=book)
    cart_obj = Cart.objects.filter(user=user)
    return JsonResponse({"success": True})


@login_required()
def delete_from_cart(request, id):
    cart_obj = Cart.objects.get(id=id)
    cart_obj.delete()
    return redirect('/cart')


def topics(request):
    return render(request, 'font-temp/topics.html', {"footer": True})


def total_cat(request, category):
    categories = [
        {
            "name": "fiction",
            "sub": [{"name": "Adventure",
                     "image": 'https://images.pexels.com/photos/672358/pexels-photo-672358.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Horror",
                     "image": "https://images.pexels.com/photos/604694/pexels-photo-604694.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Romance",
                     "image": "https://images.pexels.com/photos/5390/sunset-hands-love-woman.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Epic", "image": "https://images.unsplash.com/photo-1531177071211-ed1b7991958b?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=211aa96cc231a701af846cc1c32691ee&auto=format&fit=crop&w=500&q=60"},
                    {"name": "Thriller", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1511865427000/photosp/3597edf5-01f2-486c-8243-a306bfabf8ee/stock-photo-daytime-outdoors-sky-view-from-below-people-built-structure-incidental-people-adventure-blur-3597edf5-01f2-486c-8243-a306bfabf8ee.jpg'},
                    {"name": "Humour", "image": 'https://images.pexels.com/photos/2015/man-person-woman-face.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Legend", "image": 'https://images.pexels.com/photos/64022/joan-of-arc-golden-sculpture-golden-statue-64022.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Satire", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1495245121000/photosp/83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c/stock-photo-photography-business-beauty-beautiful-local-satire-cec-standards-local-businesses-83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c.jpg'},
                    {"name": "Sci-Fi", "image": 'https://images.pexels.com/photos/745708/pexels-photo-745708.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Urban", "image": 'https://images.pexels.com/photos/373912/pexels-photo-373912.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "History", "image": 'https://images.pexels.com/photos/36006/renaissance-schallaburg-figures-facade.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Fan Fiction", "image": "https://images.pexels.com/photos/17598/pexels-photo.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                    ]
        },
        {
            "name": "poetry",
            "sub": [{"name": "Humor",
                     "image": "https://images.pexels.com/photos/2015/man-person-woman-face.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Tragedy",
                     "image": "https://images.pexels.com/photos/73821/train-wreck-steam-locomotive-locomotive-railway-73821.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Romance",
                     "image": "https://images.pexels.com/photos/5390/sunset-hands-love-woman.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Ode", "image": 'https://images.unsplash.com/photo-1505635191065-cef84508db8e?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=b9c44ea557b0a5798eb642a97119ea4d&auto=format&fit=crop&w=500&q=60'},
                    {"name": "Epic", "image": 'https://images.unsplash.com/photo-1531177071211-ed1b7991958b?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=211aa96cc231a701af846cc1c32691ee&auto=format&fit=crop&w=500&q=60'},
                    {"name": "Nolstagia", "image": 'https://res.cloudinary.com/twenty20/private_images/t_low-fit/v1528993414/photosp/287756b6-15f5-4e48-86df-49d52e80554d/287756b6-15f5-4e48-86df-49d52e80554d.jpg'},
                    {"name": "Nature", "image": 'https://images.pexels.com/photos/34950/pexels-photo.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Didactics", "image": 'http://2.bp.blogspot.com/_fh2NFxgO-vY/S-cJqY3_cWI/AAAAAAAAAAU/furjobhNUTQ/s1600/didactica.gif'},
                    {"name": "Peace", "image": 'https://images.pexels.com/photos/415380/pexels-photo-415380.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Satire", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1495245121000/photosp/83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c/stock-photo-photography-business-beauty-beautiful-local-satire-cec-standards-local-businesses-83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c.jpg'},
                    {"name": "Sexuality", "image": 'https://images.pexels.com/photos/219646/pexels-photo-219646.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                    ]
        },
        {
            "name": "articles",
            "sub": [{"name": "Business",
                     "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Education",
                     "image": "https://images.pexels.com/photos/267885/pexels-photo-267885.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Family",
                     "image": "https://images.pexels.com/photos/532508/pexels-photo-532508.jpeg?auto=compress&cs=tinysrgb&h=350"},

                    {"name": "Children", "image": 'https://images.pexels.com/photos/707193/pexels-photo-707193.jpeg?auto=compress&cs=tinysrgb&h=350'},


                    {"name": "Finance", "image": 'https://images.pexels.com/photos/53621/calculator-calculation-insurance-finance-53621.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Food", "image": 'https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Spirituality", "image": 'https://images.pexels.com/photos/267967/pexels-photo-267967.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Technology", "image": 'https://images.pexels.com/photos/373543/pexels-photo-373543.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Politics", "image": 'https://images.pexels.com/photos/4666/berlin-eu-european-union-federal-chancellery.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Religion", "image": 'https://images.pexels.com/photos/257037/pexels-photo-257037.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                    ]
        },
        {
            "name": "creative",
            "sub": [{"name": "Art",
                     "image": "https://images.pexels.com/photos/102127/pexels-photo-102127.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Music",
                     "image": "https://images.pexels.com/photos/96380/pexels-photo-96380.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Photography",
                     "image": "https://images.pexels.com/photos/212372/pexels-photo-212372.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                    ]
        }
    ]
    context = {
        "categories": categories,
        "footer": True
    }

    return render(request, 'font-temp/cat_sub.html', context)


def sub_categories(request, category):
    sub_categories_dict = {
        "Fiction": [{"name": "Adventure",
                     "image": 'https://images.pexels.com/photos/672358/pexels-photo-672358.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Horror",
                     "image": "https://images.pexels.com/photos/604694/pexels-photo-604694.jpeg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Romance",
                     "image": "https://images.pexels.com/photos/5390/sunset-hands-love-woman.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Epic", "image": "https://images.unsplash.com/photo-1531177071211-ed1b7991958b?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=211aa96cc231a701af846cc1c32691ee&auto=format&fit=crop&w=500&q=60"},
                    {"name": "Thriller", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1511865427000/photosp/3597edf5-01f2-486c-8243-a306bfabf8ee/stock-photo-daytime-outdoors-sky-view-from-below-people-built-structure-incidental-people-adventure-blur-3597edf5-01f2-486c-8243-a306bfabf8ee.jpg'},
                    {"name": "Humour", "image": 'https://images.pexels.com/photos/2015/man-person-woman-face.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Legend", "image": 'https://images.pexels.com/photos/64022/joan-of-arc-golden-sculpture-golden-statue-64022.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Satire", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1495245121000/photosp/83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c/stock-photo-photography-business-beauty-beautiful-local-satire-cec-standards-local-businesses-83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c.jpg'},
                    {"name": "Sci-Fi", "image": 'https://images.pexels.com/photos/745708/pexels-photo-745708.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Urban", "image": 'https://images.pexels.com/photos/373912/pexels-photo-373912.jpeg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "History", "image": 'https://images.pexels.com/photos/36006/renaissance-schallaburg-figures-facade.jpg?auto=compress&cs=tinysrgb&h=350'},
                    {"name": "Fan Fiction", "image": "https://images.pexels.com/photos/17598/pexels-photo.jpg?auto=compress&cs=tinysrgb&h=350"},
                    {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                    ],
        "Poetry": [{"name": "Humor",
                    "image": "https://images.pexels.com/photos/2015/man-person-woman-face.jpg?auto=compress&cs=tinysrgb&h=350"},
                   {"name": "Tragedy",
                    "image": "https://images.pexels.com/photos/73821/train-wreck-steam-locomotive-locomotive-railway-73821.jpeg?auto=compress&cs=tinysrgb&h=350"},
                   {"name": "Romance",
                    "image": "https://images.pexels.com/photos/5390/sunset-hands-love-woman.jpg?auto=compress&cs=tinysrgb&h=350"},
                   {"name": "Ode", "image": 'https://images.unsplash.com/photo-1505635191065-cef84508db8e?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=b9c44ea557b0a5798eb642a97119ea4d&auto=format&fit=crop&w=500&q=60'},
                   {"name": "Epic", "image": 'https://images.unsplash.com/photo-1531177071211-ed1b7991958b?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=211aa96cc231a701af846cc1c32691ee&auto=format&fit=crop&w=500&q=60'},
                   {"name": "Nolstagia", "image": 'https://res.cloudinary.com/twenty20/private_images/t_low-fit/v1528993414/photosp/287756b6-15f5-4e48-86df-49d52e80554d/287756b6-15f5-4e48-86df-49d52e80554d.jpg'},
                   {"name": "Nature", "image": 'https://images.pexels.com/photos/34950/pexels-photo.jpg?auto=compress&cs=tinysrgb&h=350'},
                   {"name": "Didactics", "image": 'http://2.bp.blogspot.com/_fh2NFxgO-vY/S-cJqY3_cWI/AAAAAAAAAAU/furjobhNUTQ/s1600/didactica.gif'},
                   {"name": "Peace", "image": 'https://images.pexels.com/photos/415380/pexels-photo-415380.jpeg?auto=compress&cs=tinysrgb&h=350'},
                   {"name": "Satire", "image": 'https://res.cloudinary.com/twenty20/private_images/t_watermark-criss-cross-10/v1495245121000/photosp/83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c/stock-photo-photography-business-beauty-beautiful-local-satire-cec-standards-local-businesses-83f574d5-c6b8-4b41-8d4c-b6a7c5c1117c.jpg'},
                   {"name": "Sexuality", "image": 'https://images.pexels.com/photos/219646/pexels-photo-219646.jpeg?auto=compress&cs=tinysrgb&h=350'},
                   {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                   ],
        "Articles": [{"name": "Business",
                      "image": "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&h=350"},
                     {"name": "Education",
                      "image": "https://images.pexels.com/photos/267885/pexels-photo-267885.jpeg?auto=compress&cs=tinysrgb&h=350"},
                     {"name": "Family",
                      "image": "https://images.pexels.com/photos/532508/pexels-photo-532508.jpeg?auto=compress&cs=tinysrgb&h=350"},

                     {"name": "Children", "image": 'https://images.pexels.com/photos/707193/pexels-photo-707193.jpeg?auto=compress&cs=tinysrgb&h=350'},


                     {"name": "Finance", "image": 'https://images.pexels.com/photos/53621/calculator-calculation-insurance-finance-53621.jpeg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Food", "image": 'https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Spirituality", "image": 'https://images.pexels.com/photos/267967/pexels-photo-267967.jpeg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Technology", "image": 'https://images.pexels.com/photos/373543/pexels-photo-373543.jpeg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Politics", "image": 'https://images.pexels.com/photos/4666/berlin-eu-european-union-federal-chancellery.jpg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Religion", "image": 'https://images.pexels.com/photos/257037/pexels-photo-257037.jpeg?auto=compress&cs=tinysrgb&h=350'},
                     {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                     ],
        "Creative": [{"name": "Art",
                      "image": "https://images.pexels.com/photos/102127/pexels-photo-102127.jpeg?auto=compress&cs=tinysrgb&h=350"},
                     {"name": "Music",
                      "image": "https://images.pexels.com/photos/96380/pexels-photo-96380.jpeg?auto=compress&cs=tinysrgb&h=350"},
                     {"name": "Photography",
                      "image": "https://images.pexels.com/photos/212372/pexels-photo-212372.jpeg?auto=compress&cs=tinysrgb&h=350"},
                     {"name": "Others", "image": 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg/800px-Banded_butterflyfish_Chaetodon_striatus_and_others_%284686290777%29.jpg'},
                     ]
    }
    context = {
        "sub_cat": sub_categories_dict[category],
        "footer": True,
        "category": category
    }
    return render(request, 'font-temp/sub-categories.html', context)


def get_tag(request, tag):
    queryset_list = Post.objects.filter(tags__icontains=tag)
    paginator = Paginator(queryset_list, 8)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    x = range(1, queryset.paginator.num_pages + 1)
    news = Post.objects.filter(category='News').order_by('-timestamp')[:5]

    context = {
        "object_list": queryset,
        "title": "College",
        "page_request_var": page_request_var,
        "title": "List",
        "pages": x,
        "footer": True,
        "news": news
    }
    return render(request, "font-temp/blog.html", context)


def college_topics(request):
    return render(request, 'font-temp/categoryT.html', {"footer": True})


@login_required()
def view_cart(request):
    cart_obj = Cart.objects.filter(user=request.user)
    total_price = 0
    for obj in cart_obj:
        total_price += obj.book.price
    return render(request, 'font-temp/cart.html', {"cart_obj": cart_obj, "price": total_price, "footer": True})


def like(request, post_id):
    post = Post.objects.get(id=post_id)
    new_like, created = Like.objects.get_or_create(
        user=request.user, post=post)
    if not created:
        to_delete_like = Like.objects.get(user=request.user, post=post)
        to_delete_like.delete()
        return JsonResponse({"deleted": True})
    else:
        return JsonResponse({"created": True})
