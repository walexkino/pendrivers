from __future__ import unicode_literals

import cloudinary
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from markdown_deux import markdown

from comments.models import Comment
from .utils import get_read_time


# Create your models here.
# MVC MODEL VIEW CONTROLLER


# Post.objects.all().published()
# Post.objects.create(user=user, title="Some time")


class PostQuerySet(models.query.QuerySet):
    def not_draft(self):
        return self.filter(draft=False)

    def published(self):
        return self.filter(publish__lte=timezone.now()).not_draft()


class PostManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return PostQuerySet(self.model, using=self._db)

    def active(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return self.get_queryset().published()


def upload_location(instance, filename):
    # filebase, extension = filename.split(".")
    # return "%s/%s.%s" %(instance.id, instance.id, extension)
    TheModel = instance.__class__
    try:
        new_id = TheModel.objects.order_by("id").last().id + 1
    except:
        new_id = 0
    return "%s/%s" % (new_id, filename)

class AboutUs(models.Model):
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return "About Us"

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

class Faq(models.Model):
    question = models.TextField(blank=False)
    answer = models.TextField(blank=False)

    def __str__(self):
        return self.question

class PrivacyPolicy(models.Model):
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Privacy Policy"
    
    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

class TermsAndConditions(models.Model):
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Terms and Conditions"

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

class Post(models.Model):
    CATEGORY_CHOICES = (
        ('News', 'News'),
        ('Fiction', 'Fiction'),
        ('Poetry', 'Poetry'),
        ('Articles', 'Articles'),
        ('Creative', 'Creative')
    )
    TAG_CHOICES = (
        ('Adventure', 'Adventure'), ('Horror', 'Horror'), ('Romance', 'Romance'), ('Epic', 'Epic'),
        ('Thriller', 'Thriller'), ('Humour', 'Humour'), ('Legend', 'Legend'), ('Satire', 'Satire'),
        ('Sci-Fi', 'Sci-Fi'), ('Urban', 'Urban'), ('History', 'History'), ('Fan Fiction', 'Fan Fiction'), ('Others', 'Others'),

        ('Humor', 'Humor'), ('Tragedy', 'Tragedy'), ('Romance', 'Romance'), ('Ode', 'Ode'),
        ('Epic', 'Epic'), ('Nolstagia', 'Nolstagia'), ('Nature', 'Nature'), ('Didactics', 'Didactics'),
        ('Peace', 'Peace'), ('Satire', 'Satire'), ('Sexuality', 'Sexuality'),

        ('Business', 'Business'), ('Education', 'Education'), ('Family', 'Family'), ('Children', 'Children'),
        ('Finance', 'Finance'), ('Food', 'Food'), ('Spirituality', 'Spirituality'), ('Technology', 'Technology'),
        ('Politics', 'Politics'), ('Religion', 'Religion'),

        ('Art', 'Art'), ('Music', 'Music'), ('Photography', 'Photography')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='post_user', default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    # image = CloudinaryField('image')
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0, null=True, blank=True)
    width_field = models.IntegerField(default=0, null=True, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Articles')
    draft = models.BooleanField(default=False)
    tags = models.CharField(max_length=120, blank=False, choices=TAG_CHOICES, default='Others')
    publish = models.DateField(auto_now=True, auto_now_add=False)
    read_time = models.TimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-timestamp", "-updated"]

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def tortoise(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Ebooks.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


'''
unique_slug_generator from Django Code Review #2 on joincfe.com/youtube/
'''


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)
        # instance.slug = unique_slug_generator(instance)

    if instance.content:
        html_string = instance.get_markdown()
        read_time_var = get_read_time(html_string)
        instance.read_time = read_time_var


def pre_save_slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = tortoise(instance)


pre_save.connect(pre_save_post_receiver, sender=Post)


# def photo_delete(sender, instance, **kwargs):
#     cloudinary.uploader.destroy(instance.image.public_id)


# pre_delete.connect(photo_delete, sender=Post)


class Ebooks(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ebooks', on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    featured = models.BooleanField(default=False)
    price = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    # ebook_file = models.CharField(upload_to='ebooks/')
    ebook_link = models.CharField(max_length=250, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    cover = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True)

    # cover = models.ImageField(upload_to=upload_location, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ebook_detail", kwargs={"slug": self.slug})

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


pre_save.connect(pre_save_slug_generator, sender=Ebooks)


# def ebook_delete(sender, instance, **kwargs):
#     cloudinary.uploader.destroy(instance.cover.public_id)


# pre_delete.connect(ebook_delete, sender=Ebooks)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE)
    book = models.ForeignKey(Ebooks, related_name='cart_book')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.book.title


class Bought(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bought', on_delete=models.CASCADE)
    book = models.ForeignKey(Ebooks, related_name='bought_books')

    def __str__(self):
        return self.book.title


class College(models.Model):
    COLLEGE_CHOICES = (
        ('Class', 'Class'),
        ('Dictionary', 'Dictionary'),
        ('Biography', 'Biography'),
        ('Guest', 'Guest Posts')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='college_user', default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    # image = CloudinaryField('image')
    image = models.ImageField(upload_to=upload_location,
                              null=True,
                              blank=True,
                              width_field="width_field",
                              height_field="height_field")
    height_field = models.IntegerField(default=0, null=True, blank=True)
    width_field = models.IntegerField(default=0, null=True, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=COLLEGE_CHOICES, default='Guest')
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=True)
    read_time = models.TimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("college_detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-timestamp", "-updated"]

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


pre_save.connect(pre_save_post_receiver, sender=College)


# def college_delete(sender, instance, **kwargs):
#     cloudinary.uploader.destroy(instance.image.public_id)


# pre_delete.connect(college_delete, sender=College)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="likes", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="liked", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' ' + self.post.title
