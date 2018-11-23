from django.contrib import admin

# Register your models here.

from .models import (
    Post, College, Ebooks, Cart,
    Bought, Like, PrivacyPolicy,
    AboutUs, TermsAndConditions,
    Faq
)


class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "updated", "timestamp"]
    list_display_links = ["updated"]
    list_editable = ["title"]
    list_filter = ["updated", "timestamp"]

    search_fields = ["title", "content"]

    class Meta:
        model = Post


admin.site.register(Post, PostModelAdmin)
admin.site.register(College)
admin.site.register(Ebooks)
admin.site.register(Bought)
admin.site.register(Cart)
admin.site.register(Like)
admin.site.register(AboutUs)
admin.site.register(TermsAndConditions)
admin.site.register(PrivacyPolicy)
admin.site.register(Faq)

