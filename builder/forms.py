from datetime import date
from django import forms
from django.contrib.auth.models import User
from builder.models import Customer, Order, Material, Manual_measurements


class DateInput(forms.DateInput):
    input_type = 'date'


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'required': True,
                'id': 'password1',
                'class': 'form-control'
            })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'required': True,
                'id': 'password2',
                'class': 'form-control'
            })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            "username": forms.TextInput(
                attrs={
                    'required': True,
                    'id': 'username',
                    'class': 'form-control',
                }),
            "first_name": forms.TextInput(
                attrs={
                    'required': True,
                    'id': 'first_name',
                    'class': 'form-control'
                }),
            "last_name": forms.TextInput(
                attrs={
                    'required': True,
                    'id': 'last_name',
                    'class': 'form-control'
                }),
            "email": forms.EmailInput(
                attrs={
                    'required': True,
                    'id': 'email',
                    'class': 'form-control'
                }),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают!')
        return cd['password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('patronymic', 'address', 'date_of_birth')
        widgets = {
            "patronymic": forms.TextInput(
                attrs={
                    'required': True,
                    'id': 'patronymic',
                    'class': 'form-control',
                }),
            "address": forms.TextInput(
                attrs={
                    'required': True,
                    'id': 'address',
                    'class': 'form-control'
                }),
            "date_of_birth": DateInput(
                attrs={
                    'required': True,
                    'id': 'date_of_birth',
                    'class': 'form-control',
                    'min': '1900-01-01',
                    'max': date.today()
                }),
        }
        exclude = ('first_name', 'last_name', 'user')


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_id', 'date']

class MaterialCreateForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'weight', 'measure', 'volume', 'length', 'width', 'height', 'category', 'price', 'image']

class MaterialUpdateForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'weight', 'measure', 'volume', 'length', 'width', 'height', 'category', 'price', 'image']


class MeasureCreateForm(forms.ModelForm):
    class Meta:
        model = Manual_measurements
        fields = ['measure']