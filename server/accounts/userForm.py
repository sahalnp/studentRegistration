from django import forms
from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "name",
            "description",
            "main_image",
            "price",
            "selling_price",
            "active",
        ]
