from django import forms
from .models import UserProfile, Medication, Medication
        



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'] = forms.CharField(initial='admin', widget=forms.HiddenInput())

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'] = forms.CharField(initial='patient', widget=forms.HiddenInput())


# class MedicationForm(forms.ModelForm):
#     class Meta:
#         model = Medication
#         fields = ['name', 'description', 'price', 'quantity_available', 'category']

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'description', 'price', 'quantity_available', 'category', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'multiple': False})
        }


