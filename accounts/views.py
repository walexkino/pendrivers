from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from posts.models import Post
from .forms import UserLoginForm, UserRegisterForm, UserForm, UserProfileForm, SubscribeForm
from .models import UserProfile, Followers, Subscribe
from .utils import SendSubscribeMail


# Create your views here.

def checkout():
    return redirect('/accounts/profile')

def subscribe(request):
    form = SubscribeForm(request.POST or None)
    if form.is_valid():
        email = request.POST['email']
        email_qs = Subscribe.objects.filter(email_id=email)
        if email_qs.exists():
            return redirect('/')
        else:
            Subscribe.objects.create(email_id=email)
            SendSubscribeMail(email)
            return redirect('/')
    else:
        context = {
            "form": form,
            "title": "Subscribe",
            "footer": True
        }
        return render(request, 'font-temp/form.html', context)

@login_required()
def register_greeting(request):
    subject = "Thanks for registering with the pendrivers"
    sender = 'timpendrivers@gmail.com'
    recipients = ['timpendrivers@gmail.com', request.user.email]
    msg = """
    Thank you for registering with The Pendrivers. You can now go to the blog and check out what our bloggers have posted in many categories.
    You can check out our college for classes, dictionary and other stuffs.
    And you can get your books from the store which you can download after paying.
    Thanks and I hoped you enjoyed your visit
    """
    send_mail(subject, msg, sender, recipients)
    return redirect('/accounts/profile')

@login_required()
def additional_data(request):
    form = UserProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('/accounts/profile')
    context = {"footer": True, "form": form, "title": "Add"}
    return render(request, "font-temp/form.html", context)


@login_required()
def edit_user(request):
    user = request.user
    user_form = UserForm(instance=user)
    ProfileInlineFormset = inlineformset_factory(User, UserProfile, fields=('social_media', 'bio', 'picture'), can_delete=False)
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated() and request.user.id == user.id:
        if request.method == 'POST':
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('/')

        return render(request, "font-temp/account_update.html", {
            # "noodle": pk,
            "link_text": mark_safe('Ready to publish your Book? <a href="/sell-ebooks">Click Here now</a>'),
            "noodle_form": user_form,
            "formset": formset,
            "footer": True
        })
    else:
        raise PermissionDenied


@login_required()
def profile_view(request):
    the_user = request.user
    following_ = the_user.amfollowing.all()
    followers_ = the_user.myfollowers.all()
    followers = [i.follower for i in followers_]
    the_list = [i.following for i in following_]
    the_posts = Post.objects.filter(user__in=the_list).order_by('-timestamp')[:3]
    my_posts = the_user.post_user.all()
    ebooks = request.user.ebooks.all()
    liked_ = request.user.likes.all()

    return render(request, 'font-temp/another-profile.html',
                  {'friendP': the_posts, 'following': the_list, 'followers': followers, 'my_posts': my_posts,
                   'ebooks': ebooks, "footer": True, "liked_": liked_})


def view_profile(request, username):
    the_user = User.objects.get(username=username)
    following_ = the_user.amfollowing.all()
    followers_ = the_user.myfollowers.all()
    followers = [i.follower for i in followers_]
    the_list = [i.following for i in following_]
    the_posts = the_user.post_user.all()
    ebooks = the_user.ebooks.all()
    liked_ = the_user.likes.all()

    return render(request, 'font-temp/show-profile.html',
                  {"user": the_user, 'my_posts': the_posts, 'following': the_list, 'followers': followers,
                   "ebooks": ebooks, "liked_": liked_, "footer": True
                   })


@login_required()
def create_follower(request, following_this):
    the_follower = request.user
    the_following = User.objects.get(username=following_this)
    Followers.objects.create(follower=the_follower, following=the_following)
    return redirect('/accounts/profile')


def unfollow(request, following_this):
    the_follower = request.user
    the_following = User.objects.get(username=following_this)
    del_obj = Followers.objects.get(follower=the_follower, following=the_following)
    del_obj.delete()
    return redirect('/accounts/profile')


def login_view(request):
    next = request.GET.get('next')
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/')

    register_form = '<p>You do not have an account? Register <a href="/register">here</a></p>'
    register_form += '<p>Forgot password? Reset <a href="/forgot-password">here</a>'

    return render(request, "font-temp/form.html",
                  {"form": form, "title": title, "footer": True, "added": register_form})


def register_view(request):
    next = request.GET.get('next') 
    title = 'Register'
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()

        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('/greet')
        # if next:
        #     return redirect(next)
        # return redirect('/accounts/profile')

    login_form = '<p>Created an account already? Log in <a href="/login">here</a>'

    context = {
        "form": form,
        "title": title,
        "added": login_form,
        "footer": True
    }
    return render(request, "font-temp/form.html", context)


def logout_view(request):
    logout(request)
    return redirect('login')
