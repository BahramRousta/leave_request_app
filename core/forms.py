from django import forms


class TimeForm(forms.Form):
    start = forms.DateTimeField(widget=forms.DateInput)
    end = forms.DateTimeField(widget=forms.DateInput)


choice = [
    ('Agree', 'agree'),
    ('DisAgree', 'disagree')
    ]


class CHOICES(forms.Form):
    choice = forms.CharField(widget=forms.RadioSelect(choices=choice))
