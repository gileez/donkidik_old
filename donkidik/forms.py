from django import forms

class ProfileForm(forms.Form):
   avatar = forms.ImageField()