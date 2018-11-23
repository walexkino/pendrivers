from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from .forms import ContestForm, ContestantForm, CompleteContestantForm
from .models import Contest, Contestant
from posts.models import Ebooks, Bought
import string
import random
import cloudinary
from django.core.mail import send_mail
from comments.forms import CommentForm
from comments.models import Comment
# Create your views here.

@login_required()
def register_contest(request):
    form = ContestForm(request.POST or None)
    if form.is_valid():
        # ebook_name = form.cleaned_data['recommeded_book']
        # ebook = Ebooks.objects.get(title=ebook_name)
        # url = ebook.get_absolute_url()
        form.save()
        return redirect('/contest')
    context = {
        "form": form,
        "footer": True,
        "title": "Create Contest"
    }
    return render(request, "font-temp/form.html", context)

def submit_manuscript(request, random_str):
    contestant = Contestant.objects.get(random_string=random_str)
    form = CompleteContestantForm(request.POST or None, request.FILES or None, instance=contestant)
    if form.is_valid():
        # the_manuscript = cloudinary.uploader.upload(request.FILES['manuscript_file'])
        # the_pdf = the_manuscript['url']
        # contestant.manuscript = the_pdf
        # contestant.save()
        form.save()
        return redirect('/')

    context = {
        "form": form,
        "footer": True,
        "title": "Submit Manuscript"
    }
    return render(request, 'font-temp/form.html', context)


def generate_email(random_string, receiver):
    subject = "Entering the contest"
    message = "Thank you for entering the contest.\n"
    message += "The url is https://localhost:8000/contest/submit-manuscript/{}".format(
        random_string)
    from_user = 'timpendrivers@gmail.com'
    to = [receiver]
    send_mail(subject, message, from_user, to, fail_silently=False)

@login_required()
def recom_success(request):
    # book_id = request.GET.get('id')
    # book = Ebooks.objects.get(id=book_id)
    contestant = Contestant.objects.get(user=request.user, bought_book=False)
    book = contestant.contest.recommeded_book
    Bought.objects.create(user=request.user, book=book)
    book.sold += 1
    book.owner.user.money += book.price
    book.owner.user.save()
    book.save()
    contestant = Contestant.objects.get(user=request.user)
    random_str = contestant.random_string
    contestant.bought_book = True
    contestant.save()
    generate_email(random_str, request.user.email)
    return render(request, 'font-temp/bought_recom.html', {"footer": True})

@login_required()
def already_bought(request):
    contestant = Contestant.objects.get(user=request.user)
    random_str = contestant.random_string
    contestant.bought_book = True
    contestant.save()
    generate_email(random_str, request.user.email)
    return render(request, 'font-temp/bought_recom.html', {"footer": True})

@login_required()
def buy_recommened_book(request, slug=None):
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

    # Comment.objects.filter_by_instance(instance)
    comments = instance.comments
    context = {
        "title": instance.title,
        "book": instance,
        "comments": comments,
        "comment_form": form,
        "price": instance.price
    }
    return render(request, "font-temp/buy_recom.html", context)

@login_required()
def register_contestant(request):
    form = ContestantForm(request.POST or None)
    if form.is_valid():
        contest_name = form.cleaned_data['contest']
        contest = Contest.objects.get(name=contest_name)
        ebook = contest.recommeded_book
        bought_obj = Bought.objects.filter(user=request.user, book=ebook)
        x = form.save(commit=False)
        x.user = request.user
        random_str = ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(10))
        x.random_string = random_str
        if bought_obj.count() > 0:
            x.bought_book = True
            x.save()
            return redirect('/contest/thank-you')
        else:
            x.save()
            return redirect('contest:buy_recom', slug=ebook.slug)

    context = {
        "form": form,
        "footer": True,
        "title": "Enter Contest"
    }
    return render(request, "font-temp/form.html", context)
