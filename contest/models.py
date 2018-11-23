from django.db import models
from posts.models import Ebooks
from django.conf import settings
# Create your models here.

class Contest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    recommeded_book = models.ForeignKey(Ebooks, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

class Contestant(models.Model):
    CATEGORY_CHOICES = (
        ('Poetry', 'Poetry'),
        ('Short Fiction (4500 words max)', 'Short Fiction'),
        ('Creative short non fiction (4500 words max)', 'Non Fiction')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contesting', default=1)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=254)
    email = models.EmailField(max_length=254)
    country = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Poetry')
    bought_book = models.BooleanField(default=False)
    random_string = models.CharField(max_length=20, unique=True, null=True)
    manuscript = models.FileField(upload_to='manuscripts', null=True)

    def __str__(self):
        return self.name

