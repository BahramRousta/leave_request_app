from django import forms
from .models import Message, Employee


class RequestLeaveForm(forms.ModelForm):
    substitute = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = Message
        fields = ['start', 'end', 'description', 'substitute']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the logged-in user from the form kwargs
        super(RequestLeaveForm, self).__init__(*args, **kwargs)

        # Exclude the logged-in user from the 'substitute' field's queryset
        self.fields['substitute'].queryset = Employee.objects.exclude(id=user.id)