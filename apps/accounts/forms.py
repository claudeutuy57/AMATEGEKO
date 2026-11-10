from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name / Izina ry'iribukiro")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name / Izina ry'umuryango")
    email = forms.EmailField(required=True, label="Email Address")
    phone_number = forms.CharField(required=False, label="Phone Number (e.g. 0788123456)")
    preferred_language = forms.ChoiceField(
        choices=CustomUser.LANGUAGE_CHOICES,
        initial='rw',
        label="Preferred Language / Ururimi wifuza"
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'phone_number', 'preferred_language'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'LEARNER'
        if commit:
            user.save()
        return user


class StudentLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'national_id', 'preferred_language', 'target_exam_date', 
            'bio', 'avatar'
        ]
        widgets = {
            'target_exam_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'avatar':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control-file'})

