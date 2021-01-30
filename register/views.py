from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin,  UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import send_mail
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, resolve_url
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy, reverse

from .forms import (
    LoginForm, UserCreateForm, ProfileForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
)
from .models import Profile
from character.models import Character

# get_user_model関数は、そのプロジェクトで使用しているUserモデルを取得します。
# つまりデフォルトのUserか、カスタムしたUserが帰ります。汎用的な処理が書けるようになります
User = get_user_model()


class Top(generic.TemplateView):
    template_name = 'register/top.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_data = {'page_title': 'ログイン'}
        context.update(context_data)
        return context


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'register/top.html'


def user_data_input(request):
    """新規ユーザー情報の入力。"""
    # フォームからの遷移や、確認画面から戻るリンクを押したときはここ。
    if request.method == 'GET':
        # セッションに入力途中のデータがあればそれを使う。
        user_form = UserCreateForm(request.session.get('user_form_data'))
        profile_form = ProfileForm(request.session.get('profile_form_data'))
    else:
        user_form = UserCreateForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # 入力後の送信ボタンでここ。セッションに入力データを格納する。
            request.session['user_form_data'] = request.POST
            request.session['profile_form_data'] = request.POST
            return redirect('register:user_data_confirm')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        "page_title": "ユーザー登録",
    }
    return render(request, 'register/user_create.html', context)


def user_data_confirm(request):
    """入力データの確認画面。"""
    # user_data_inputで入力したユーザー情報をセッションから取り出す。
    session_user_form_data = request.session.get('user_form_data')
    session_profile_form_data = request.session.get('profile_form_data')
    if session_user_form_data is None and session_profile_form_data is None:
        # セッション切れや、セッションが空でURL直接入力したら入力画面にリダイレクト。
        return redirect('register:user_create')

    context = {
        'user_form': UserCreateForm(session_user_form_data),
        'profile_form': ProfileForm(session_profile_form_data),
        "page_title": "ユーザー登録",
    }
    return render(request, 'register/user_data_confirm.html', context)


@require_POST
def user_create(request):
    """仮登録と本登録用メールの発行."""
    # user_data_inputで入力したユーザー情報をセッションから取り出す。
    # ユーザー作成後は、セッションを空にしたいのでpopメソッドで取り出す。
    session_user_form_data = request.session.pop('user_form_data', None)
    session_profile_form_data = request.session.pop('profile_form_data', None)
    if session_user_form_data is None and session_profile_form_data is None:
        # ここにはPOSTメソッドで、かつセッションに入力データがなかった場合だけ。
        # セッション切れや、不正なアクセス対策。
        return redirect('register:user_create')

    user_form = UserCreateForm(session_user_form_data)
    profile_form = ProfileForm(session_profile_form_data)
    if user_form.is_valid() and profile_form.is_valid():
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 仮登録の段階なので、is_activeをFalseにします。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = user_form.save(commit=False)
        user.is_active = False
        user.save()

        # Profileモデルの処理。↑のUserモデルと紐づけます。
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()

        # アクティベーションURLの送付
        # プロトコルやドメインを取得しています。
        # self.request.schemeでプロトコルを取得（httpsなど）
        # django.core.signing.dumpを使うことで、tokenを生成しています。
        # これはsettings.pyのSECRET_KEYの値等から生成される文字列で、
        # 第三者が推測しずらい文字列です。この文字列をもとに、本登録用のURLを作成し、そのURLをメールで伝えるという流れです。
        current_site = get_current_site(request)
        domain = current_site.domain
        context = {
            'protocol': request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        # render_to_string()はrender関数にも内部的に使われているショートカット関数
        subject = render_to_string('register/mail_template/create/subject.txt', context)
        message = render_to_string('register/mail_template/create/message.txt', context)

        # ユーザーモデルにはメールアドレスフィールドがあるため、send_mailではなく
        # 宛先不要のuser.email_userを使う
        user.email_user(subject, message,)
        return redirect('register:user_create_done')

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "page_title": "ユーザー登録",
    }
    return render(request, 'register/user_create.html', context)


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したことを表示するだけ"""
    template_name = 'register/user_create_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "ユーザー登録"
        return context


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    # getattr()はオブジェクト（クラス）を第一引数で指定して、そのフィールド（属性）を第二引数で
    # 指定してその値を得る関数。指定した属性が存在しない場合の値を第三引数で指定。
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    # generic.TemplateViewのgetメソッドをtokenが正しければ本登録してオーバーライドする。
    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        # エラーの場合はHttpResponseBadRequest()で状態コード 400を表示
        # django.core.signing.dumps(user.pk)として作成したトークンを
        # django.core.signing.loads(token)としてuserのpkに復号化する。 max_ageで有効期限の設定が可能
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れの状態でアクティベーションリンクを踏んだ際に出るエラー
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "ユーザー登録"
        return context


class OnlyYouMixin(UserPassesTestMixin):
    # クラス属性raise_exceptionは、条件を満たさない場合に403ページに移動させるかどうかのフラグです。
    # test_func というメソッドをオーバーライドして、そのメソッド内で条件分岐式を記述しておきます。
    # test_func の返り値で制限をかけるかかけないかが決まります。
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'register/user_detail.html'

    # get_context_data() をオーバーライドしてコンテキストにProfileのオブジェクトを加える
    def get_context_data(self, **kwargs):
        # 今ログインしているユーザーまたはスーパーユーザーのオブジェクトを取得
        user = self.request.user
        if user.pk == self.kwargs['pk']:
            profile = Profile.objects.get(user_id__exact=user.pk)
            character = Character.objects.get(user_id__exact=user.pk)
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["profile"] = profile
        context["character"] = character
        context["page_title"] = "アカウント情報"
        return context


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しましたと表示するだけ"""
    template_name = 'register/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ※忘れた時の処理"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "パスワード再発行"
        return context

