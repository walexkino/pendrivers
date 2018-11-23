from django.contrib import admin

# Register your models here.
from .models import UserProfile, Subscribe

admin.site.register(UserProfile)
admin.site.register(Subscribe)