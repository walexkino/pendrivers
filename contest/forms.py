from django import forms

from .models import Contest
from .models import Contestant

class ContestForm(forms.ModelForm):

    class Meta:
        model = Contest
        fields = ('name', 'description', 'recommeded_book')

class ContestantForm(forms.ModelForm):

    class Meta:
        model = Contestant
        exclude = ('manuscript', 'random_string', 'user', 'bought_book')

class CompleteContestantForm(forms.ModelForm):
    
    class Meta:
        model = Contestant
        fields = ('manuscript',)