class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ※忘れた時の処理"""
    template_name = 'register/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "パスワード再発行"
        return context


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ※忘れた時の処理"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "パスワード再発行"
        return context

class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ※忘れた時の処理"""
    template_name = 'register/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "パスワード再発行"
        return context


class EmailChange(LoginRequiredMixin, generic.FormView):
    """メールアドレスの変更"""
    template_name = 'register/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            # self.request.is_secure():リクエストがセキュアである、すなわち HTTPS を介したリクエストのときに True を返します。
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('register/mail_template/email_change/subject.txt', context)
        message = render_to_string('register/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('register:email_change_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """メールアドレスの変更メールを送ったよ"""
    template_name = 'register/email_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """リンクを踏んだ後に呼ばれるメアド変更ビュー"""
    template_name = 'register/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class PhoneChange(LoginRequiredMixin, generic.UpdateView):
    """電話番号の変更"""
    template_name = 'register/phone_change_form.html'
    model = Profile
    fields = ['name', 'phone', 'gender', 'birthday']

    def get_success_url(self):
        return reverse('register:phone_change_done')

    def get_form(self):
        form = super(PhoneChange, self).get_form()
        form.fields['phone'].label = '電話番号'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class PhoneChangeDone(LoginRequiredMixin, generic.TemplateView):
    """電話番号変更しましたと表示するだけ"""
    template_name = 'register/phone_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class NameChange(LoginRequiredMixin, generic.UpdateView):
    """ハンドルネームの変更"""
    template_name = 'register/name_change_form.html'
    model = Profile
    fields = ['name', 'phone', 'gender', 'birthday']

    def get_success_url(self):
        return reverse('register:name_change_done')

    def get_form(self):
        form = super(NameChange, self).get_form()
        form.fields['name'].label = 'ハンドルネーム'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context


class NameChangeDone(LoginRequiredMixin, generic.TemplateView):
    """ハンドルネーム変更しましたと表示するだけ"""
    template_name = 'register/name_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # 継承元のメソッドを呼び出す
        context["page_title"] = "アカウント情報"
        return context

# class UserCreate(generic.CreateView):
#    """ユーザー仮登録"""
#    template_name = 'register/user_create.html'
#    form_class = UserCreateForm

#    def form_valid(self, form):
#        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 仮登録の段階なので、is_activeをFalseにします。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
#        user = form.save(commit=False)
#        user.is_active = False
#        user.save()

        # アクティベーションURLの送付
        # プロトコルやドメインを取得しています。
        # self.request.schemeでプロトコルを取得（httpsなど）
        # django.core.signing.dumpを使うことで、tokenを生成しています。
        # これはsettings.pyのSECRET_KEYの値等から生成される文字列で、
        # 第三者が推測しずらい文字列です。この文字列をもとに、本登録用のURLを作成し、そのURLをメールで伝えるという流れです。
#        current_site = get_current_site(self.request)
#        domain = current_site.domain
#        print(user.pk)
#        context = {
#            'protocol': self.request.scheme,
#            'domain': domain,
#            'token': dumps(user.pk),
#            'user': user,
#        }

        # render_to_string()はrender関数にも内部的に使われているショートカット関数
#        subject = render_to_string('register/mail_template/create/subject.txt', context)
#        message = render_to_string('register/mail_template/create/message.txt', context)

        # ユーザーモデルにはメールアドレスフィールドがあるため、send_mailではなく
        # 宛先不要のuser.email_userを使う
#        user.email_user(subject, message)
#        return redirect('register:user_create_done')



