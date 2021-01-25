from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm,
    PasswordChangeForm,  PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Profile

User = get_user_model()


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    # placeholderにフィールドのラベルを入れる
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    """ユーザー登録用フォーム"""

    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        # cleaned_dataは、バリデート後のデータを型に応じて一定のやり方で整形して返します。
        # 例えば、EmailFieldの項目にドメインが大文字で入れたときに、常に形式にあった小文字にしてくれます。
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "name", "gender", "phone", "birthday",
        )
        widgets = {
            'birthday': forms.SelectDateWidget(years=[x for x in range(1930, int(timezone.now().year)+1)]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""
    # HTMLで表示する際にクラスを「form-control」に指定してBootstrap4に対応させます。
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class EmailChangeForm(forms.ModelForm):
    """メールアドレス変更フォーム"""

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email
