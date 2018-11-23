from django import forms
from pagedown.widgets import PagedownWidget

from .models import Post, College, Ebooks, PrivacyPolicy, TermsAndConditions, AboutUs, Faq


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "category",
            "image",
            "tags"
        ]


class AboutUsForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = AboutUs
        fields = ("content",)

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=100)

class ResetPassword(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput(), required=False)
    new_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput)

class FaqForm(forms.ModelForm):
    class Meta:
        model = Faq
        fields = ("question", "answer")


class PrivacyPolicyForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = PrivacyPolicy
        fields = ("content",)


class CheckoutForm(forms.Form):
    BANK_CHOICES = (
        ('044', 'Access Bank'), ('023', 'Citibank Nigeria'), 
        ('063', 'Diamond Bank'), ('050', 'Ecobank Nigeria'), 
        ('084', 'Enterprise Bank'), ('070', 'Fidelity Bank'), 
        ('011', 'First Bank of Nigeria'), ('214', 'First City Monument Bank'), 
        ('058', 'Guaranty Trust Bank'), ('030', 'Heritage Bank'), 
        ('082', 'Keystone Bank'), ('014', 'MainStreet Bank'), 
        ('076', 'Skye Bank'), ('221', 'Stanbic IBTC Bank'), 
        ('068', 'Standard Chartered Bank'), ('232', 'Sterling Bank'), 
        ('032', 'Union Bank of Nigeria'), ('033', 'United Bank For Africa'), 
        ('215', 'Unity Bank'), ('035', 'Wema Bank'), ('057', 'Zenith Bank')
    )
    account_name = forms.CharField()
    account_number = forms.CharField()
    bank = forms.ChoiceField(choices=BANK_CHOICES)


class TermsAndConditionsForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = TermsAndConditions
        fields = ("content",)


class ContactForm(forms.Form):
    sender = forms.EmailField(max_length=120)
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea)


class EbooksForm(forms.ModelForm):
    ebook_file = forms.FileField()
    class Meta:
        model = Ebooks
        fields = [
            "title",
            "description",
            "cover",
            # "ebook_file",
            "price",
        ]


class CollegeForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget(show_preview=False))

    class Meta:
        model = College
        fields = [
            "title",
            "content",
            "image",
            "category",
        ]
