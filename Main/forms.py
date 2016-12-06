from django import forms

class LoginForm(forms.Form):
    username=forms.CharField(max_length=32,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'请输入您的用户名'
    }))
    password=forms.CharField(max_length=32,widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'请输入您的密码'
    }))

class RegisterForm(forms.Form):
    username=forms.CharField(max_length=32,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'请输入您的用户名'
    }))
    email=forms.EmailField(max_length=32,widget=forms.EmailInput(attrs={
        'class':'form-control',
        'placeholder':'请输入您的邮箱'
    }))
    password=forms.CharField(max_length=32,widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'请输入您的密码'
    }))
    password_confirm=forms.CharField(max_length=32,widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder':'请再次确认您的密码'
    }))

    def clean(self):
        cleaned_data=super(RegisterForm,self).clean()
        password=cleaned_data['password']
        password_confirm=cleaned_data['password_confirm']
        if password!=password_confirm:
            raise forms.ValidationError("两次输入的密码不相同")

class ChgPwdForm(forms.Form):
    old_password=forms.CharField(max_length=32,widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder':'请输入您原来的密码'
    }))
    new_password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '请输入新的密码'
    }))
    password_confirm = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '请再次确认新的密码'
    }))

    def clean(self):
        cleaned_data=super(ChgPwdForm,self).clean()
        old_password=cleaned_data['old_password']
        new_password=cleaned_data['new_password']
        password_confirm=cleaned_data['password_confirm']
        if(old_password==new_password):
            raise forms.ValidationError("新旧密码没有变化")
        if(new_password!=password_confirm):
            raise forms.ValidationError("两次新密码输入不相同")

class ChnlForm(forms.Form):
    channel=forms.CharField(max_length=64,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'请输入要添加的订阅源'
    }))
